from nyquist._private.assets.resource_descriptions import (
    _AEROPENDULUM_HTTP_RESOURCES,
    _AEROPENDULUM_WS_RESOURCES,
    _MOTOR_ENCODER_HTTP_RESOURCES,
    _MOTOR_ENCODER_WS_RESOURCES,
)
from nyquist._private.network.base import _SystemDescription


aeropendulum_description = _SystemDescription(
    address="192.168.100.41",
    http_port=80,
    ws_port=80,
    http_timeout=2,
    ws_timeout=1,
    ws_get_mode="new",
    http_resources=_AEROPENDULUM_HTTP_RESOURCES,
    ws_resources=_AEROPENDULUM_WS_RESOURCES,
)

motor_encoder_description = _SystemDescription(
    address="192.168.0.50",
    http_port=80,
    ws_port=80,
    http_timeout=2,
    ws_timeout=1,
    ws_get_mode="new",
    http_resources=_MOTOR_ENCODER_HTTP_RESOURCES,
    ws_resources=_MOTOR_ENCODER_WS_RESOURCES,
)
