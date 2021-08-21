# standard imports
import urllib
import base64
import logging

logg = logging.getLogger(__name__)


# THANKS to https://stackoverflow.com/questions/2407126/python-urllib2-basic-auth-problem
class PreemptiveBasicAuthHandler(urllib.request.HTTPBasicAuthHandler):
    """Handler for basic auth urllib callback.
    """

    def http_request(self, req):
        """Handler for basic auth urllib callback.

        :param req: Request payload
        :type req: str
        :return: Request payload
        :rtype: str
        """
        url = req.get_full_url()
        realm = None
        user, pw = self.passwd.find_user_password(realm, url)

        if pw:
            raw = "%s:%s" % (user, pw)
            raw_bytes = raw.encode('utf-8')
            auth_base_bytes = base64.encodebytes(raw_bytes)
            auth_base = auth_base_bytes.decode('utf-8')
            auth_base_clean = auth_base.replace('\n', '').strip()
            auth = 'Basic %s' % auth_base_clean
            req.add_unredirected_header(self.auth_header, auth)
            logg.debug('head {}'.format(req.header_items()))

        return req

    https_request = http_request
