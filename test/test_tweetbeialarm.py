import unittest

import mock

import tweetbeialarm


def mock_response(url):
    return mock.MagicMock(status_code=200)


class TestMethods(unittest.TestCase):
    @mock.patch('tweetbeialarm.requests.get', side_effect=mock_response)
    def test_perform_request(self, get_function):
        response = tweetbeialarm.perform_request(1337)
        self.assertEqual(response.status_code, 200)
