import unittest

import mock

import tweetbeialarm


class TestPerformRequest(unittest.TestCase):
    sensor_id = 1337

    @mock.patch('tweetbeialarm.requests.get')
    def test_perform_request_should_request_correct_url(self, get_function):
        get_function.return_value = mock.MagicMock(status_code=200)

        tweetbeialarm.perform_request(self.sensor_id)

        args, kwargs = get_function.call_args
        assert args == ('http://api.luftdaten.info/static/v1/sensor/{0}/'.format(self.sensor_id),)

    @mock.patch('tweetbeialarm.requests.get')
    def test_perform_request_should_handle_status_code_200_correct(self, get_function):
        mocked_response = mock.MagicMock(status_code=200)
        get_function.return_value = mocked_response

        response = tweetbeialarm.perform_request(self.sensor_id)

        assert response == mocked_response

    @mock.patch('tweetbeialarm.requests.get')
    def test_perform_request_should_handle_status_code_300_correct(self, get_function):
        mocked_response = mock.MagicMock(status_code=300)
        get_function.return_value = mocked_response

        response = tweetbeialarm.perform_request(self.sensor_id)

        assert response == 0

    @mock.patch('tweetbeialarm.requests.get')
    def test_perform_request_should_handle_status_code_100_correct(self, get_function):
        mocked_response = mock.MagicMock(status_code=100)
        get_function.return_value = mocked_response

        response = tweetbeialarm.perform_request(self.sensor_id)

        assert response == 0
