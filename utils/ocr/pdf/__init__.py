import os
import requests
from ocr.pdf import PDFUtils

class PDFHandler():
    """
    a处理pdf格式文件，转换成文本格式
    """
    def __init__(self):
        # 根据文件中或数据库中的id来标识下载的文件
        self.dbID = 0
        self.filePath = '' 
        self.basePath = os.path.dirname(os.path.abspath(__file__))
        self.pdfPath = os.path.join(self.basePath, 'pdfdir')
        if not os.path.exists(self.pdfPath):os.mkdir(self.pdfPath)

    def Inet_download_PDF(self, pdfUrl, dbID):
        """
        a下载pdf
        """
        res = requests.get(pdfUrl)
        self.dbID = dbID
        self.filePath = os.path.join(self.pdfPath, '%s.pdf'%str(dbID))
        (lambda f,d:(f.write(d), f.close()))(open(self.filePath, 'wb'), res.content)
        return res
        
    def pdf2img(self):
        PDFUtils.pdf_to_img(self.filePath, self.dbID)
        
    def parse(self, pdfUrl, dbID):
        self.Inet_download_PDF(pdfUrl, dbID)
        self.pdf2img()
        
if __name__ == "__main__":
    pdf = PDFHandler()
    pdfUrl = "http://beijing.customs.gov.cn/Portals/159/行政处罚/2017-221.pdf"
    pdf.parse(pdfUrl, 'result')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    