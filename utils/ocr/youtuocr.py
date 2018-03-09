# -*- coding: utf-8 -*-
import configparser
import math
import time
import hmac, hashlib
import base64
import json
import random
import requests
import codecs
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用SSL认证安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class YouTuOcr():
    """
    b.调用第三方通用OCR识别API
    """
    def __init__(self):
        """
        a.从配置文件中加载敏感数据
        """
        conf = configparser.ConfigParser()
        conf.read("D:\\conf\\youtuocr.ini", "utf8")
        self.u = conf.get("USERINFO", "u")
        self.a = conf.get("USERINFO", "a")
        self.k = conf.get("USERINFO", "k")
        self.secret_key = conf.get("USERINFO", "SecretKey")
        self.url = conf.get("INTERFACE", "url")
        self.host = conf.get("INTERFACE", "host")
        self.content_type = conf.get("INTERFACE", "content_type")
    
    def app_sign(self, expired=0):
        """
        a.生成调用API需要的签名
        """
        now = int(time.time())
        rdm = random.randint(0, 999999999)
        plain_text = "u=%s&a=%s&k=%s&e=%s&t=%s&r=%s&f="%(self.u, self.a, self.k, str(expired), str(now), str(rdm))
        bin = hmac.new(self.secret_key.encode('utf8'), plain_text.encode('utf8'), hashlib.sha1).digest()
        sign = base64.b64encode(bin+plain_text.encode('utf8'))
        return sign

    def read_file_to_base64string(self, infile):
        """
        a.读取本地待识别的文件，将其转换为base64字符串
        """
        base64_string = ""
        with open(infile, "rb") as f:
            base64_string = base64.b64encode(f.read()).decode('utf8') 
        return base64_string

    def save_result_to_txt(self, result, outfile):
        """
        a.将识别的结果保存到指定的文件中
        """
        (lambda f,d:(f.write(d+' '), f.close()))(codecs.open(outfile, 'a'), result) 
        
    def ocr_img_result(self, infile, outfile):
        """
        a.调用API进行ocr识别
        """
        headers = {
            'Host':self.host,
            'Content-Type': self.content_type,
            'Authorization':self.app_sign(),
        }
        data = {
            "app_id":self.a,
            "image":self.read_file_to_base64string(infile),
        }
        res = requests.post(self.url,headers=headers, data=json.dumps(data), verify=False)
        res.encoding = 'UTF8'
        res_json = json.loads(res.text)
        items =res_json.get('items')
        item_list = [i.get('itemstring') for i in items]
        result = ''.join(item_list)
        self.save_result_to_txt(result, outfile)
        
    def dir_all_ocr(self, dir, outfile):
        """
        a.识别文件夹中的所有图片，识别内容追加到一个指定的文件中
        """
        for root,dirs,files in os.walk(dir):
            for f in files:
                imgs = os.path.join(root, f)
                print(imgs)
                self.ocr_img_result(imgs, outfile)       
        
    def __str__(self):
        """
        a.调试打印查看对象获取的参数
        """
        return "u=%s;a=%s;k=%s;secretKey=%s"%(self.u, self.a, self.k, self.secret_key)

if __name__ == '__main__':
    ocr = YouTuOcr()
    infile = "E:\\001"
    outfile = "E:\\result.txt"
    #ocr.ocr_img_result(infile, outfile)
    ocr.dir_all_ocr(infile, outfile)
    print('完成')
    
