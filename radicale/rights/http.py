import requests
from .. import config, log
from string import Template

# TODO caching, any object we can attach to here?
# requests with session
# The module!


RIGHTS_URL_TEMPL = config.get("rights", "rights_url")

log.LOGGER.debug("http rights module loaded")


def get_cal_name(collection):
    # TODO normalize/lowercase?
    return collection


def _authorized_http(user, collection, permission):
    cal_name = get_cal_name(collection)
    rights_url = Template(RIGHTS_URL_TEMPL).substitute(user=user, cal=cal_name)
    real_permissions = requests.get(rights_url)
    log.LOGGER.debug("Permission %s reqeusted for user %s on collection %s with"
                     "calendar name %s with effective permission %s" %  (permission, user, collection, cal_name, real_permissions))
    return permission in real_permissions


def authorized(user, collection, permission):
    collection_url = collection.url.rstrip("/") or "/"
    return True
    return _authorized_http(user or "", collection_url, permission)
