#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple command-line example for Latitude.

Command-line application that sets the users
current location.

Usage:
  $ python latitude.py

You can also get help on all the command-line flags the program understands
by running:

  $ python latitude.py --help

To get detailed log output run:

  $ python latitude.py --logging_level=DEBUG
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import gflags
import httplib2
import logging
import geopy
import geopy.distance
import os
import math
import json
import datetime
import pprint
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

def dt_from_epoch(epoch):
    epoch = int(epoch)
    secs = epoch/1000
    mils = epoch - (secs*1000)

    dt = datetime.datetime.fromtimestamp(secs)
    dt.replace(microsecond=mils*1000)
    return dt


FLAGS = gflags.FLAGS

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = 'client_secrets.json'

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console <https://code.google.com/apis/console>.

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)

# Set up a Flow object to be used if we need to authenticate.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/latitude.all.best',
    message=MISSING_CLIENT_SECRETS_MESSAGE)
CHARLES_HOME_LONGITUDE = 7.07532
CHARLES_HOME_LATITUDE = 43.618244

        
def main(argv):
  # Let the gflags module process the command-line arguments
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  # Set the logging according to the command-line flag
  logging.basicConfig(filename='Logs.log',level=logging.DEBUG)

  # If the Credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # Credentials will get written back to a file.
  storage = Storage('latitude.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build("latitude", "v1", http=http)

  try:
    aCurrentLocation = service.currentLocation().get(granularity='best').execute()
    print (str(aCurrentLocation))
    #aCurrentLocationJson = json.loads(aCurrentLocation)
    aTimeStamp = float(aCurrentLocation["timestampMs"])
    aDate = dt_from_epoch(aTimeStamp)
   
    pt1 = geopy.Point(CHARLES_HOME_LATITUDE, CHARLES_HOME_LONGITUDE)
    pt2 = geopy.Point(float(aCurrentLocation["latitude"]), float(aCurrentLocation["longitude"]))
   
    dist = geopy.distance.distance(pt1, pt2).km
   
    #dist = math.sqrt( ( float(aCurrentLocation["latitude"]) - CHARLES_HOME_LATITUDE)**2 + (float(aCurrentLocation["longitude"]) - CHARLES_HOME_LONGITUDE)**2 )
    print ("Distance was : " + str(dist) + " km at "  + str(aDate))

  except AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)