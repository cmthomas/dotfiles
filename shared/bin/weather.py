#!/usr/bin/python
# coding=utf-8

import argparse
import math
import os
import random
import re
import sys
import time
import urllib2


BASEURL = 'http://weather.noaa.gov/pub/data/observations/metar/stations'

# Coefficients of the heat index formula.
hc1 = -42.379
hc2 = 2.04901523
hc3 = 10.14333127
hc4 = -0.22475541
hc5 = -0.00683783
hc6 = -0.05481717
hc7 = 0.00122874
hc8 = 0.00085282
hc9 = -0.00000199

# Coefficients of the wind chill formula.
wc1 = 13.12
wc2 = 0.6215
wc3 = -11.37
wc4 = 0.3965


def heat_index(temp, rh):
  # The heat index is only defined for temperatures at or above 27 °C and
  # relative humidity above 40%.
  if temp < 27 or rh < 40:
    return temp

  # The NOAA heat index formula requires temperature in degrees Fahrenheit
  # and relative humidity as a percentage (40%, not 0.4).
  temp = temp * 1.8 + 32
  hi = (hc1 + hc2 * temp + hc3 * rh + hc4 * temp * rh +
      hc5 * math.pow(temp, 2) + hc6 * math.pow(rh, 2) +
      hc7 * math.pow(temp, 2) * rh + hc8 * temp * math.pow(rh, 2) +
      hc9 * math.pow(temp, 2) * math.pow(rh, 2))
  return int(round((hi - 32) / 1.8))


def wind_chill(temp, wind):
  # The wind chill is only defined for temperatures at or below 10 °C and
  # wind speed above 3 knots.
  if temp > 10 or wind < 3:
    return temp

  # The wind chill formula requires the wind speed in km/h.
  wind = wind * 1.852
  return int(round(wc1 + wc2 * temp + wc3 * math.pow(wind, 0.16) +
      wc4 * temp * math.pow(wind, 0.16)))


def parse_temperature_rh(metar_text):
  temp_re = re.compile(r' ([M]?\d{2})/([M]?\d{2}) ')
  if temp_re.search(metar_text):
    temperature = int(temp_re.search(metar_text).group(1).replace('M', '-'))
    dewpoint = int(temp_re.search(metar_text).group(2).replace('M', '-'))

    # Es = saturation vapor pressure, E = actual vapor pressure
    es = 6.11 * pow(10, (7.5 * temperature / (237.7 + temperature)))
    e = 6.11 * pow(10, (7.5 * dewpoint / (237.7 + dewpoint)))
    rh = int(round(e/es * 100))
    return temperature, dewpoint, rh


def parse_wind(metar_text):
  wind_re = re.compile(r' (\d{3}|VRB)(\d{2})(?:G(\d{2}))?(KT|MPS)')
  result = wind_re.search(metar_text)
  if result:
    direction = result.group(1)
    wind_speed = int(result.group(2))
    gust_speed = int(result.group(3)) if result.group(3) else None
    unit = result.group(4)

    if unit == 'MPS':
      wind_speed = int(round(wind_speed * 1.944))
      if gust_speed:
        gust_speed = int(round(gust_speed * 1.944))
    return direction, wind_speed, gust_speed


def report(station, metar_text, si_units):
  print '%s:' % station,

  temperature, dewpoint, rh = parse_temperature_rh(metar_text)
  direction, wind, gusts = parse_wind(metar_text)

  if temperature <= 10:
    apparent_temperature = wind_chill(temperature, wind)
  elif temperature >= 27:
    apparent_temperature = heat_index(temperature, rh)
  else:
    apparent_temperature = temperature

  # Ignore the wind chill/heat index if it makes a difference of 2 °C or less.
  if abs(apparent_temperature - temperature) <= 2:
    apparent_temperature = temperature

  if apparent_temperature < 10:
    color_start = '^fg(#0077ff)'
  elif apparent_temperature > 30:
    color_start = '^fg(#ff0000)'
  else:
    color_start = ''
  color_stop = '^fg()'

  if not si_units:
    temperature = temperature * 9 / 5 + 32
    apparent_temperature = apparent_temperature * 9 / 5 + 32
    unit = '°F'
  else:
    unit = '°C'

  if apparent_temperature == temperature:
    print '%s%.0f %s%s, rh %.0f%%' % (color_start, temperature, unit, 
                                      color_stop, rh)
  else:
    print '%s%.0f %s (app. %.0f %s)%s, rh %.0f%%' % (color_start,
                                                     temperature, unit,
                                                     apparent_temperature,
                                                     unit, color_stop, rh)
  print metar_text


def main(argv):
  parser = argparse.ArgumentParser(description='Print the current weather.')
  parser.add_argument('ICAO', nargs='+',
                      help='Display weather at the airport with this ICAO code')
  parser.add_argument('-s', '--si_units', action='store_true',
                      help='Force SI units')
  parser.add_argument('-u', '--us_units', action='store_true',
                      help='Force US customary units')
  args = parser.parse_args()

  if args.us_units:
    si_units = False
  elif args.si_units:
    si_units = True
  else:
    us_station_re = re.compile(r'(^K|^PA|^PG|^PH|^PM|^TI|^TJ)')
    if us_station_re.search(args.ICAO[0]):
      si_units = False
    else:
      si_units = True

  # Sleep for a random period of time 0...10 minutes.
  # (This makes it less likely that all machines will hit the site at the
  # same time.)
  time.sleep(random.randint(0, 600))

  try:
    site = urllib2.urlopen(os.path.join(BASEURL, args.ICAO[0] + '.TXT'))
    metar_text = site.read()
    site.close()
    report(args.ICAO[0], metar_text, si_units)
  except urllib2.HTTPError:
    print args.ICAO[0] + ': not available'


if __name__ == '__main__':
  main(sys.argv)

