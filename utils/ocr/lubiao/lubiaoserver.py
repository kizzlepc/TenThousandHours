from flask import Flask
from flask import request
from flask import make_response,Response
import json
import base64
import os
import time


os.environ["TF_CPP_MIN_LOG_LEVEL"] = '3'

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Verifying Code Interface. Created by kizzlepc'

@app.route('/ocr', methods=['POST'])
def test():
    print(request.form.to_dict())
    if request.method == 'POST' and request.form.get('project') == 'lubiao': 
        try:
            start_time = time.time()
            base64_string = request.form.to_dict().get('image')
            bin_img = base64.b64decode(base64_string)
            (lambda f,d:(f.write(d),f.close()))(open('example.png', 'wb'), bin_img)
            auto_code = os.popen('python predict_captcha.py example.png').read()
            end_time = time.time()
            resp = json.dumps({"code":auto_code.strip(), "response_time":"%.4ss"%(end_time-start_time)})
            return resp
        except Exception as e:
            err_resp = json.dumps({"error_code":"1002"})
            print(request.form.to_dict())
            print(e)
            return err_resp
    else:
        err_resp = json.dumps({"error_code":"1001"})
        print(request.form.to_dict())
        return err_resp

def run_server():
    """
    a.用flask快速搭建的验证码识别服务器
    """
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='192.168.100.81', port='5000')
       
if __name__ == '__main__':
    #from werkzeug.contrib.fixers import ProxyFix
    #app.wsgi_app = ProxyFix(app.wsgi_app)
    #app.run(host='192.168.100.81', port='5000')
    app.run()
