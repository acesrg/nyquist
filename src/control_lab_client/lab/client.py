from http.client import HTTPConnection as _HTTPConnection
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


class HTTPConnection:
    """A nice way to handle HTTP requests.

    :param ip: Host's IP/Domain.
    :type ip: str
    :param port: Destination port.
    :type port: int
    :param timeout: A timeout [s] for each request.
    :type timeout: float
    """
    def __init__(self, ip, port, timeout):
        self.con = _HTTPConnection(ip, port=port, timeout=timeout)

    def request(self, method, url):
        """Masks the communication with the server.
        The object has already been instanced with the host's address, port
        and timeout. Given that information and the provided URL the
        function will craft an HTTP request.

        NOTE: sending the same URL to the host without this class
        will NOT result in the same behavior.

        Why?

        Since the `remote-control lab
        <https://marcomiretti.gitlab.io/remote-control-lab/>`_
        servers do not support other methods other than GET just yet, a
        decision was taken, and that behaviour was wrapped into a customized
        URL. ALL the request going out from this function are using the verb
        GET, and passing the desired HTTP method as a query parameter
        (?verb={GET,POST}).

        The goal from this function, is to make this dirty filthy workaround
        invisible to the user, allowing it to use the
        aeropendulum API `lab API
        <https://marcomiretti.gitlab.io/remote-control-lab/openapi.html>`_
        as if it supported multiple HTTP verbs.

        :param method: HTTP verb, representing the communication method.
        :type method: str
        :param url: Destination's URL, composed with a resource and it's query.
        :type url: str
        """
        HARDCODED_SUPPORTED_METHOD = "GET"

        # decode
        parsed_url = urlparse(url)

        if (not parsed_url.path) or (parsed_url.path == "/"):
            updated_url = url
        else:
            query_elements = parse_qsl(parsed_url.query)

            # add method
            query_elements.append(('verb', method))

            # re encode
            updated_query = urlencode(query_elements)
            updated_parsed_url = parsed_url._replace(query=updated_query)
            updated_url = urlunparse(updated_parsed_url)

        self.con.request(HARDCODED_SUPPORTED_METHOD, updated_url)

    def getresponse(self):
        """Wrapper to avoid accessing "con" (as in connection) member.

        :return: The response of the last request.
        :rtype: string
        """
        return self.con.getresponse()


class Resourcer(HTTPConnection):
    """HTTPConnection intuitive wrapper. Allows the user to executing
    a request of type GET, POST, etc. with a simple function. Since
    the behaviours of said verbs are well defined, we dont have to worry
    about consulting the response, encoding our message, or anything like
    that.

    The parameters are the same as in :class:`HTTPConnection`, and are
    supercharged to it.

    :param ip: Host's IP/Domain.
    :type ip: str
    :param port: Destination port.
    :type port: int
    :param timeout: A timeout [s] for each request.
    :type timeout: float
    """

    def __init__(self, ip, port, timeout):
        super().__init__(ip, port, timeout)

    @staticmethod
    def __retval(mode, response):
        """Adjusts the return value to be more human readable.

        :return: Whatever the request response was.
        :rtype: depends on parameter: mode
        """
        if mode == "payload":
            return response.read().decode().splitlines()[0]
        elif mode == "code":
            return response.code
        else:
            return response

    def get(self, resource, retval_mode="payload"):
        """Gets the value of a resource.

        :param resource: The resource whose value we want.
        :type resource: string
        :param retval_mode: The type of return value we expect.
        :type retval_mode: string

        :return: The value of the resource.
        :rtype: depends on the resource.
        """
        METHOD = "GET"
        self.request(METHOD, resource)
        return self.__retval(retval_mode, self.getresponse())

    def post(self, resource, value, retval_mode="code"):
        """Gets the value of a resource.

        :param resource: The resource whose value we want to set.
        :type resource: string
        :param value: The resource whose value we want to set.
        :type value: depends on the resource
        :param retval_mode: The type of return value we expect.
        :type retval_mode: string

        :return: The return code.
        :rtype: int
        """
        METHOD = "POST"

        parsed_resource = urlparse(resource)

        q = urlencode([("value", value)])
        resource_with_query = parsed_resource._replace(query=q)
        unparsed_resource_with_query = urlunparse(resource_with_query)
        self.request(METHOD, unparsed_resource_with_query)

        return self.__retval(retval_mode, self.getresponse())


class Void:
    """A void class, a simple object.

    Is used to assign intermediate attributes from an URI.
    """
    pass


class Endpoint:
    """A URI endpoint.

    The goal of an entire URI, the resource. When this class is instanced, it
    will look into the resource.methods, if existent it will create attributes
    for itself, linking to :meth:`Resourcer.get` or :meth:`Resourcer.post`
    respectively.


    :param resourcer: An instance of :class:`Resourcer`.
    :type resourcer: :class:`Resourcer`
    :param resource: A description of the resource, endpoint.
    :type resource: collections.namedtuple
    """
    def __init__(self, resourcer, resource):
        self.__uri = resource.uri
        self.__docs = resource.docs
        self.__resourcer = resourcer

        setattr(self, "help", self.__help_me)

        if "GET" in resource.methods:
            setattr(self, "get", self.__get_res)
        if "POST" in resource.methods:
            setattr(self, "post", self.__post_res)

    def __get_res(self):
        return self.__resourcer.get(self.__uri)

    def __post_res(self, value):
        return self.__resourcer.post(self.__uri, value)

    def __help_me(self):
        print(self.__docs)


class SystemClient:
    """Generates an object with the complete resource tree as attributes.

    Given an IP address or Domain, and a tuple of resources, when instancing
    the class, it will walk through every resource path, creating class
    attributes and sub-attributes, matching the resources.

    The last word of each URL, each resource is an :class:`Endpoint`, that
    according the methods assigned to the resource, will have
    :meth:`Resourcer.get`, :meth:`Resorcer.post` or any HTTP verb provided
    in the resource.methods.

    :param ip: An IP address or domain.
    :type ip: str
    :param http_resources: Set of HTTP resources.
    :type http_resources: tuple
    :param ws_resources: Set of Websocket resources.
    :type ws_resources: tuple
    :param http_port: Destination HTTP port.
    :type http_resources: int
    :param ws_resources: Destination Websocket port.
    :type ws_resources: int
    :param timeout: Timeout for each request.
    :type timeout: float
    """
    @staticmethod
    def __generate_tree(obj, resourcer, iterable_path, resource):
        for subresource in iterable_path:
            if not hasattr(obj, subresource):
                if len(iterable_path) == 1:
                    setattr(obj, subresource, Endpoint(resourcer, resource))
                else:
                    setattr(obj, subresource, Void())
            iterable_path.pop(0)
            SystemClient.__generate_tree(
                getattr(obj, subresource),
                resourcer,
                iterable_path,
                resource
            )

    def __init__(
        self, ip, http_resources, ws_resources,
        http_port=80, ws_port=80, timeout=5,
    ):
        resourcer = Resourcer(ip, http_port, timeout)

        self._http_resources = http_resources

        for http_resource in self._http_resources:
            iterable_path = list(filter(None, http_resource.uri.split("/")))
            self.__generate_tree(self, resourcer, iterable_path, http_resource)
