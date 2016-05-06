####################################################################
# Author: Chunlin Zhang <zhangchunlin@gmail.com>
# License: BSD
####################################################################

__author__ = 'zhangchunlin'
__author_email__ = 'zhangchunlin@gmail.com'
__url__ = 'https://github.com/zhangchunlin/linci'
__license__ = 'MIT'
version = __version__ = '0.1'

import requests
import os
import json
import logging
from urlparse import urljoin

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%y-%m-%d %H:%M:%S')
log = logging.getLogger("linci.client")

class ConfigError(Exception): pass
class LoginError(Exception): pass

class LinciClient(object):
    def __init__(self,client_conf_fname = ".linci_client.conf"):
        self.client_conf_fname = client_conf_fname
        self.client_conf_fpath = None
        self.config = self.get_config()
        self._server_url = self.config.get("server_url","")
        self._cookies = self.config.get("cookies",{})
        self._session = requests.Session()
        self.make_sure_login()

    def get_config(self):
        dpath = os.getcwd()
        l = dpath.split(os.sep)
        fpath = None
        while l:
            p = os.path.join(os.sep.join(l),self.client_conf_fname)
            if os.path.exists(p):
                fpath = p
                break
            l = l[:-1]
        if fpath:
            log.debug("load linci client config file from %s"%(fpath))
            self.client_conf_fpath = fpath
            return json.load(open(fpath))
        else:
            raise ConfigError("linci client config file not found, your should use linci_client_config to generate a %s file"%(self.client_conf_fname))

    def set_config(self,k,v):
        self.config = self.get_config()
        self.config[k] = v
        with open(self.client_conf_fpath, 'wb') as f:
            json.dump(self.config,f,indent=2)

    def request_post(self,uri,data={},files=None):
        if not self._server_url:
            raise ConfigError("no server url, you should linci_client_config --server-url=SERVER_URL")
        url = urljoin(self._server_url,uri)
        return self._session.post(url,data=data,cookies=self.config.get("cookies",{}),files=files)

    def make_sure_login(self):
        r = self.request_post("apiuser/api_get_auth")
        if not (r.status_code==200 and r.json().get("username")):
            self.config["cookies"] = {}
            username = self.config.get("username")
            password = self.config.get("password")
            r = self.request_post("apiuser/api_login",data={"username":username,"password":password})
            if r.status_code==200:
                rjson = r.json()
                if rjson.get("success"):
                    log.debug("login in successfully: %s"%(rjson.get("msg")))
                    token_name = rjson.get("token_name")
                    token = rjson.get("token")
                    self.set_config("cookies",{token_name:token})
                    return
                else:
                    raise LoginError("fail to login, err message: %s"%(rjson.get("msg","unknown error")))
            raise LoginError("fail to login, server return status_code: %s, text: %s"%(r.status_code,r.text))
