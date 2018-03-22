import logging  
import time  
import configparser   
from logging.handlers import TimedRotatingFileHandler  


logFilePath = "D:\\log\\timed_test.log"  
logger = logging.getLogger("YouLoggerName")  
logger.setLevel(logging.INFO)  

# 每隔1分钟生成一个log文件，最多保存7个
handler = TimedRotatingFileHandler(logFilePath,  
                                   when="m",  
                                   interval=1,  
                                   backupCount=7)  

formatter = logging.Formatter('%(message)s')  
  
handler.setFormatter(formatter)  
  
logger.addHandler(handler)  

for i in range(6000):  
    logger.info("This is a test!")  
    time.sleep(3)  