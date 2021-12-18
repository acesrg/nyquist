import asyncio
import json

import websockets


class _WSResourcer():
    def __init__(self, ip, port, timeout, get_mode):
        self._connected = False
        self._reconnecting = False
        self._last_ws_message = None
        self._uri = "ws://{}/stream".format(ip)
        self._port = port
        self._timeout = timeout
        self._get_mode = get_mode
        self._post_uri_resource_map = {
            "/propeller/pwm/duty": "duty",
        }
        self._get_uri_resource_map = {
            "/sensors/encoder/angle": "angle",
        }
        self.new_message = False

    def __start_telemetry(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.__gather_telemetry())

    async def __gather_telemetry(self):
        async for ws in websockets.connect(self._uri):
            try:
                self._connected = True
                self._reconnecting = False
                self._ws = ws
                while ws.open:
                    message = await asyncio.wait_for(ws.recv(), self._timeout)
                    self._last_ws_message = json.loads(message)
                    self.new_message = True
            except (
                websockets.ConnectionClosed,
                websockets.ConnectionClosedError,
                asyncio.exceptions.TimeoutError
            ):
                self._reconnecting = True
                continue

        self._connected = False

    async def __async_send(self, message):
        while not self._connected or self._reconnecting:
            await asyncio.sleep(self._timeout / 100)
        await self._ws.send(message)

    @staticmethod
    def _aero_angle_to_deg(aero_angle):
        start_angle_deg = 22
        degree_per_pulse = 0.0625
        return aero_angle * degree_per_pulse + start_angle_deg

    @staticmethod
    def _decode(message, resource):
        if message is not None:
            value = int(message[resource], 16)
            if resource == "angle":
                value = _WSResourcer._aero_angle_to_deg(value)
            return value
        else:
            return message

    @staticmethod
    def _duty_percent_to_duty_aero(duty_percent):
        duty_zero = 0x1D6A
        duty_max = 0x2710
        return (duty_percent / 100) * (duty_max - duty_zero) + duty_zero

    @staticmethod
    def _encode(message, resource):
        if resource == "duty":
            message = _WSResourcer._duty_percent_to_duty_aero(message)
        json_data = {resource: "0x{:X}".format(int(message))}
        return json.dumps(json_data)

    def get(self, resource):
        """Gets the last telemetry value of given resource.

        If the telemetry is not initialized (socket not opened yet) it opens
        a websocket and starts receiving telemetry asynchronously. Said
        telemetry will be saved, and can be retrieved by this method.

        Is most likely that this method will return None the first time it's
        called, so it's advised to call it in the after_script first.

        Every call of this method will set
        :attr:`~nyquist._private.network.ws._WSResourcer.new_message` to
        False, and every time a new message is stored, that attribute will
        be set to true. This way the user can implement methods to avoid
        reading the same message twice.
        """
        if resource not in self._get_uri_resource_map:
            raise ValueError("{} is not a valid uri.".format(resource))
        if not self._connected:
            self.__start_telemetry()
        if self._get_mode == "new" and not self.new_message:
            return None

        self.new_message = False
        decoded = self._decode(
            self._last_ws_message,
            self._get_uri_resource_map[resource]
        )
        return decoded

    def post(self, resource, value):
        """Sets the value of a resource through a fast channel,
        asynchronously.
        """
        if resource not in self._post_uri_resource_map:
            raise ValueError("{} is not a valid uri.".format(resource))
        if not self._connected:
            self.__start_telemetry()

        loop = asyncio.get_event_loop()
        encoded = self._encode(value, self._post_uri_resource_map[resource])
        loop.create_task(self.__async_send(encoded))
