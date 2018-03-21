import requests

splash_url = 'http://192.168.100.81:8050'
target_url = 'http://bj.gsxt.gov.cn/'
wait = 5
url = '%s/render.html?url=%s&wait=%s'%(splash_url, target_url, wait)

res = requests.get(url)
print(res.text)