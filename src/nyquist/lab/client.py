from nyquist._private.network.base import (
    _Void,
    _Endpoint,
)
from nyquist._private.network.http import _HTTPResourcer
from nyquist._private.network.ws import _WSResourcer
from nyquist.lab.descriptions import (
    aeropendulum_description,
    motor_encoder_description,
)


class System:
    """Generates an object with the complete resource tree as attributes.

    An instance from System defines a laboratory sistem completely, and allows
    the user to interact with it.

    Given an string with the name of the device to control, the library will
    load the default values for it's configuration. Said configuration can
    also be modified via keyword optional arguments.

    The last word of each URL, each resource is an :class:`_HTTPEndpoint` or
    :class:`_WSEndpoint`, that according the methods assigned to the resource,
    will have a
    :meth:`~nyquist._private.network.http._HTTPResourcer.get` and/or
    :meth:`~nyquist._private.network.http._HTTPResorcer.post` method... or
    :meth:`~nyquist._private.network.ws._WSResourcer.get` and/or
    :meth:`~nyquist._private.network.ws._WSResorcer.post` method. The latter
    ones are much faster, but require an open websockets stream.

    :param description: The system name.
    :type description: str
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
    :param http_timeout: Timeout for each HTTP request.
    :type http_timeout: float
    :param ws_timeout: Timeout for each ws request.
    :type ws_timeout: float
    :param ws_get_mode: Strategy to gather messages.
    :type ws_timeout: str. ("new" or "last").
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
        self, description,
        ip=None,
        http_resources=None,
        ws_resources=None,
        http_port=None,
        ws_port=None,
        http_timeout=None,
        ws_timeout=None,
        ws_get_mode=None,
    ):
        valid_devices = (
            "aeropendulum",
        )
        if description not in valid_devices:
            raise ValueError(
                "The device description is not valid,"
                " should be one of {}".format(valid_devices)
            )

        device_map = {
            "aeropendulum": aeropendulum_description,
            "motor-encoder": motor_encoder_description,
        }
        if ip is None:
            ip = device_map[description].address
        if http_resources is None:
            http_resources = device_map[description].http_resources
        if ws_resources is None:
            ws_resources = device_map[description].ws_resources
        if http_port is None:
            http_port = device_map[description].http_port
        if ws_port is None:
            ws_port = device_map[description].ws_port
        if http_timeout is None:
            http_timeout = device_map[description].http_timeout
        if ws_timeout is None:
            ws_timeout = device_map[description].ws_timeout
        if ws_get_mode is None:
            ws_get_mode = device_map[description].ws_get_mode

        http_resourcer = _HTTPResourcer(ip, http_port, http_timeout)
        ws_resourcer = _WSResourcer(ip, ws_port, ws_timeout, ws_get_mode)

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
