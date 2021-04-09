from http.client import HTTPConnection
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


class _HTTPConnection:
    """A nice way to handle HTTP requests.

    :param ip: Host's IP/Domain.
    :type ip: str
    :param port: Destination port.
    :type port: int
    :param timeout: A timeout [s] for each request.
    :type timeout: float
    """
    def __init__(self, ip, port, timeout):
        self.con = HTTPConnection(ip, port=port, timeout=timeout)

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


class _HTTPResourcer(_HTTPConnection):
    """_HTTPConnection intuitive wrapper. Allows the user to executing
    a request of type GET, POST, etc. with a simple function. Since
    the behaviours of said verbs are well defined, we dont have to worry
    about consulting the response, encoding our message, or anything like
    that.

    The parameters are the same as in :class:`_HTTPConnection`, and are
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
    def _retval(mode, response):
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

        :param resource: The resource whose value we want. If using any
                         :class:`nyquist.lab.client.System` object, this
                         argument mustn't be passed.
        :type resource: string
        :param retval_mode: The type of return value we expect.
        :type retval_mode: string

        :return: The value of the resource.
        :rtype: depends on the resource.
        """
        METHOD = "GET"
        self.request(METHOD, resource)
        return self._retval(retval_mode, self.getresponse())

    def post(self, resource, value, retval_mode="code"):
        """Gets the value of a resource.

        :param resource: The resource whose value we want to set. If using any
                         :class:`nyquist.lab.client.System` object, this
                         argument mustn't be passed.
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

        return self._retval(retval_mode, self.getresponse())
