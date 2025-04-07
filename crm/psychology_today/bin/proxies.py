import random

def load_proxies(proxy_file="psychology_today/bin/good_proxies.txt"):
    proxies = []
    with open(proxy_file, "r") as pfile:
        for p in pfile.readlines():
            if p:
                proxies.append(p.strip())
    random.shuffle(proxies)
    return proxies
