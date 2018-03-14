import time
from datetime import timedelta
from tornado import httpclient, gen, ioloop, queues


class AsyMethodPostSpider(object):
    def __init__(self, url, params, concurrency):
        self.url = url
        self.params = params
        self.concurrency = concurrency
        self._q = queues.Queue()
        self._fetching = set()
        self._fetched = set()
    
    @gen.coroutine
    def handle_data(self, response):
        print('打印结果：url:%s, body:%s'%(response.request.url, response.body))

    @gen.coroutine
    def method_post(self, url, req_body):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',}
            response = yield httpclient.AsyncHTTPClient().fetch(url, method='POST', headers=headers, body=req_body)
            print('POST请求完成： %s' % url)
        except Exception as e:
            print('POST请求错误: %s , 请求参数：%s' % (e, req_body))
            raise gen.Return('')
        raise gen.Return(response)

    @gen.coroutine
    def _run(self):
        start = time.time()
        @gen.coroutine
        def fetch_url():
            req_body = yield self._q.get()
            try:
                if req_body in self._fetching:
                    return

                print('post参数： %s' % req_body)
                self._fetching.add(req_body)
                response = yield self.method_post(self.url, req_body)

                if response:
                    yield self.handle_data(response)
                    self._fetched.add(req_body)
                else:
                    self._fetching.remove(req_body)
                    yield self._q.put(req_body)


            finally:
                self._q.task_done()

        @gen.coroutine
        def worker():
            while True:
                yield fetch_url()

        for param in self.params:
            yield self._q.put(param)

        for _ in range(self.concurrency):
            worker()
        yield self._q.join(timeout=timedelta(seconds=300))   
        assert self._fetching == self._fetched
        print('POST完成共用： %d 秒, 完成请求POST次数: %s.' % (time.time() - start, len(self._fetched)))

    def post(self):
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._run)


def main():
    url ='http://httpbin.org/post' 
    params = ["a=1",'b=2','c','d','e','f','g']
    s = AsyMethodPostSpider(url, params, 10)
    s.post()

if __name__ == '__main__':
    main()
