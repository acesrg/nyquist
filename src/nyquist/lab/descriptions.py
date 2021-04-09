from nyquist._private.assets.resource_descriptions import (
    _AEROPENDULUM_HTTP_RESOURCES,
    _AEROPENDULUM_WS_RESOURCES,
)
from nyquist._private.network.base import _SystemDescription


aeropendulum_description = _SystemDescription(
    address="192.168.100.41",
    port=80,
    timeout=1,
    http_resources=_AEROPENDULUM_HTTP_RESOURCES,
    ws_resources=_AEROPENDULUM_WS_RESOURCES,
)
