import time
import threading
import logging

from collections import defaultdict

from test.utils import BaseTestCase, MockProvider

from proxeneta.utils import timecall
from proxeneta.proxy import Proxy, Pool


logger = logging.getLogger(__name__)


# <seconds>: <max_requests>
LIMITS = {10: 10,
          60: 20,
          120: 30}
TOTAL_REQUESTS = 100
TEST_PROXY_HOST = '181.14.245.194'
TEST_PROXY_PORT = 8000


class TestProxy(BaseTestCase):

    def test_check(self):
        invalid_proxy = Proxy(host='185.92.220.84', port=3128)
        valid_proxy = Proxy(host=TEST_PROXY_HOST, port=TEST_PROXY_PORT)
        self.assertFalse(invalid_proxy.check())
        self.assertTrue(valid_proxy.check())


class TestPool(BaseTestCase):

    def test_proxy_rotation(self):
        self._test_proxy_rotation(1)
        self.assertRaises(AssertionError, lambda: self._test_proxy_rotation(.001))

    def _test_proxy_rotation(self, rotation_interval):
        requests = defaultdict(list)
        pool = Pool(MockProvider(),
                    size=TOTAL_REQUESTS / 4,
                    rotation_interval=rotation_interval)
        pool.start()

        def request(proxy):
            logger.info("Request through proxy %s", proxy)
            requests[proxy].append(time.time())

        threads = []
        for _ in range(TOTAL_REQUESTS):
            thread = threading.Thread(target=lambda: request(pool.get()))
            thread.start()
            threads.append(thread)

        logger.info("Waiting until all requests are done")
        for thread in threads:
            if thread.is_alive():
                thread.join()

        logger.info("Check proxy rotation")
        for proxy, request_times in requests.items():
            for count, request_time in enumerate(request_times, start=1):
                for interval, max_count in LIMITS.items():
                    if request_times[0] + request_time >= interval:
                        logger.info("Requests through proxy %s " \
                                    "within interval %d: %d",
                                    proxy, interval, count)
                        self.assertLessEqual(count, max_count)
