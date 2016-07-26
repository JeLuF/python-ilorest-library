###
# Copyright 2016 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-
"""Module for working with global configuration options."""

#---------Imports---------

import os
import re
import logging
import ConfigParser

#---------End of imports---------


#---------Debug logger---------

LOGGER = logging.getLogger(__name__)

#---------End of debug logger---------

class AutoConfigParser(object):
    """Auto configuration parser"""
    # properties starting with _ac__ are automatically
    # serialized to config file
    _config_pattern = re.compile(r'_ac__(?P<confkey>.*)')

    def __init__(self, filename=None):
        self._sectionname = 'globals'
        self._configfile = filename

    def _get_ac_keys(self):
        """Retrieve parse option keys"""
        result = []
        for key in self.__dict__.keys():
            match = AutoConfigParser._config_pattern.search(key)
            if match:
                result.append(match.group('confkey'))
        return result

    def _get(self, key):
        """Retrieve parse option key

        :param key: key to retrieve.
        :type key: str.

        """
        ackey = '_ac__%s' % key.replace('-', '_')
        if ackey in self.__dict__:
            return self.__dict__[ackey]
        return None

    def _set(self, key, value):
        """Set parse option key

        :param key: key to be set.
        :type key: str.
        :param value: value to be given to key.
        :type value: str.

        """
        ackey = '_ac__%s' % key.replace('-', '_')
        if ackey in self.__dict__:
            self.__dict__[ackey] = value
        return None

    def load(self, filename=None):
        """Load configuration settings from the file filename, if filename"""
        """ is None then the value from get_configfile() is used

        :param filename: file name to be used for config loading.
        :type filename: str.

        """
        fname = self.get_configfile()
        if filename is not None and len(filename) > 0:
            fname = filename

        if fname is None or not os.path.isfile(fname):
            return

        try:
            config = ConfigParser.RawConfigParser()
            config.read(fname)
            for key in self._get_ac_keys():
                configval = None
                try:
                    configval = config.get(self._sectionname, key)
                except ConfigParser.NoOptionError:
                    # also try with - instead of _
                    try:
                        configval = config.get(self._sectionname, \
                                                        key.replace('_', '-'))
                    except ConfigParser.NoOptionError:
                        pass

                if configval is not None and len(configval) > 0:
                    ackey = '_ac__%s' % key
                    self.__dict__[ackey] = configval
        except ConfigParser.NoOptionError:
            pass
        except ConfigParser.NoSectionError:
            pass

    def save(self, filename=None):
        """Save configuration settings from the file filename, if filename"""
        """ is None then the value from get_configfile() is used

        :param filename: file name to be used for config saving.
        :type filename: str.

        """
        fname = self.get_configfile()
        if filename is not None and len(filename) > 0:
            fname = filename

        if fname is None or len(fname) == 0:
            return

        config = ConfigParser.RawConfigParser()
        try:
            config.add_section(self._sectionname)
        except ConfigParser.DuplicateSectionError:
            pass # ignored

        for key in self._get_ac_keys():
            ackey = '_ac__%s' % key
            config.set(self._sectionname, key, str(self.__dict__[ackey]))

        fileh = open(self._configfile, 'wb')
        config.write(fileh)
        fileh.close()

    def get_configfile(self):
        """ The current configuration file location"""
        return self._configfile

