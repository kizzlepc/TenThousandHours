import configparser
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Integer, DateTime, TEXT
Base = declarative_base()

class HotTable(Base):
    """
    a.工商热搜列表
    """
    __tablename__ = 'business_hot_search_list'

    id = Column(Integer, primary_key=True)
    social_code = Column('social_code', String(64), comment='统一社会信用代码')
    enterprise_name = Column('enterprise_name', String(64), comment='企业名称')
    company_type = Column('company_type', String(32), comment='公司类型')
    legal_person = Column('legal_person', String(16), comment='法定代表人')
    reg_capital = Column('reg_capital', String(32), comment='注册资本')  
    build_date = Column('build_date', DateTime, comment='成立日期')
    period_from = Column('period_from', String(32), comment='营业期限自')
    period_to = Column('period_to', String(32), comment='营业期限至')
    reg_authority = Column('reg_authority', String(32), comment='登记机关')
    approved_date = Column('approved_date', DateTime, comment='核准日期')
    reg_status = Column('reg_status', TEXT, comment='登记状态')
    address = Column('address', String(200), comment='住所')
    range = Column('range', String(800), comment='经营范围')
    province = Column('province', String(100), comment='所在省份')
    create_time = Column('create_time', DateTime, comment='dd创建时间')
    update_date = Column('update_date', DateTime, comment='日期')

    def __str__(self):
        fields_all = dir(HotTable)
        fields = [fields for fields in fields_all if not fields.startswith('_')]
        fields.remove('metadata')
        datas = [getattr(self,field) for field in fields]
        return str(datas)

class MysqlOpration():
    def __init__(self):
        conf = configparser.ConfigParser()
        conf.read("D:\\conf\\mysqlconf.ini", "utf8")
        self.user = conf.get("business_hot_search_list", "user")
        self.password = conf.get("business_hot_search_list", "password")
        self.host = conf.get("business_hot_search_list", "host")
        self.dbname = conf.get("business_hot_search_list", "dbname")
        self.charset = conf.get("business_hot_search_list", "charset")

    @staticmethod
    def get_engine():
        mysql = MysqlOpration()
        conf = []
        conf.append(mysql.user)
        conf.append(mysql.password)
        conf.append(mysql.host)
        conf.append(mysql.dbname)
        conf.append(mysql.charset)
        return create_engine('mysql+mysqlconnector://%s:%s@%s/%s?charset=%s'%(*conf,))

    def get_session(self):
        return sessionmaker(bind=get_engine())() 
    
    def __str__(self):
        """
        a.调试打印查看对象获取的参数
        """
        return "user=%s;password=%s;host=%s;dbname=%s;charset=%s"%(self.user, self.password, self.host, self.dbname, self.charset)
    
if __name__ == "__main__":
    obj = MysqlOpration()
    print(obj)
    Base.metadata.create_all(MysqlOpration.get_engine())
    exit()
    sql = MysqlOpration()
    session = sql.get_session()
    query = session.query(models.HotTable).filter(models.HotTable.id==13450).first()
    print(query)
    
    
    
    
    