# -*- coding: utf-8 -*-
import configparser

class YouTuOcr():
    def __init__(self):
        """
                        从配置文件中加载敏感数据
        """
        conf = configparser.ConfigParser()
        conf.read("D:\\conf\\youtuocr.ini", "utf8")
        self.u = conf.get("USERINFO", "u")
        self.a = conf.get("USERINFO", "a")
        self.k = conf.get("USERINFO", "k")
        self.SecretKey = conf.get("USERINFO", "SecretKey")
    
    def __str__(self):
        return "u=%s;a=%s;k=%s;secretKey=%s"%(self.u, self.a, self.k, self.SecretKey)

if __name__ == '__main__':
    yto = YouTuOcr()
    print(yto)
