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
        print(response.request.headers.get('cookie'))
        print('打印GET结果：url:%s, bytes:%s'%(response.request.url, response.body))

    @gen.coroutine
    def method_get(self, url):
        try:
            cookie = {"Cookie" : 'my_cookie=kizzlepc'}
            response = yield httpclient.AsyncHTTPClient().fetch(url, headers=cookie)
            print('GET请求完成： %s' % url)
        except Exception as e:
            print('GET请求错误: %s %s' % (e, url))
            raise gen.Return('')
        raise gen.Return(response)

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
                response = yield self.method_get(current_url)
                
                if response:
                    yield self.handle_data(response)
                    self._fetched.add(current_url)
                else:
                    self._fetching.remove(current_url)
                    yield self._q.put(current_url)

            finally:
                self._q.task_done()

        @gen.coroutine
        def worker():
            while True:
                yield fetch_url()
  

        for url in self.urls:
            yield self._q.put(url)

        for _ in range(self.concurrency):
            worker()
        yield self._q.join(timeout=timedelta(seconds=300))   
        assert self._fetching == self._fetched
        print('GET完成共用： %d 秒, 完成请求的url个数: %s.' % (time.time() - start, len(self._fetched)))

    def get(self):
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._run)


def main():
    urls = [
        'http://httpbin.org/cookies',   
        ]
    s = AsyMethodGetSpider(urls, 10)
    s.get()

if __name__ == '__main__':
    main()
