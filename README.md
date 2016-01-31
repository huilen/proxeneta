# Proxeneta #

## Installation ##

```
pip install git+https://github.com/huilen/mobidick.git
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

## Add provider ##

Extend from Provider if you want to add other proxy providers:

```
from proxeneta.provider import Provider
from proxeneta.proxy import Proxy


class MyProvider(Provider):

    def get(self):
        // return list of Proxy's
```
