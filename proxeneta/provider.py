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
