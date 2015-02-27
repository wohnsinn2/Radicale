# -*- coding: utf-8 -*-
#
# This file is part of Radicale Server - Calendar Server
# Copyright © 2012 Ehsanul Hoque
# Copyright © 2013 Guillaume Ayoub
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radicale.  If not, see <http://www.gnu.org/licenses/>.

"""
HTTP authentication.

Authentication based on the ``requests`` module.

Post a request to an authentication server with the username/password.
Anything other than a 200/201 response is considered auth failure.

"""

import requests

from .. import config, log, utils

AUTH_URL = config.get("auth", "http_url")
USER_PARAM = config.get("auth", "http_user_parameter")
PASSWORD_PARAM = config.get("auth", "http_password_parameter")
TIMEOUT = config.get("auth", "http_cache_timeout")
CAL_USER = config.get("rights", "http_calendar_user")
CAL_USER_PW = config.get("rights", "http_calendar_user_password")

session = requests.Session()
user_cache = utils.CacheDict(TIMEOUT)


def is_authenticated(user, password):
    """Check if ``user``/``password`` couple is valid."""
    log.LOGGER.debug("HTTP-based auth on %s." % AUTH_URL)
    if user is None or password is None:
        return False
    if user == CAL_USER and password == CAL_USER_PW:
        return True
    try:
        cache_password = user_cache[user]
        log.LOGGER.debug('Got password {} for user {} from cache password {}'.format(password, user, cache_password))
        return password == cache_password
    except KeyError:
        payload = {USER_PARAM: user, PASSWORD_PARAM: password}
        state = session.post(AUTH_URL, data=payload, stream=False).status_code
        if state in (200, 201):
                  user_cache[user] = password
                  log.LOGGER.debug('Got password {} for user {} from http'.format(password, user))
                  return True
        return False
