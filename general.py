import pandas as pd
import random
import datetime
import base64
from selenium import webdriver

class Connection(object):
    def __init__(self, proxy_path, user_agent_path, phantomjs_path):
        # path  = 'C:\\Users\\dor.lavi\\Google Drive\\flights\\proxy_list.tsv'
        self.proxy_list = pd.read_csv(proxy_path, sep='\t')
        self.user_agent_df = pd.read_csv(user_agent_path)
        self.phantomjs_path = phantomjs_path

    def get_proxy(self):
        rnd = random.randint(0, len(self.proxy_list)-1)
        return self.proxy_list.ip[rnd]

    def get_userAgent(self):
        rnd = random.randint(0, len(self.user_agent_df)-1)
        return self.user_agent_df.userAgent[rnd]

    def get_service_args(self):
        ip = self.get_proxy()
        service_args = [
            '--proxy=%s' % (ip),
            '--proxy-type=http',
            '--proxy-auth=username:password'
        ]
        return service_args

    def get_driver(self):
        authentication_token = "Basic " + base64.b64encode(b'username:password')
        capa = webdriver.DesiredCapabilities.PHANTOMJS
        capa['phantomjs.page.customHeaders.Proxy-Authorization'] = authentication_token
        capa["phantomjs.page.settings.userAgent"] = (self.get_userAgent())
        self.driver = webdriver.PhantomJS(desired_capabilities=capa, service_args=self.get_service_args(), executable_path=self.phantomjs_path)
        webdriver.support.ui.WebDriverWait(self.driver, 15)
        return self.driver
