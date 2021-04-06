from unittest import TestCase, mock

from nyquist.lab.client import System
from nyquist._private.network.http import (
    _HTTPConnection,
    _Resourcer,
    _Resource,
)


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
        self.resourcer = _Resourcer(
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


@mock.patch('nyquist._private.network.http._Resourcer.get')
@mock.patch('nyquist._private.network.http._Resourcer.post')
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

        self.system = System(
            ip=self.my_ip,
            http_resources=self.my_http_resources,
            ws_resources=None,
        )

    def test_correct_attributes(self, mock_post, mock_get):
        def get_public_attributes_list(obj):
            attr_list = list(obj.__dict__.keys())
            for attr in obj.__dict__.keys():
                if attr[0] == "_":
                    attr_list.remove(attr)
            return attr_list

        attrs = get_public_attributes_list(self.system)
        self.assertListEqual(["hey"], attrs)

        attrs = get_public_attributes_list(self.system.hey)
        self.assertListEqual(["it_is"], attrs)

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

    def test_calls(self, mock_post, mock_get):
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

    @mock.patch('builtins.print')
    def test_docs(self, mock_post, mock_get, mock_print):
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
