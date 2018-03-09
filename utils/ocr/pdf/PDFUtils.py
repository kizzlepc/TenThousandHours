from wand.image import Image
import os
from ocr.youtuocr import YouTuOcr


def pdf_to_img(infile, newname):
    # 将pdf文件转为jpg图片文件
    # ./PDF_FILE_NAME 为pdf文件路径和名称
    image_pdf = Image(filename=infile,resolution=300)
    image_jpeg = image_pdf.convert('jpg')
    img_list = join_img_list(image_jpeg)
    img_to_save(img_list, infile, newname)

def join_img_list(image_jpeg): 
    # wand已经将PDF中所有的独立页面都转成了独立的二进制图像对象。我们可以遍历这个大对象，并把它们加入到req_image序列中去。
    req_image = []
    for img in image_jpeg.sequence:
        img_page = Image(image=img)
        req_image.append(img_page.make_blob('jpg'))
    return req_image
  
def img_to_save(imgs, infile, newname):  
    # 遍历req_image,保存为图片文件
    dirpath = os.path.dirname(infile)
    i = 0
    for img in imgs:
        img_name = os.path.join(dirpath, "%s_%s.jpg"%(str(newname), str(i)))
        txt_name = os.path.join(dirpath, "%s.txt"%(str(newname)))
        taskimg = open(img_name,'wb')
        taskimg.write(img)
        taskimg.close()
        #img_parse(img_name)
        YouTuOcr().ocr_img_result(img_name, txt_name)
        i += 1
        
        
        
        
        
        