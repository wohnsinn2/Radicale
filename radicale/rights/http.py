import requests

from .. import config, log
from ..utils import CacheDict
from string import Template

# TODO use __missing__ in dict to fill the cache

RIGHTS_URL_TEMPL = config.get("rights", "rights_url")

log.LOGGER.debug("http rights module loaded")
TIMEOUT = config.get("rights", "http_cache_timeout")
CAL_USER = config.get("rights", "http_calendar_user")


session = requests.Session()
permission_cache = CacheDict(TIMEOUT)


def _get_cal_name(collection):
    # TODO normalize/lowercase
    # TODO use urllib parser
    # TODO check sanity [a-zA-Z-_]
    # ! TODO check user!!!
    collection_parts = collection.split('/')
    if len(collection_parts) >= 2:
        cal_name = collection.split('/')[1]
        cal_name = cal_name.rstrip(".ics")
        return cal_name
    else:
        return None

def _get_user(collection):
    return collection.split('/')[0]

def _http_get_permission(user, cal_name):
    rights_url = Template(RIGHTS_URL_TEMPL).substitute(user=user, cal=cal_name)
    response = session.get(rights_url)
    permission = response.text or ""
    response.raise_for_status()
    return permission


def _get_permission(user, collection):
    cal_name = _get_cal_name(collection)
    if cal_name is None:
        return 'r'
    try:
        permission = permission_cache[user][cal_name]
        log.LOGGER.debug("Got permission {} for user {} and collection {} from cache".format(permission, user, cal_name))
        return permission
    except KeyError:
        try:
            permission = _http_get_permission(user, cal_name)
            log.LOGGER.debug("Got permission {} for user {} and collection {} from http".format(permission, user, cal_name))
        except:
            log.LOGGER.debug("Error while trying to get the permission for user {} on collection {}".format(user, cal_name))
            return ""
        permission_cache[user] = {cal_name: permission}
        return permission


def _authorized_http(user, collection, permission):
    real_permission = _get_permission(user, collection)
    return permission in real_permission


def authorized(user, collection, permission):
    collection_url = collection.url.rstrip("/") or "/"
    cal_user = _get_user(collection_url)
    # TODO: iterate over list of additional auth providers
    # the collection owner supplied in the URL is not the system user
    if cal_user != CAL_USER:
        return False
    # the authenticated user is the system backend (no personal user)
    if user == CAL_USER:
        return True
    # no anonymous access
    if user is None:
        return False
    else:
        return _authorized_http(user, collection_url, permission)
