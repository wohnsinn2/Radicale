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
    cal_name = collection.rstrip(".ics")
    cal_name = cal_name.split('/')[-1]
    return cal_name


def _http_get_permission(user, collection):
    cal_name = _get_cal_name(collection)
    rights_url = Template(RIGHTS_URL_TEMPL).substitute(user=user, cal=cal_name)
    response = session.get(rights_url)
    permission = response.text or ""
    response.raise_for_status()
    return permission


def _get_permission(user, collection):
    try:
        return permission_cache[user][collection]
        log.LOGGER.debug("Got permission {} for user {} and collection {} from cache".format(content, user, collection))
    except KeyError:
        try:
            permission = _http_get_permission(user, collection)
            permission_cache[user] = {collection: permission}
            log.LOGGER.debug("Got permission {} for user {} and collection {} from http".format(content, user, collection))
            return permission
        except:
            return ""


def _authorized_http(user, collection, permission):
    real_permission = _get_permission(user, collection)
    return permission in real_permission


def authorized(user, collection, permission):
    collection_url = collection.url.rstrip("/") or "/"
    if user is None:
        return False
    else:
        return _authorized_http(user, collection_url, permission)
