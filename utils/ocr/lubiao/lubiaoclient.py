import requests
import base64


def get_code(fileName):
    """
    a.客户端发送图片，接收识别结果
    """
    #url = 'http://192.168.100.81:5000/ocr'
    url = 'http://127.0.0.1:5000/ocr'
    f = open(fileName,'rb')
    base64_string = base64.b64encode(f.read()).decode('utf8') 
    f.close()
    data = {
        "project":'lubiao',
        "image":base64_string,
    }
    res = requests.post(url, data=data)
    print(res.text)

if __name__ == '__main__':
    #get_code('52xf.jpg')
    get_code('35n7.jpg')
    #get_code('captcha.jpg')