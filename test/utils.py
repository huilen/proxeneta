import unittest
import logging
import string
import random
import time

from proxeneta.proxy import Proxy
from proxeneta.provider import Provider


logger = logging.getLogger(__name__)


PROVIDER_SIZE = 20


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)


class MockProvider(Provider):

    def get(self):
        proxies = [MockProxy(valid=random.choice([True, False]))
                   for _ in range(PROVIDER_SIZE)]
        logger.info("%d proxies found", len(proxies))
        return proxies


class MockProxy(Proxy):

    def __init__(self, valid=True):
        host = random_word(5) + '.com'
        port = random.choice([80, 8080, 8000])
        super(MockProxy, self).__init__(host=host, port=port)
        self.valid = valid

    def _check(self):
        logger.info("Checking %s", self.url)
        if self.valid:
            self.response_time = random.randint(1, 10)
            self.checked = True
            logger.info("Check %s successful", self.url)
            return True
        else:
            logger.error("Check %s failed", self.url)
            return False


def random_word(length):
   return ''.join(random.choice(string.ascii_letters.lower())
                  for i in range(length))
