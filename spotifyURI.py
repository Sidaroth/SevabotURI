#!/sevabot
# -*- coding: utf-8 -*-

#####################
#
# Author: Christian Holt (Sidaroth / Ymabob)
#
# Purpose: Module for Sevabot that recognizes and retrieves information about Spotify URI's
#
# Dependency: This module uses the non-standard module 'requests'. It can be acquired by doing
#             'pip install requests'
#
# Last edit: 16-Dec-13 
#
# License: Free to use for any purpose.  (Public Domain)
#
#####################

import Skype4Py
import logging
 
from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode
 
import re
import requests
import string
import math

logger = logging.getLogger('SpotifyURIHandler')
logger.setLevel(logging.INFO)
logger.debug('SpotifyURIHandler module level load import')

HELP_TEXT = """
    This module does not take any commands.

    The module automatically parses the chat for any
    spotify URI's and retrieves the information.
"""
 
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

        self.commands = {
            "!spotify": self.help
        }


    def help(self, msg, status, desc, chat_id):
        """
        Print help text to chat.
        """

        # Make sure we don't trigger ourselves with the help text 
        if not desc:
            self.send_msg(msg, status, HELP_TEXT)
    
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

        # Compile regex objects
        uriRegex = re.compile("(?P<URI>spotify:(?P<type>(album|track|artist)):([a-zA-Z0-9]{22}))")
        urlRegex = re.compile("http(s)?://open.spotify.com/(?P<type>(album|track|artist))/(?P<URI>([a-zA-Z0-9]{22}))")

        uriMatch = uriRegex.search(body)        # Check for URI match (spotify:track:URI)
        urlMatch = urlRegex.search(body)        # Check for URL match (open.spotify.com/track/URI)
        matchType = ""

        if uriMatch:
            matchType = uriMatch.group("type")
            uri = uriMatch.group("URI")

        elif urlMatch:
            matchType = urlMatch.group("type")
            uri = "spotify:" + matchType + ":" + urlMatch.group("URI")
            
        else:
            return False

        if len(uri):
            # Retrieve the response, and get the JSON from spotify's lookup API. 
            response = requests.get('http://ws.spotify.com/lookup/1/.json?uri=' + uri)
            data = response.json()

            # Parse track type JSON (URI/URL was a track i.e spotify:track:)
            if matchType == "track":
                album     = data["track"]["album"]["name"]
                albumYear = data["track"]["album"]["released"]
                track     = data["track"]["name"]
                length    = data["track"]["length"]
                artist    = data["track"]["artists"][0]["name"]
                minutes, seconds = self.convertToMinuteTime(length)

                self.send_msg(msg, status, "Track: " + track + " (" + repr(minutes) + ":" + repr(seconds).zfill(2) + ") by " + artist)  
                self.send_msg(msg, status, "Album: " + album + " (" + albumYear + ")")

            # Parse album type JSON (URI/URL was an album i.e spotify:album:)
            elif matchType == "album":
                album  = data["album"]["name"]
                artist = data["album"]["artist"]
                year   = data["album"]["released"]

                self.send_msg(msg, status, "Album: " + album + " (" + year + ") by " + artist)

            # Parse artist type JSON (URI/URL was an aritst i.e spotify:artist:)
            elif matchType == "artist":
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
