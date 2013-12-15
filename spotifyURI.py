#!/sevabot
# -*- coding: utf-8 -*-

#####################
#
# Author: Christian Holt (Sidaroth / Ymabob)
#
# Purpose: Module for Sevabot that recognizes and retrieves information about Spotify URI's
#
# Last edit: 15-Dec-13 
#
# License: Free to use for any purpose.  (Public Domain)
#
#####################

import Skype4Py
import logging
 
from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode
 
import re
import simplejson
import requests
import json
import string
import math

logger = logging.getLogger('SpotifyURIHandler')
logger.setLevel(logging.DEBUG)
logger.debug('SpotifyURIHandler module level load import')
 
 
class SpotifyURIHandler(StatefulSkypeHandler):
    """
    Skype message handler class for spotify URIs
    """
 
    def __init__(self):
        """
        ...
        """
 
        logger.debug("SpotifyURIHandler constructed")
 
    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instance
        """
 
        logger.debug("SpotifyURIHandler init")
        self.sevabot = sevabot
        self.skype = sevabot.getSkype()
    
    def convertToMinuteTime(self, seconds):
        """
        Converts the given seconds into minutes and seconds (min:sec)
        """
        secs = seconds
        mins =  int(secs / 60)
        secs -= 60 * mins
        return mins, int(secs)

    def handle_message(self, msg, status):
        """
        Handles all the work on the messages and URI checking. 
        """

        # if the chat message is from the bot, ignore it. 
        if msg.FromHandle == "bubbebot":
            return False

        body = ensure_unicode(msg.Body)
        words = body.split(" ")

        # if it's an empty string, ignore it. 
        if len(words) == 0:
            return False

        # Compile regex object
        prog = re.compile("(?P<URI>spotify:(?P<type>(album|track|artist)):([a-zA-Z0-9]{22}))")
        match = prog.search(body)

        if match:
            uri = match.group("URI")

            if len(uri):
                # Retrieve the response, and get the JSON from spotify's lookup API. 
                response = requests.get('http://ws.spotify.com/lookup/1/.json?uri=' + uri)
                data = response.json()

                # Parse track type JSON (URI was a track i.e spotify:track:)
                if match.group("type") == "track":
                    album     = data["track"]["album"]["name"]
                    albumYear = data["track"]["album"]["released"]
                    track     = data["track"]["name"]
                    length    = data["track"]["length"]
                    artist    = data["track"]["artists"][0]["name"]
                    minutes, seconds = self.convertToMinuteTime(length)

                    self.send_msg(msg, status, "Track: " + track + " (" + repr(minutes) + ":" + repr(seconds).zfill(2) + ") by " + artist)  
                    self.send_msg(msg, status, "Album: " + album + " (" + albumYear + ")")

                # Parse album type JSON (URI was an album i.e spotify:album:)
                elif match.group("type") == "album":
                    album  = data["album"]["name"]
                    artist = data["album"]["artist"]
                    year   = data["album"]["released"]

                    self.send_msg(msg, status, "Album: " + album + " (" + year + ") by " + artist)

                # Parse artist type JSON (URI was an aritst i.e spotify:artist:)
                elif match.group("type") == "artist":
                    artist = data["artist"]["name"]
                    self.send_msg(msg, status, "Artist: " + artist)

                return True
 
        return False

    def shutdown():
        """
        Called when module is reloaded.
        """
 
        logger.debug("SpotifyURIHandler shutdown")
 
    def send_msg(self, msg, status, args):
        """
        Print stuff
        """
 
        msg.Chat.SendMessage(args)

 
# export the instance to sevabot
sevabot_handler = SpotifyURIHandler()
 
__all__ = ['sevabot_handler']
