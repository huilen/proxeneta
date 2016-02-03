import threading
import requests
import logging
import time

from proxeneta.utils import timecall, chunks


logger = logging.getLogger(__name__)


TEST_URL = 'http://google.com/'
PROXY_TIMEOUT = 5
PROXY_TTL = 120
PROXY_ROTATION_INTERVAL = 20
MAX_THREADS = 100
LOG_FILE = 'proxeneta.log'


class Proxy(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.last_check_time = -float('inf')
        self.last_use_time = -float('inf')
        self.response_time = float('inf')
        self.valid = None

    @property
    def available(self):
        elapsed_time = time.time() - self.last_use_time
        return self.valid and elapsed_time > PROXY_ROTATION_INTERVAL

    def check(self):
        if time.time() - self.last_check_time < PROXY_TTL:
            # check expired
            self.valid = None
            self.response_time = float('inf')
            self.last_check_time = -float('inf')
            self.last_use_time = -float('inf')
        return self._check() if self.valid == None else self.valid

    def _check(self):
        try:
            logger.debug("Checking %s", self.url)
            proxies = {'http': self.url}
            call_time, response = timecall(
                lambda: requests.get(TEST_URL,
                                     proxies=proxies,
                                     timeout=PROXY_TIMEOUT))
            if response.status_code == 200:
                logger.debug("Check %s successful", self.url)
                self.response_time = call_time
                self.last_check_time = time.time()
                self.valid = True
                return True
            else:
                raise Exception(response.content)
        except Exception as e:
            logger.debug("Check %s failed: %s", self.url, e)
        self.valid = False
        self.response_time = float('inf')
        self.last_use_time = float('inf')
        self.last_check_time = float('inf')
        return False

    @property
    def url(self):
        return 'http://{host}:{port}/'.format(
            host=self.host, port=self.port)

    def __repr__(self):
        return self.url

    def __str__(self):
        return self.url

    def __eq__(self, other):
        return self.url == other.url


class Pool(object):

    def __init__(self, provider):
        self.provider = provider
        self._proxies = []
        self._cond = threading.Condition()
        self._start()

    def _start(self):
        def start_thread(fn):
            thread = threading.Thread(target=fn)
            thread.setDaemon(True)
            thread.start()
        start_thread(self._add_from_provider)
        start_thread(self._check)
        start_thread(self._log)

    @property
    def proxies(self):
        proxies = [p for p in self._proxies if p.available]
        return sorted(proxies, key=lambda p: p.response_time)

    def get(self):
        self._cond.acquire()
        proxies = self.proxies
        if proxies == []:
            logger.debug("Pool is empty, waiting...")
        while proxies == []:
            self._cond.wait()
            proxies = self.proxies
        proxy = proxies[0]
        proxy.last_use_time = time.time()
        logger.info("Proxy %s provided", proxy)
        self._cond.release()
        return proxy

    def _check(self):
        def loop(partition_number):
            while True:
                for idx, proxy in enumerate(self._proxies):
                    if idx % MAX_THREADS == partition_number:
                        if proxy.check() and proxy.available:
                            self._cond.acquire()
                            self._cond.notify_all()
                            self._cond.release()
                time.sleep(1)
        for idx in range(MAX_THREADS):
            threading.Thread(target=loop, args=(idx,)).start()

    def _add_from_provider(self):
        while True:
            count = 0
            for proxy in self.provider.get():
                if proxy not in self._proxies:
                    self._proxies.append(proxy)
                    count += 1
            logger.info("%d new proxies found", count)
            time.sleep(10)

    def _log(self):
        while True:
            with open(LOG_FILE, 'w') as f:
                proxies = sorted(self._proxies, key=lambda p: p.response_time)
                valid = [p for p in self._proxies if p.valid]
                available = [p for p in self._proxies if p.available]
                log = '{available} available / {total} total\n'.format(
                    available=len(available), total=len(valid))
                log += 'PROXY\tRESPONSE TIME\tVALID\tAVAILABLE\n'
                for proxy in proxies:
                    line = []
                    line.append(proxy.url)
                    line.append(str(proxy.response_time))
                    line.append(str(proxy.valid))
                    line.append(str(proxy.available))
                    log += '\t'.join(line) + '\n'
                f.write(log)
            time.sleep(3)
