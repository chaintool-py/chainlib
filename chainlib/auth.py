# standard imports
import base64


class Auth:

    def urllib_header(self):
        raise NotImplementedError()


class BasicAuth(Auth):

    def __init__(self, username, password):
        self.username = username
        self.password = password


    def urllib_header(self):
        s = '{}:{}'.format(self.username, self.password)
        b = base64.b64encode(s.encode('utf-8'))
        return (('Authorization'), ('Basic ' + b.decode('utf-8')),)


class CustomHeaderTokenAuth(Auth):

    def __init__(self, header_name, auth_token):
        self.header_name = header_name
        self.auth_token = auth_token


    def urllib_header(self):
        return (self.header_name, self.auth_token,)
