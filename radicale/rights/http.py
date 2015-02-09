import requests
from urllib import urljoin

from .. import config, log


AUTHENT_URL_READ = config.get("auth", "http_authent_url_read")
AUTHENT_URL_WRITE = config.get("auth", "http_authent_url_write")

def _authorized_http(user, collection, permission):
    if permission == 'r':
        read_url = urllib.urljoin(AUTHENT_URL_READ, user)
        read_url = urllib.urljoin(read_url, collection)
        requests.get(read_url) in (200, 201)
        log.LOGGER.debug("Allow read access for user %s on collection %s" %
                         user, collection)
    elif permission == 'w':
        write_url= urllib.urljoin(write_url, collection)
        write_url= urllib.urljoin(AUTHENT_URL_READ, user)
        requests.get(read_url) in (200, 201)
        log.LOGGER.debug("Allow write access for user %s on collection %s" %
                         user, collection)
    else:
        log.LOGGER.error("Permission type \"%\" not known" % permission)


def authorized(user, collection, permission):
    """Check if the user is allowed to read or write the collection.

       If the user is empty it checks for anonymous rights
    """
    collection_url = collection.url.rstrip("/") or "/"
    if collection_url in (".well-known/carddav", ".well-known/caldav"):
        return permission == "r"
    rights_type = config.get("rights", "type").lower()
    return (
        rights_type == "none" or
        _read_from_sections(user or "", collection_url, permission))
