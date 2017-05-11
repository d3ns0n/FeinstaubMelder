#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import requests
import tweepy


def load_config():
    with open('config.json') as json_data_file:
        return json.load(json_data_file)


def perform_request(sensor):
    response = requests.get('http://api.luftdaten.info/static/v1/sensor/{0}/'.format(sensor))
    if response.status_code and not 200 <= response.status_code < 300:
        # Request konnte nicht erfolgreich ausgeführt werden
        print('Luftdaten API error respone: status code = {0}'.format(response.status_code))
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
            return result
    # Falls Json unvollständig ist
    return 0


# Auswerte Funktion
def get_pm10_value(sensor):
    # Sensordaten für SDS011 abfragen und Maximum prüfen
    # dazu die api von luftdaten.info nutzen
    # Peter Fürle @Alpensichtung Hotzenwald 04/2017
    response = perform_request(sensor)
    return parse_response(response)


config = load_config()

sensors = config["sensors"]
maxlist = []
for sensor in sensors:
    print(sensor)
    # Liste erzeugen mit den Werten, ok float() ist nicht ganz sauber...
    maxlist.append(float(get_pm10_value(sensor)))

# welches ist der höchste Wert ?
maxwert = max(maxlist)
# zu welchem Sensor aus der Liste sd gehört der Höchstwert ?
maxsensor = sensors[maxlist.index(maxwert)]

tweet = ' Aktuell liegen keine Grenzwert- Überschreitungen in Freiburg vor '
alarm = False

# hier kannst du den Maxwert anpassen
if maxwert > config["max_value"]:
    tweet = 'Achtung Freiburg! Feinstaubwerte hoch - Sensor: {0} ist bei PM10 {1} µg/m³'.format(maxsensor, maxwert)
    # hier den Tweet auslösen
    alarm = True

print tweet

tokens = config["tokens"]
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(tokens["consumer_key"], tokens["consumer_secret"])
auth.set_access_token(tokens["access_key"], tokens["access_secret"])

# Creation of the actual interface, using authentication
api = tweepy.API(auth)

# twittern nur Text
if alarm:
    api.update_status(status=tweet)
