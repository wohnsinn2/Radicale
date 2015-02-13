import requests

from .. import config, log
from ..utils import CacheDict
from string import Template


# TODO caching, any object we can attach to here?
# requests with session
# The module!


RIGHTS_URL_TEMPL = config.get("rights", "rights_url")

log.LOGGER.debug("http rights module loaded")
TIMEOUT = config.get("rights", "http_cache_timeout")

session = requests.Session()
permission_cache = {}


def _get_cal_name(collection):
    # TODO normalize/lowercase?
    # check sanity [a-zA-Z-_]
    cal_name = collection.rstrip(".ics")
    cal_name = cal_name.split('/')[-1]
    return cal_name


def _http_get_permission(user, collection):
    cal_name = _get_cal_name(collection)
    rights_url = Template(RIGHTS_URL_TEMPL).substitute(user=user, cal=cal_name)
    response = session.get(rights_url, )
    content = response.text or ""
    try:
        response.raise_for_status()
        return content
    except requests.exceptions.HTTPError:
        return None


# TODO: multi-dim cache
def _add_entry(user, collection, permission):
    entry = {collection: permission}
    try:
        permission_cache[user].update(entry)
    except KeyError:
        new_entry = CacheDict(TIMEOUT, entry)
        permission_cache[user] = new_entry


def _get_permission(user, collection):
    try:
        return permission_cache[user][collection]
    except KeyError:
        permission = _http_get_permission(user, collection)
        if permission is not None:
            _add_entry(user, collection, permission)
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
