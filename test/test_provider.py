from test.utils import BaseTestCase

from proxeneta.provider import (SSLProxiesProvider,
                                USProxyProvider,
                                ProxyListProvider)


class TestProviders(BaseTestCase):

    def test(self):
        self._test(SSLProxiesProvider())
        self._test(USProxyProvider())
        self._test(ProxyListProvider())

    def _test(self, provider):
        proxies = provider.get()
        self.assertGreater(len(proxies), 0)
        valid = 0
        for proxy in proxies:
            if proxy.check():
                valid += 1
            if valid > 3:
                break
        self.assertGreater(valid, 3)
