#!/usr/bin/env python
# -*- coding: utf-8 -*-

import decimal
import json
import operator

import requests
import tweepy


def load_config():
    with open('config.json') as json_data_file:
        return json.load(json_data_file)


def perform_request(sensor):
    response = requests.get('http://api.luftdaten.info/static/v1/sensor/{0}/'.format(sensor))
    if response.status_code and not 200 <= response.status_code < 300:
        # Request konnte nicht erfolgreich ausgeführt werden
        print('Luftdaten API error response: status code = {0}'.format(response.status_code))
        return 0
    return response


def parse_response(response):
    parsed_json = json.loads(response.text)
    l = len(parsed_json)
    if l:
        a = len(parsed_json[l - 1]['sensordatavalues'])
        if a:
            # in der Regel ist der erste Wert der PM10
            result = (parsed_json[l - 1]['sensordatavalues'][0]['value'])
            return decimal.Decimal(result)
    # Falls Json leer ist
    return 0


# Auswerte Funktion
def get_pm10_value(sensor):
    # Sensordaten für SDS011 abfragen und Maximum prüfen
    # dazu die api von luftdaten.info nutzen
    # Peter Fürle @Alpensichtung Hotzenwald 04/2017
    response = perform_request(sensor)
    return parse_response(response)


def post_tweet(tweet_text):
    tokens = config["tokens"]
    # OAuth process, using the keys and tokens
    auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
    auth.set_access_token(tokens["access_key"], tokens["access_secret"])

    # Creation of the actual interface, using authentication
    api = tweepy.API(auth)

    # twittern nur Text
    api.update_status(status=tweet_text)


def iterate_sensors(sensors):
    maxlist = {}
    for sensor in sensors:
        # Sensor und PM10 Wert als Key-Value Pair im Dictionary speichern
        maxlist[sensor] = get_pm10_value(sensor)

    # das Key-Value Pair mit dem höchsten Sensorwert ermitteln
    maxsensor = max(maxlist.iteritems(), key=operator.itemgetter(1))

    # hier kannst du den Maxwert anpassen
    if maxsensor[1] > config["max_value"]:
        tweet = 'Achtung Freiburg! Feinstaubwerte hoch - Sensor: {0} ist bei PM10 {1} µg/m³' \
            .format(maxsensor[0], maxsensor[1])
        # hier den Tweet auslösen
        post_tweet(tweet)

if __name__ == '__main__':
    config = load_config()
    iterate_sensors(config["sensors"])
