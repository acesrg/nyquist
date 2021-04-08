import asyncio
import json

import websockets


class _WSResourcer():
    def __init__(self, ip, port, timeout):
        self._connected = False
        self._last_ws_message = None
        self._uri = "ws://{}/stream".format(ip)
        self._port = port
        self._timeout = timeout
        self.new_message = False

    def __start_telemetry(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.__gather_telemetry())

    async def __gather_telemetry(self):
        async with websockets.connect(self._uri) as ws:
            self._connected = True
            self._ws = ws
            while ws.open:
                try:
                    message = await asyncio.wait_for(ws.recv(), self._timeout)
                    self._last_ws_message = json.loads(message)
                    self.new_message = True
                except asyncio.exceptions.TimeoutError:
                    pass
        self._connected = False

    async def __async_send(self, message):
        while not self._connected:
            await asyncio.sleep(self._timeout / 100)
        await self._ws.send(message)

    @staticmethod
    def _aero_angle_to_deg(aero_angle):
        start_angle_deg = 22
        degree_per_pulse = 0.0625
        return aero_angle * degree_per_pulse + start_angle_deg

    @staticmethod
    def _decode(message, resource):
        if resource == "/sensors/encoder/angle":
            if message is not None:
                aero_angle = int(message["angle"], 16)
                return _WSResourcer._aero_angle_to_deg(aero_angle)
            else:
                return message
        raise IOError

    @staticmethod
    def _duty_percent_to_duty_aero(duty_percent):
        duty_zero = 0x1D6A
        duty_max = 0x2710
        return (duty_percent / 100) * (duty_max - duty_zero) + duty_zero

    @staticmethod
    def _encode(message, resource):
        if resource == "/propeller/pwm/duty":
            duty = _WSResourcer._duty_percent_to_duty_aero(message)
            json_data = {"duty": "0x{:X}".format(int(duty))}
            return json.dumps(json_data)
        raise IOError

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
        if not self._connected:
            self.__start_telemetry()
        self.new_message = False
        return self._decode(self._last_ws_message, resource)

    def post(self, resource, value):
        """Sets the value of a resource through a fast channel,
        asynchronously.
        """
        if not self._connected:
            self.__start_telemetry()

        loop = asyncio.get_event_loop()
        loop.create_task(self.__async_send(self._encode(value, resource)))
