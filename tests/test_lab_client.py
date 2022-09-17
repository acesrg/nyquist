import asyncio
from unittest import TestCase, IsolatedAsyncioTestCase, mock

from nyquist.lab import System
from nyquist._private.network.base import _Resource
from nyquist._private.network.http import (
    _HTTPConnection,
    _HTTPResourcer,
)
from nyquist._private.network.ws import _WSResourcer


class HTTPConnectionTestCase(TestCase):
    def setUp(self):
        self.my_ip = "127.0.0.1"
        self.my_port = 80
        self.my_timeout = 5
        self.connection = _HTTPConnection(
            self.my_ip,
            self.my_port,
            self.my_timeout,
        )

    def _test_some_manganeta_uri(self, my_url, my_method):
        self.connection.con.request = mock.MagicMock()
        HARDCODED_METHOD = "GET"
        self.connection.request(my_method, my_url)

        if "?" in my_url:
            expected_manganeta = my_url + "&verb=" + my_method
        else:
            expected_manganeta = my_url + "?verb=" + my_method

        self.assertEqual(
            mock.call(HARDCODED_METHOD, expected_manganeta),
            self.connection.con.request.call_args,
        )

    def test_manganeteada_post(self):
        self._test_some_manganeta_uri("/hey/look/a_wild/url", "POST")

    def test_manganeteada_get(self):
        self._test_some_manganeta_uri("/hey/look/a_wild/url", "GET")

    def test_manganeteada_wild_method(self):
        self._test_some_manganeta_uri("/hey/look/a_wild/url", "OMG")

    def test_manganeteada_with_query(self):
        self._test_some_manganeta_uri(
            "/hey/look/a_wild/url?pepito=jose",
            "POST"
        )

    def test_getresponse(self):
        self.connection.con.getresponse = mock.MagicMock(return_value="hey")
        self.assertFalse(self.connection.con.getresponse.called)
        retval = self.connection.getresponse()
        self.assertTrue(self.connection.con.getresponse.called)
        self.assertEqual(retval, "hey")


@mock.patch('nyquist._private.network.http._HTTPConnection.request')
@mock.patch('nyquist._private.network.http._HTTPConnection.getresponse')
class ResourcerTestCase(TestCase):
    def _mocky_response(self):
        return str.encode(self.mocky_response_value + "\n")

    def setUp(self):
        self.my_ip = "127.0.0.1"
        self.my_port = 80
        self.my_timeout = 5
        self.resourcer = _HTTPResourcer(
            self.my_ip,
            self.my_port,
            self.my_timeout,
        )

        self.mock_response_object = mock.MagicMock()
        self.mock_response_object.code = 200
        self.mocky_response_value = ""
        self.mock_response_object.read.side_effect = self._mocky_response

    def test_get_method(self, mock_getresponse, mock_request):
        mock_getresponse.return_value = self.mock_response_object
        self.mocky_response_value = "some_funny_value"

        res = self.resourcer.get("/some/funny/resource")
        self.assertEqual(res, "some_funny_value")

        self.assertEqual(
            mock.call("GET", "/some/funny/resource"),
            mock_request.call_args,
        )

    def test_set_method(self, mock_getresponse, mock_request):
        mock_getresponse.return_value = self.mock_response_object
        res = self.resourcer.post("/some/unfunny/resource", 10)
        self.assertEqual(res, 200)

        self.assertEqual(
            mock.call("POST", "/some/unfunny/resource?value=" + str(10)),
            mock_request.call_args,
        )


@mock.patch('websockets.client.WebSocketClientProtocol')
@mock.patch('websockets.connect')
class WSResourcerTestCase(IsolatedAsyncioTestCase):
    def _mocky_response(self):
        return str.encode(self.mocky_response_value + "\n")

    def setUp(self):
        self.my_ip = "127.0.0.1"
        self.my_port = 80
        self.my_timeout = 0.1
        self.ws_get_mode = 'last'
        self.resourcer = _WSResourcer(
            self.my_ip,
            self.my_port,
            self.my_timeout,
            self.ws_get_mode,
        )

    async def fake_telemetry(self):
        await asyncio.sleep(0.05)
        return '{"angle": "0x0000", "error": "0x0000"}'

    async def test_connection(self, mock_connect, mock_client):
        mock_context_manager_enter = mock_connect.return_value.__aenter__
        mock_recv = mock_context_manager_enter.return_value.recv
        mock_recv.side_effect = self.fake_telemetry

        self.resourcer.post("/propeller/pwm/duty", 10)
        await asyncio.sleep(0.1)

        self.assertEqual(
            mock_connect.call_args,
            mock.call('ws://127.0.0.1/stream')
        )

    # TODO: remove toast when know how to mock aiter
    async def toast_post_method(self, mock_connect, mock_client):
        mock_context_manager_enter = mock_connect.return_value.__aenter__
        mock_recv = mock_context_manager_enter.return_value.recv
        mock_send = mock_context_manager_enter.return_value.send
        mock_recv.side_effect = self.fake_telemetry

        self.resourcer.post("/propeller/pwm/duty", 10)
        await asyncio.sleep(0.1)

        self.assertEqual(
            mock_send.call_args,
            mock.call('{"duty": "0x1E61"}')
        )

    # TODO: remove toast when know how to mock aiter
    async def toast_get_method(self, mock_connect, mock_client):
        mock_context_manager_enter = mock_connect.return_value.__aenter__
        mock_recv = mock_context_manager_enter.return_value.recv
        mock_recv.side_effect = self.fake_telemetry

        # first initialize
        self.resourcer.get("/sensors/encoder/angle")
        await asyncio.sleep(0.1)

        # after waiting for telemetry to arrive, ask
        result = self.resourcer.get("/sensors/encoder/angle")

        self.assertEqual(result, 22)


@mock.patch('nyquist._private.network.ws._WSResourcer.get')
@mock.patch('nyquist._private.network.ws._WSResourcer.post')
@mock.patch('nyquist._private.network.http._HTTPResourcer.get')
@mock.patch('nyquist._private.network.http._HTTPResourcer.post')
class SystemTestCase(TestCase):
    def setUp(self):
        self.my_ip = "127.0.0.1"
        self.my_http_resources = [
            _Resource(
                uri="/hey/it_is/the/uri",
                methods=["GET", "POST"],
                docs="No docs, how naughty."
            ),
            _Resource(
                uri="/hey/it_is/another/uri",
                methods=["GET"],
                docs="Always documment your sources!."
            ),
        ]

        self.my_ws_resources = [
            _Resource(
                uri="/hey/ws/uri",
                methods=["GET", "POST"],
                docs="No docs, how naughty."
            ),
            _Resource(
                uri="/hey/ws/uri2",
                methods=["GET"],
                docs="Always documment your sources!."
            ),
        ]

        self.system = System(
            description="aeropendulum",
            ip=self.my_ip,
            http_resources=self.my_http_resources,
            ws_resources=self.my_ws_resources,
        )

    def test_correct_attributes(
        self,
        mock_post,
        mock_get,
        mock_ws_post,
        mock_ws_get

    ):
        def get_public_attributes_list(obj):
            attr_list = list(obj.__dict__.keys())
            for attr in obj.__dict__.keys():
                if attr[0] == "_":
                    attr_list.remove(attr)
            return attr_list

        attrs = get_public_attributes_list(self.system)
        self.assertListEqual(["hey"], attrs)

        attrs = get_public_attributes_list(self.system.hey)
        self.assertListEqual(["it_is", "ws"], attrs)

        attrs = get_public_attributes_list(self.system.hey.it_is)
        self.assertListEqual(["the", "another"], attrs)

        attrs = get_public_attributes_list(self.system.hey.it_is.the)
        self.assertListEqual(["uri"], attrs)

        attrs = get_public_attributes_list(self.system.hey.it_is.another)
        self.assertListEqual(["uri"], attrs)

        attrs = get_public_attributes_list(self.system.hey.it_is.the.uri)
        self.assertListEqual(["help", "get", "post"], attrs)

        attrs = get_public_attributes_list(self.system.hey.it_is.another.uri)
        self.assertListEqual(["help", "get"], attrs)

        attrs = get_public_attributes_list(self.system.hey.ws)
        self.assertListEqual(["uri", "uri2"], attrs)

        attrs = get_public_attributes_list(self.system.hey.ws.uri)
        self.assertListEqual(["help", "get", "post"], attrs)

        attrs = get_public_attributes_list(self.system.hey.ws.uri2)
        self.assertListEqual(["help", "get"], attrs)

    def test_calls(self, mock_post, mock_get, mock_ws_post, mock_ws_get):
        self.system.hey.it_is.the.uri.post("some")
        self.assertEqual(
            mock_post.call_args,
            mock.call("/hey/it_is/the/uri", "some"),
        )

        self.system.hey.it_is.another.uri.get()
        self.assertEqual(
            mock_get.call_args,
            mock.call("/hey/it_is/another/uri"),
        )

    def test_instance_with_defaults(
        self,
        mock_post,
        mock_get,
        mock_ws_post,
        mock_ws_get
    ):
        System("aeropendulum")

    def test_non_existent_system(
        self,
        mock_post,
        mock_get,
        mock_ws_post,
        mock_ws_get
    ):
        with self.assertRaises(ValueError):
            System("this_system_does_not_exist")

    @mock.patch('builtins.print')
    def test_docs(
        self,
        mock_post,
        mock_get,
        mock_ws_post,
        mock_ws_get,
        mock_print
    ):
        self.system.hey.it_is.the.uri.help()
        self.assertEqual(
            print.call_args,
            mock.call(self.my_http_resources[0].docs),
        )

        self.system.hey.it_is.another.uri.help()
        self.assertEqual(
            print.call_args,
            mock.call(self.my_http_resources[1].docs),
        )
