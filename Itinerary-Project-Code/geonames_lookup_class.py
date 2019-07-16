"""
-*- coding: utf-8 -*-

geonames_lookup_class.py

This is a modified websearch for geonames id codes and locations based in
large part on the geonames-org-wrapper by Markbnj.  The original is
available here: https://gist.github.com/Markbnj/e1541d15699c4d2d8c98

For information on endpoints and arguments see the geonames API documentation at: http://www.geonames.org/export/web-services.html

the class takes arguments depending on the type of lookup, ex:
    Geonames.lookup_nearby_place(lat, long, feat_class, feat_code, verbose)
        Defaults for feat_class and feat_code are none, verbose is "short"
            Verbose can also take Medium, Long, or Full.

NOTE: Currently only the lookup_nearby_place function can return both a
proper URL lookup as well as possible errors from geonames (such as too
many searches per day or per hour on a free account).  The two other
features lookup_neighborhood and lookup_feature should be recoded to better
match the nearby_place function.

@author: Adam Franklin-Lyons
    Marlboro College | Python 3.7

Created on Tue May 21 16:01:10 2019
"""

import requests
import json

class Geonames(object):
    """
    This class provides a client to call certain entrypoints of the geonames
    API.  Each instantiation of the class requires a username to function.
    """

    def __init__(self, username):
        self.GEONAMES_USER = username
        self.GEONAMES_API = "http://api.geonames.org/"
        self._base_feature_url = "{}getJSON?geonameId={{}}&username={}\
                &style=full".format(self.GEONAMES_API,
                self.GEONAMES_USER)
        self._base_nearby_url = "{}findNearbyJSON?lat={{}}\
                &lng={{}}{{}}&username={}".format(self.GEONAMES_API,
                self.GEONAMES_USER)
        self._base_neighbourhood_url = "{}neighbourhoodJSON?lat={{}}\
                &lng={{}}&username={}".format(self.GEONAMES_USER,
                self.GEONAMES_USER)

    def lookup_feature(self, geoname_id):
        """
        Looks up a feature based on its geonames id
        """
        url = self._base_feature_url.format(geoname_id)
        response = requests.get(url)
        return self._decode_feature(response.text)

    def _decode_feature(self, response_text):
        """
        Decodes the response from geonames.org feature lookup and
        returns the properties in a dict.
        """
        raw_result = json.loads(response_text)
        if 'status' in raw_result:
            raise Exception("Geonames: call returned status {}".format(
                            raw_result['status']['value']))
        result = response_text.json()['geonames'][0]
        return result

    def lookup_nearby_place(self, latitude, longitude, feature_class=None,
                            feature_code=None, verbose='short'):
        """
        Looks up places near a specific geographic location, optionally
        filtering for feature class and feature code.
        """
        feature_filter = ''
        if feature_class:
            feature_filter += "&featureClass={}".format(feature_class)
        if feature_code:
            feature_filter += "&featureCode={}".format(feature_code)
        if verbose:
            feature_filter += "&style={}".format(verbose)
        url = self._base_nearby_url.format(latitude, longitude,
                                           feature_filter)
        response = requests.get(url)
        return self._decode_nearby_place(response)

    def _decode_nearby_place(self, response):
        """
        Decodes the response from the geonames nearby place lookup and
        returns the properties in a dict.
        """
        raw_result = json.loads(response.text)
        result = None
        try:
            if len(raw_result['geonames']) > 0:
                result = response.json()['geonames'][0]
        except KeyError:
            result = response.json()['status']
        return result

    def lookup_neighbourhood(self, latitude, longitude):
        """
        Finds the neighborhood record for a specific geographic location.
        """
        url = self._base_neighbourhood_url.format(latitude, longitude)
        response = requests.get(url)
        return self._decode_neighbourhood(response.text)

    def _decode_neighbourhood(self, response_text):
        raw_result = json.loads(response_text)
        result = None

        if 'status' not in raw_result:
            result = response_text.json()['geonames'][0]
        return result
