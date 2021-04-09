from nyquist._private.network.base import (
    _Void,
    _Endpoint,
)
from nyquist._private.network.http import _HTTPResourcer
from nyquist._private.network.ws import _WSResourcer


class System:
    """Generates an object with the complete resource tree as attributes.

    An instance from System defines a laboratory sistem completely, and allows
    the user to interact with it.

    Given an IP address or Domain, and a tuple of resources (like
    :data:`~resource_descriptions.AEROPENDULUM_HTTP_RESOURCES`), when
    instancing the class, it will walk through every resource path, creating
    object attributes and sub-attributes, matching the resources.

    The last word of each URL, each resource is an :class:`_Endpoint`, that
    according the methods assigned to the resource, will have a
    :meth:`~nyquist._private.network.http._Resourcer.get` and/or
    :meth:`~nyquist._private.network.http._Resorcer.post` method.

    :param ip: An IP address or domain.
    :type ip: str
    :param http_resources: Set of HTTP resources.
    :type http_resources: tuple
    :param ws_resources: Set of Websocket resources.
    :type ws_resources: tuple
    :param http_port: Destination HTTP port.
    :type http_port: int
    :param ws_port: Destination Websocket port.
    :type ws_port: int
    :param timeout: Timeout for each request.
    :type timeout: float
    """
    @staticmethod
    def __generate_tree(obj, resourcer, iterable_path, resource):
        for subresource in iterable_path:
            if not hasattr(obj, subresource):
                if len(iterable_path) == 1:
                    setattr(obj, subresource, _Endpoint(resourcer, resource))
                else:
                    setattr(obj, subresource, _Void())
            iterable_path.pop(0)
            System.__generate_tree(
                getattr(obj, subresource),
                resourcer,
                iterable_path,
                resource
            )

    def __init__(
        self, ip, http_resources, ws_resources,
        http_port=80, ws_port=80, timeout=5,
    ):
        http_resourcer = _HTTPResourcer(ip, http_port, timeout)
        ws_resourcer = _WSResourcer(ip, ws_port, timeout)

        for http_resource in http_resources:
            iterable_path = list(filter(None, http_resource.uri.split("/")))
            self.__generate_tree(
                self,
                http_resourcer,
                iterable_path,
                http_resource
            )

        for ws_resource in ws_resources:
            iterable_path = list(filter(None, ws_resource.uri.split("/")))
            self.__generate_tree(
                self,
                ws_resourcer,
                iterable_path,
                ws_resource
            )
