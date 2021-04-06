from nyquist._private.network.http import (
    _Resourcer,
    _Void,
    _Endpoint,
)


class System:
    """Generates an object with the complete resource tree as attributes.

    Given an IP address or Domain, and a tuple of resources, when instancing
    the class, it will walk through every resource path, creating class
    attributes and sub-attributes, matching the resources.

    The last word of each URL, each resource is an :class:`_Endpoint`, that
    according the methods assigned to the resource, will have
    :meth:`_Resourcer.get`, :meth:`_Resorcer.post` or any HTTP verb provided
    in the resource.methods.

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
        resourcer = _Resourcer(ip, http_port, timeout)

        self._http_resources = http_resources

        for http_resource in self._http_resources:
            iterable_path = list(filter(None, http_resource.uri.split("/")))
            self.__generate_tree(self, resourcer, iterable_path, http_resource)
