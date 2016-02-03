# Proxeneta #

Proxy pool for Python.

- Support for multiple providers
- Ranking by response time
- Asynchronous check and expiration
- Throttling

## Installation ##

```
pip install git+https://github.com/huilen/proxeneta.git
```

## Usage ##

```
from proxeneta.proxy import Pool
from proxeneta.provider import SSLProxiesProvider


provider = SSLProxiesProvider()
pool = Pool(provider,
            size=100,
            rotation_interval=10)

proxy = pool.get()

print(proxy.host)
print(proxy.port)
```

You must use only once each proxy that you get from the pool, and call
pool.get() again whenever you need to do a new request. The pool will
take care of checking and throttling the proxies for you, and it is
prepared to be used concurrently.

## Configuration ##

You may want to adjust the following parameters to suit your needs:

PROXY_TIMEOUT = 5
PROXY_TTL = 120
PROXY_ROTATION_INTERVAL = 20
MAX_THREADS = 100

## Logs ##

You can see the table of proxies in real time at proxeneta.log:

```
$ watch cat proxeneta.log
Every 2,0s: cat proxeneta.log                          Wed Feb  3 16:57:51 2016

PROXY   RESPONSE TIME   VALID   AVAILABLE
http://177.105.214.32:80/       0.7377173900604248      True    False
http://181.14.245.194:8000/     0.7536842823028564      True    False
http://151.236.216.251:10000/   0.7693524360656738      True    False
http://162.243.23.177:3128/     0.7832741737365723      None    None
http://151.80.177.18:8080/      0.845919132232666       True    False
http://185.92.220.84:3128/      0.9640853404998779      True    False
http://192.95.27.140:8080/      0.9745504856109619      True    False
http://188.166.156.246:3128/    1.0246026515960693      None    None
http://87.98.134.136:8080/      1.1917321681976318      True    False
http://45.32.59.33:8080/        1.3310987949371338      True    False
http://210.245.25.226:3128/     1.4117391109466553      True    False
http://128.199.128.102:8080/    1.415281057357788       True    False
http://54.157.185.100:10000/    1.448075294494629       True    False
```

## Add provider ##

Extend from Provider if you want to add other proxy providers:

```
from proxeneta.provider import Provider
from proxeneta.proxy import Proxy


class MyProvider(Provider):

    def get(self):
        // return list of Proxy's
```
