"""
absolutely not do the time separation

put junk DNS before every get

wireshark capture filter:
    port domain (port 53 DNS traffic) or (host localip and host 128.135.11.239)

    all DNS traffic, and all things between you and blase

    display only DNS queries from you
    display only A and AAAA

    fake website will cause the DNS resolver to try and A record the nameserver, Alec's appended a .comcastblablabla
    so the $ just looks for requests that END with the mysite.com

    get doens't return till site fully loaded/timesout

    driver.get fake website will make the tombstone DNS library*
"""
