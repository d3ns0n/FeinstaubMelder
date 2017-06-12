#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from decimal import Decimal

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


class PostTweetTest(unittest.TestCase):
    config = {'tokens': {
        'consumer_key': 'consumer_key_value',
        'consumer_secret': 'consumer_secret_value',
        'access_key': 'access_key_value',
        'access_secret': 'access_secret_value'
    }}
    tweet_text = 'This is a tweet.'

    @mock.patch('tweetbeialarm.tweepy.OAuthHandler')
    @mock.patch('tweetbeialarm.tweepy.API')
    def test_post_tweet_should_initialize_OAuthHandler_correct(self, api_class, handler_class):
        tweetbeialarm.config = self.config

        tweetbeialarm.post_tweet(self.tweet_text)

        args, kwargs = handler_class.call_args
        assert args == ('consumer_key_value', 'consumer_secret_value',)

    @mock.patch('tweetbeialarm.tweepy.OAuthHandler')
    @mock.patch('tweetbeialarm.tweepy.API')
    def test_post_tweet_should_set_access_tokens_for_OAuthHandler_correct(self, api_class, handler_class):
        handler_class.return_value = handler_class
        tweetbeialarm.config = self.config

        tweetbeialarm.post_tweet(self.tweet_text)

        args, kwargs = handler_class.set_access_token.call_args
        assert args == ('access_key_value', 'access_secret_value',)

    @mock.patch('tweetbeialarm.tweepy.OAuthHandler')
    @mock.patch('tweetbeialarm.tweepy.API')
    def test_post_tweet_should_initialize_API_correct(self, api_class, handler_class):
        handler_class.return_value = handler_class
        tweetbeialarm.config = self.config

        tweetbeialarm.post_tweet(self.tweet_text)

        args, kwargs = api_class.call_args
        assert args == (handler_class,)

    @mock.patch('tweetbeialarm.tweepy.OAuthHandler')
    @mock.patch('tweetbeialarm.tweepy.API')
    def test_post_tweet_should_post_tweet_text_correct(self, api_class, handler_class):
        api_class.return_value = api_class
        tweetbeialarm.config = self.config

        tweetbeialarm.post_tweet(self.tweet_text)

        args, kwargs = api_class.update_status.call_args
        assert kwargs['status'] == self.tweet_text


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


class ParseResponseTest(unittest.TestCase):
    def test_parse_response_should_return_p1_value(self):
        json = '[{},' \
               '{ \
                    "sensordatavalues": [ \
                        { \
                            "id": 123456789, \
                            "value": "1.11", \
                            "value_type": "P1" \
                        }, \
                        { \
                            "id": 234567890, \
                            "value": "2.22", \
                            "value_type": "P2" \
                        } \
                    ] \
                }' \
               ']'

        value = tweetbeialarm.parse_response(mock.MagicMock(text=json))

        assert value.compare(Decimal('1.11')) == 0

    def test_parse_response_should_return_p1_value_of_newer_sensor_entry(self):
        json = '[ \
               { \
                   "sensordatavalues": [ \
                        { \
                            "id": 123456789, \
                            "value": "1.11", \
                            "value_type": "P1" \
                        }, \
                        { \
                            "id": 234567890, \
                            "value": "2.22", \
                            "value_type": "P2" \
                        } \
                    ]' \
               '},' \
               '{ \
                    "sensordatavalues": [ \
                        { \
                            "id": 123456789, \
                            "value": "3.33", \
                            "value_type": "P1" \
                        }, \
                        { \
                            "id": 234567890, \
                            "value": "4.44", \
                            "value_type": "P2" \
                        } \
                    ] \
                } \
               ]'

        value = tweetbeialarm.parse_response(mock.MagicMock(text=json))

        assert value.compare(Decimal('3.33')) == 0

    def test_parse_response_should_return_0_when_json_is_empty(self):
        json = '[ ]'

        value = tweetbeialarm.parse_response(mock.MagicMock(text=json))

        assert value == 0


class IterateSenorsTest(unittest.TestCase):
    config = {'max_value': 50}

    @mock.patch('tweetbeialarm.get_pm10_value')
    @mock.patch('tweetbeialarm.post_tweet')
    def test_iterate_sensors_should_get_pm_10_value_of_correct_sensor(
            self, post_tweet_function,
            get_pm10_value_function
    ):
        tweetbeialarm.config = self.config

        tweetbeialarm.iterate_sensors([1])

        args, kwargs = get_pm10_value_function.call_args
        assert args == (1,)

    @mock.patch('tweetbeialarm.get_pm10_value')
    @mock.patch('tweetbeialarm.post_tweet')
    def test_iterate_sensors_should_post_tweet_when_value_is_higher_than_50(
            self, post_tweet_function,
            get_pm10_value_function
    ):
        tweetbeialarm.config = self.config
        get_pm10_value_function.return_value = 60

        tweetbeialarm.iterate_sensors([1])

        args, kwargs = post_tweet_function.call_args
        assert args == ('Achtung Freiburg! Feinstaubwerte hoch - Sensor: 1 ist bei PM10 60 µg/m³',)
