import logging  
import time  
from logging.handlers import TimedRotatingFileHandler  
import random
# hadoop项目，自动模拟生成nginx日志

def create_logger():
    logFilePath = "D:\\log\\access_log"  
    logger = logging.getLogger("YouLoggerName")  
    logger.setLevel(logging.INFO)  
    
    handler = TimedRotatingFileHandler(logFilePath,  
                                       when="m",  
                                       interval=5,  
                                       backupCount=7)  
    
    
    formatter = logging.Formatter('%(message)s')  
      
    handler.setFormatter(formatter)  
      
    logger.addHandler(handler)  
    return logger
 
if __name__ == '__main__':
    logger = create_logger()
    msgs,_ = (lambda f:(f.readlines(), f.close()))(open('access.log.fensi'))
    for msg in msgs:
        logger.info(msg.strip())
        time.sleep(random.randint(0,3))
    
    
    
    
    