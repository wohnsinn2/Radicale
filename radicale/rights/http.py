import requests

from .. import config, log
from ..utils import CacheDict
from string import Template

# TODO use __missing__ in dict to fill the cache

RIGHTS_URL_TEMPL = config.get("rights", "rights_url")

log.LOGGER.debug("http rights module loaded")
TIMEOUT = config.get("rights", "http_cache_timeout")

session = requests.Session()
permission_cache = CacheDict(TIMEOUT)


def _get_cal_name(collection):
    # TODO normalize/lowercase
    # check sanity [a-zA-Z-_]
    # use urllib parser
    log.LOGGER.debug(collection)
    cal_name = collection
    cal_name = cal_name.split('/')[-1]
    cal_name = cal_name.rstrip(".ics")
    log.LOGGER.debug(cal_name)
    return cal_name


def _http_get_permission(user, cal_name):
    rights_url = Template(RIGHTS_URL_TEMPL).substitute(user=user, cal=cal_name)
    response = session.get(rights_url)
    permission = response.text or ""
    response.raise_for_status()
    return permission


def _get_permission(user, collection):
    cal_name = _get_cal_name(collection)
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
    if user is None:
        return False
    else:
        return _authorized_http(user, collection_url, permission)
