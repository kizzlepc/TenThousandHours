from __future__ import print_function

import gevent
from gevent import monkey
monkey.patch_all()

import requests

urls = [
    'http://www.baidu.com',
    'http://www.qq.com',
    'http://www.taobao.com',
    ]


def print_head(url):
    print('starting %s'%url)
    data = requests.get(url)
    print('%s:%s, resualt:%s'%(url, len(data.text), data.status_code))
    
jobs = [gevent.spawn(print_head(url)) for url in urls]

gevent.wait(jobs)