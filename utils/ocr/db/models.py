from sqlalchemy import create_engine, Column, String, Integer, DateTime, TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PunishmentTable(Base):
    """
    a.工商异常公告表
    """
    __tablename__ = 'ent_administrative_punishment_custom_info'

    id = Column(Integer, primary_key=True)
    custom_name = Column('custom_name', String(200), comment='海关名称')
    name = Column('name', String(200), comment='当事人')
    address = Column('address', String(300), comment='企业地址')
    legal_person = Column('legal_person', String(200), comment='法人')
    reg_id = Column('reg_id', String(100), comment='海关注册编号')
    id_type = Column('id_type', String(200), comment='证件类型')
    id_num = Column('id_num', String(50), comment='证件号码')
    book_number = Column('book_number', String(200), comment='行政处罚决定书文号')
    custom_name_dept = Column('custom_name_dept', String(255), comment='作出处罚决定的海关名称')
    punishment_date = Column('punishment_date', DateTime, comment='行政处罚作出日期')
    content = Column('content', TEXT, comment='处罚决定书全文')
    title = Column('title', String(200), comment='标题')
    attachment_path = Column('attachment_path', String(800), comment='附件路径')
    attachment_type = Column('attachment_type', String(200), comment='附件类型')
    province = Column('province', String(200), comment='所属省份')
    create_time = Column('create_time', DateTime, comment='创建时间')
    update_time = Column('update_time', DateTime, comment='修改时间')
    data_status = Column('data_status', Integer, comment='数据当前状态（1 已采集 2 已清洗 3 已检查 4 已成功）')
    url = Column('url', String(200), comment='网页链接') 

    def __str__(self):
        fields_all = dir(PunishmentTable)
        fields = [fields for fields in fields_all if not fields.startswith('_')]
        fields.remove('metadata')
        datas = [getattr(self,field) for field in fields]
        return str(datas)