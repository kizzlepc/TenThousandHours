import time
from datetime import timedelta
from tornado import httpclient, gen, ioloop, queues


class AsyMethodGetSpider(object):
    def __init__(self, urls, concurrency):
        self.urls = urls
        self.concurrency = concurrency
        self._q = queues.Queue()
        self._fetching = set()
        self._fetched = set()
    
    @gen.coroutine
    def handle_data(self, response):
        print('打印GET结果：url:%s, bytes:%s'%(response.request.url, len(response.body)))

    @gen.coroutine
    def method_get(self, url):
        try:
            yield httpclient.AsyncHTTPClient().fetch(url, self.handle_data)
            print('GET请求完成： %s' % url)
        except Exception as e:
            print('GET请求错误: %s %s' % (e, url))
            raise gen.Return('')

    @gen.coroutine
    def _run(self):
        start = time.time()
        @gen.coroutine
        def fetch_url():
            current_url = yield self._q.get()
            try:
                if current_url in self._fetching:
                    return

                print('GET正在请求： %s' % current_url)
                self._fetching.add(current_url)
                yield self.method_get(current_url)
                self._fetched.add(current_url)

                for i in range(self.concurrency):
                    if self.urls:
                        yield self._q.put(self.urls.pop())

            finally:
                self._q.task_done()

        @gen.coroutine
        def worker():
            while True:
                yield fetch_url()

        self._q.put(self.urls.pop())

        for _ in range(self.concurrency):
            worker()
        yield self._q.join(timeout=timedelta(seconds=300))   
        assert self._fetching == self._fetched
        print('GET完成共用： %d 秒, 完成请求的url个数: %s.' % (time.time() - start, len(self._fetched)))

    def run(self):
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._run)


def main():
    urls = [
        'http://www.baidu.com',
        'http://www.qq.com',
        'http://www.taobao.com',
        'https://www.python.org/',
        'https://www.yahoo.com/',
        'https://github.com/',
        ] 
    s = AsyMethodGetSpider(urls, 10)
    s.run()

if __name__ == '__main__':
    main()
