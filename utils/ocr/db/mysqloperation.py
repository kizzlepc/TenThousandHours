import configparser
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import models


class MysqlOpration():
    def __init__(self):
        conf = configparser.ConfigParser()
        conf.read("D:\\conf\\mysqlconf.ini", "utf8")
        self.user = conf.get("ent_administrative_punishment_custom_info", "user")
        self.password = conf.get("ent_administrative_punishment_custom_info", "password")
        self.host = conf.get("ent_administrative_punishment_custom_info", "host")
        self.dbname = conf.get("ent_administrative_punishment_custom_info", "dbname")
        self.charset = conf.get("ent_administrative_punishment_custom_info", "charset")

    def get_engine(self):
        conf = []
        conf.append(self.user)
        conf.append(self.password)
        conf.append(self.host)
        conf.append(self.dbname)
        conf.append(self.charset)
        return create_engine('mysql+mysqlconnector://%s:%s@%s/%s?charset=%s'%(*conf,))

    def get_session(self):
        return sessionmaker(bind=self.get_engine())() 
    
    def __str__(self):
        """
        a.调试打印查看对象获取的参数
        """
        return "user=%s;password=%s;host=%s;dbname=%s;charset=%s"%(self.user, self.password, self.host, self.dbname, self.charset)
    
if __name__ == "__main__":
    sql = MysqlOpration()
    session = sql.get_session()
    query = session.query(models.PunishmentTable).filter(models.PunishmentTable.id==13450).first()
    print(query)
    
    
    
    
    