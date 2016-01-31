from test.utils import BaseTestCase

from proxeneta.provider import SSLProxiesProvider


class TestSSLProxiesProvider(BaseTestCase):

    def test(self):
        provider = SSLProxiesProvider()
        proxies = provider.get()
        self.assertGreater(len(proxies), 0)
        valid = 0
        for proxy in proxies:
            if proxy.check():
                valid += 1
            if valid > 3:
                break
        self.assertGreater(valid, 3)
