import threading
import requests
import logging
import time

from requests.exceptions import ConnectTimeout

from proxeneta.utils import timecall


logger = logging.getLogger(__name__)


TEST_URL = 'http://google.com/'
PROXY_TIMEOUT = 5
PROXY_TTL = 120


class Proxy(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.creation_time = time.time()
        self.last_time = -float('inf')
        self.response_time = float('inf')
        self.checked = False

    def check(self):
        if self.checked and time.time() - self.creation_time < PROXY_TTL:
            return True
        return self._check()

    def _check(self):
        try:
            logger.info("Checking %s", self.url)
            proxies = {'http': self.url}
            time, response = timecall(
                lambda: requests.get(TEST_URL,
                                     proxies=proxies,
                                     timeout=PROXY_TIMEOUT))
            if response.status_code == 200:
                logger.info("Check %s successful", self.url)
                self.response_time = time
                self.checked = True
                return True
        except ConnectTimeout as e:
            logger.error("Check %s failed: %s", self.url, e)
        return False

    @property
    def url(self):
        return 'http://{host}:{port}/'.format(
            host=self.host, port=self.port)

    def __repr__(self):
        return self.url

    def __str__(self):
        return self.url
            

class Pool(threading.Thread):

    def __init__(self, provider, size=20, rotation_interval=30):
        super(Pool, self).__init__()
        self.setDaemon(True)
        self.provider = provider
        self.size = size
        self.rotation_interval = rotation_interval
        self._proxies = []
        self._cond = threading.Condition()

    def refresh(self):
        logger.info("Refreshing pool...")
        self._cond.acquire()
        proxies = self._proxies + self.provider.get()
        proxies = self._filter_expired(proxies)
        proxies = self._sort_by_response_time(proxies)
        self._proxies = proxies
        logger.info("Pool refreshed: %d proxies", len(proxies))
        self._cond.notify_all()
        self._cond.release()

    def run(self):
        while True:
            if len(self.proxies) < self.size:
                self.refresh()
            time.sleep(1)

    @property
    def proxies(self):
        return self._filter_recently_used(self._proxies)

    def get(self):
        self._cond.acquire()
        proxies = self.proxies
        while proxies == []:
            logger.info("Pool is empty, waiting...")
            self._cond.wait()
            proxies = self.proxies
        proxy = proxies[0]
        proxy.last_time = time.time()
        logger.info("Proxy %s provided", proxy)
        self._cond.release()
        return proxy

    def _sort_by_response_time(self, proxies):
        return sorted(proxies, key=lambda p: p.response_time)

    def _filter_recently_used(self, proxies):
        return [p for p in proxies
                if time.time() - p.last_time > self.rotation_interval]

    def _filter_expired(self, proxies):
        count = len(proxies)
        proxies = [p for p in proxies if p.check()]
        logger.info("%d proxies expired", count - len(proxies))
        return proxies
