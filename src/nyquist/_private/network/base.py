from collections import namedtuple


class _Void:
    """A void class, a simple object.

    Is used to assign intermediate attributes from an URI.
    """
    pass


class _Endpoint:
    """A URI endpoint.

    The goal of an entire URI, the resource. When this class is instanced, it
    will look into the resource.methods, if existent it will create attributes
    for itself, linking to :meth:`_Resourcer.get` or :meth:`_Resourcer.post`
    respectively.


    :param resourcer: An instance of :class:`_Resourcer`.
    :type resourcer: :class:`_Resourcer`
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


_Resource = namedtuple("Resource", ["uri", "methods", "docs"])


_SystemDescription = namedtuple(
    "SystemDescription",
    [
        "address",
        "http_port",
        "ws_port",
        "http_timeout",
        "ws_timeout",
        "ws_get_mode",
        "http_resources",
        "ws_resources",
    ]
)
