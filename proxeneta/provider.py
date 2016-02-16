import base64
import re
import threading
import requests

from lxml import html

from proxeneta.proxy import Proxy


class Provider(object):

    def get(self):
        return []


class SSLProxiesProvider(Provider):

    def get(self):
        response = requests.get('http://www.sslproxies.org/')
        dom = html.fromstring(response.content)
        trs = dom.xpath('//table[@id="proxylisttable"]//tr')
        proxies = []
        for tr in trs[1:-1]:
            tds = tr.xpath('td/text()')
            proxies.append(Proxy(host=tds[0], port=tds[1]))
        return proxies


class ProxyListProvider(Provider):

    def __init__(self):
        self._page = 1

    def get(self):
        proxies = []
        response = requests.get(
            'https://proxy-list.org/spanish/index.php?p=' + str(self._page))
        dom = html.fromstring(response.content)
        for row in dom.xpath('//li[@class="proxy"]//script/text()'):
            row = re.compile('\'(.+)\'').search(row).group(1)
            row = base64.b64decode(row).decode()
            row = re.compile('(.+):(.+)').search(row)
            proxies.append(Proxy(host=row.group(0), port=row.group(2)))
        if self._page >= 10:
            self._page += 1
        else:
            self._page = 1
        return proxies


class USProxyProvider(Provider):

    def get(self):
        proxies = []
        response = requests.get('https://www.us-proxy.org/')
        dom = html.fromstring(response.content)
        for host, port in zip(dom.xpath('//tr/td[1]/text()'),
                              dom.xpath('//tr/td[2]/text()')):
            proxies.append(Proxy(host=host, port=port))
        return proxies


class MixProvider(Provider):

    def __init__(self, *providers):
        self._providers = providers
        self._index = 0

    def get(self):
        provider = self._providers[self._index]
        if self._index < len(self._providers) - 1:
            self._index += 1
        else:
            self._index = 0
        return provider.get()
