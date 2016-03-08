#!/usr/bin/python
# coding=utf-8

import argparse
import math
import os
import re
import sys
import urllib2


BASEURL = 'http://weather.noaa.gov/pub/data/observations/metar/stations'


def parse_temperature_rh(metar_text):
  temp_re = re.compile(r'([M]?\d{2})/([M]?\d{2})')
  if temp_re.search(metar_text):
    temperature = int(temp_re.search(metar_text).group(1).replace('M', '-'))
    dewpoint = int(temp_re.search(metar_text).group(2).replace('M', '-'))

    # Es = saturation vapor pressure, E = actual vapor pressure
    es = 6.11 * pow(10, (7.5 * temperature / (237.7 + temperature)))
    e = 6.11 * pow(10, (7.5 * dewpoint / (237.7 + dewpoint)))
    rh = int(round(e/es * 100))
    return temperature, dewpoint, rh


def report(station, metar_text, si_units):
  print '%s:' % station,

  temperature, dewpoint, rh = parse_temperature_rh(metar_text)
  if temperature < 10:
    color_start = '^fg(#0077ff)'
  elif temperature > 30:
    color_start = '^fg(#ff0000)'
  else:
    color_start = ''
  color_stop = '^fg()'

  if si_units:
    print '%s%.0f °C%s, rh %.0f%%' % (color_start, temperature, color_stop, rh)
  else:
    print '%s%.0f °F%s, rh %.0f%%' % (color_start, temperature * 9 / 5 + 32,
                                      color_stop, rh)


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

  try:
    site = urllib2.urlopen(os.path.join(BASEURL, args.ICAO[0] + '.TXT'))
    metar_text = site.read()
    site.close()
    report(args.ICAO[0], metar_text, si_units)
  except urllib2.HTTPError:
    print args.ICAO[0] + ': not available'


if __name__ == '__main__':
  main(sys.argv)

