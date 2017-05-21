import unittest

import mock

import tweetbeialarm


class LoadConfigTest(unittest.TestCase):
    @mock.patch('tweetbeialarm.json.load')
    @mock.patch('tweetbeialarm.open')
    def test_load_config_should_load_correct_file(self, open_function, load_function):
        open_function.return_value = mock.MagicMock()

        tweetbeialarm.load_config()

        args, kwargs = open_function.call_args
        assert args == ('config.json',)


class GetPm10ValueTest(unittest.TestCase):
    sensor_id = 1337

    @mock.patch('tweetbeialarm.perform_request')
    @mock.patch('tweetbeialarm.parse_response')
    def test_get_pm10_value_should_request_correct_sensor(self, parse_response_function, perform_request_function):
        tweetbeialarm.get_pm10_value(self.sensor_id)

        args, kwargs = perform_request_function.call_args
        assert args == (self.sensor_id,)

    @mock.patch('tweetbeialarm.perform_request')
    @mock.patch('tweetbeialarm.parse_response')
    def test_get_pm10_value_should_handle_response_correct(self, parse_response_function, perform_request_function):
        response = mock.MagicMock

        perform_request_function.return_value = response

        tweetbeialarm.get_pm10_value(self.sensor_id)

        args, kwargs = parse_response_function.call_args
        assert args == (response,)


class PerformRequestTest(unittest.TestCase):
    sensor_id = 1337

    @mock.patch('tweetbeialarm.requests.get')
    def test_perform_request_should_build_url_correct(self, get_function):
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
