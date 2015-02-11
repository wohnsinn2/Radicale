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
    cal_name = collection.rstrip(".ics")
    cal_name = cal_name.split('/')[-1]
    return cal_name


def _authorized_http(user, collection, permission):
    cal_name = get_cal_name(collection)
    rights_url = Template(RIGHTS_URL_TEMPL).substitute(user=user, cal=cal_name)
    response = requests.get(rights_url)
    state = response.status_code
    content = response.text or ""
    log.LOGGER.debug("Permission %s reqeusted for user %s on collection %s with"
                     "calendar name %s with effective permission %s" % (permission, user, collection, cal_name, content))
    return (permission in content) and (state in (200, 201))


def authorized(user, collection, permission):
    collection_url = collection.url.rstrip("/") or "/"
    if user is None:
        return False
    else:
        return _authorized_http(user, collection_url, permission)
