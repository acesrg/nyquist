from nyquist._private.network.http import _Resource


AEROPENDULUM_HTTP_RESOURCES = (
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
