import os
import re
import string

def render_templatefile(path, **kwargs):
    """
    .替换模板tmlp文件的project_name和ProjectName占位符
    """
    with open(path, 'rb') as fp:
        raw = fp.read().decode('utf8')
        
    content = string.Template(raw).substitute(**kwargs)
 
    #复制模板tmlp并删除
    render_path = path[:-len('.tmpl')] if path.endswith('.tmpl') else path
    with open(render_path, 'wb') as fp:
        fp.write(content.encode('utf8'))
    if path.endswith('.tmpl'):
        os.remove(path)
    

CAMELCASE_INVALID_CHARS = re.compile('[^a-zA-Z\d]')
def string_camelcase(string):
    """
    .替换变量名中的各种符号并生成驼峰式命令格式
    """
    return CAMELCASE_INVALID_CHARS.sub('', string.title())