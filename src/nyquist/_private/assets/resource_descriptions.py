from nyquist._private.network.base import _Resource


_AEROPENDULUM_HTTP_RESOURCES = (
    _Resource(
        uri="/logger/level",
        methods=["GET", "POST"],
        docs=(
            "The UART logging level.\n"
            "Values: 'LOG_TRACE'\n"
            "        'LOG_DEBUG'\n"
            "        'LOG_INFO'\n"
            "        'LOG_WARN'\n"
            "        'LOG_ERROR'"
        )
    ),
    _Resource(
        uri="/propeller/pwm/status",
        methods=["GET", "POST"],
        docs=(
            "The status of the propeller.\n"
            "Values: 'initialized', 'disabled'"
        )
    ),
    _Resource(
        uri="/telemetry/period",
        methods=["GET", "POST"],
        docs=(
            "The period of the websocket emmited telemetry [ms].\n"
            "Values: float from 1 to 60000"
        )
    ),
    _Resource(
        uri="/test/resource",
        methods=["GET", "POST"],
        docs=(
            "The value of a dummy resource.\n"
            "Values: string up to 16 chars."
        )
    ),
    _Resource(
        uri="/test/parent_resource",
        methods=["GET"],
        docs=(
            "The value of it's child resources, jsonized."
        )
    ),
    _Resource(
        uri="/test/parent_resource/child_a",
        methods=["GET", "POST"],
        docs=(
            "The value of a child_a resource.\n"
            "Values: string up to 16 chars."
        )
    ),
    _Resource(
        uri="/test/parent_resource/child_b",
        methods=["GET", "POST"],
        docs=(
            "The value of a child_b resource.\n"
            "Values: string up to 16 chars."
        )
    ),
)
"""
The aeropendulum system HTTP resources, containing uri path, methods, and
references for the user.
"""


_AEROPENDULUM_WS_RESOURCES = (
    _Resource(
        uri="/sensors/encoder/angle",
        methods=["GET"],
        docs=(
            """The angle (deg) of the encoder attached to the aeropendulum.

            Note: Calling get() on this attribute will trigger a websocket
            stream opening. The aeropendulum will start sending telemetry at
            a quite constant period (that can be consulted at
            ".telemetry.period.get()" or modified at ".telemetry.period.set()"
            Of course, this applies only to the first call on any of those
            methods.

            Is likely that you will receive a None the first time calling this
            method, so better call it in the after_script, so is ready in
            the control loop.
            """
        )
    ),
    _Resource(
        uri="/propeller/pwm/duty",
        methods=["POST"],
        docs=(
            """The propellers pwm duty percentage [0 to 100].

            Note: Calling post() on this attribute will trigger a websocket
            stream opening. The aeropendulum will start sending telemetry at
            a quite constant period (that can be consulted at
            ".telemetry.period.get()" or modified at ".telemetry.period.set()"
            Of course, this applies only to the first call on any of those
            methods.
            """
        )
    ),
)
"""
The aeropendulum system WS resources, containing uri path, methods, and
references for the user.
"""

_MOTOR_ENCODER_HTTP_RESOURCES = (
    _Resource(
        uri="/logger/level",
        methods=["GET", "POST"],
        docs=(
            "The UART logging level.\n"
            "Values: 'LOG_TRACE'\n"
            "        'LOG_DEBUG'\n"
            "        'LOG_INFO'\n"
            "        'LOG_WARN'\n"
            "        'LOG_ERROR'"
        )
    ),
    _Resource(
        uri="/motor/state",
        methods=["GET", "POST"],
        docs=(
            "The status of the motor.\n"
            "Values: 'STATE_ON', 'STATE_OFF'"
        )
    ),
    _Resource(
        uri="/motor/rotation",
        methods=["GET", "POST"],
        docs=(
            "The direction of the motor rotation.\n"
            "Values: 'ROTATION_CW', 'ROTATION_CCW'"
        )
    ),
    _Resource(
        uri="/encoder/value",
        methods=["POST"],
        docs=(
            "The value of encoder to set.\n"
            "Values: float"
        )
    ),
)
"""
The motor-encoder system HTTP resources, containing uri path, methods, and
references for the user.
"""


_MOTOR_ENCODER_WS_RESOURCES = (
    _Resource(
        uri="/stream/angle",
        methods=["GET"],
        docs=(
            """The angle (deg) of the encoder attached to the motor.

            Note: Calling get() on this attribute will trigger a websocket
            stream opening. The device will start sending telemetry at
            a quite constant period (that can be consulted at
            ".telemetry.period.get()" or modified at ".telemetry.period.set()"
            Of course, this applies only to the first call on any of those
            methods.

            Is likely that you will receive a None the first time calling this
            method, so better call it in the after_script, so is ready in
            the control loop.
            """
        )
    ),
    _Resource(
        uri="/steam/duty",
        methods=["POST"],
        docs=(
            """The motor pwm duty percentage [0 to 100].

            Note: Calling post() on this attribute will trigger a websocket
            stream opening. The device will start sending telemetry at
            a quite constant period (that can be consulted at
            ".telemetry.period.get()" or modified at ".telemetry.period.set()"
            Of course, this applies only to the first call on any of those
            methods.
            """
        )
    ),
)
"""
The motor-encoder system WS resources, containing uri path, methods, and
references for the user.
"""
