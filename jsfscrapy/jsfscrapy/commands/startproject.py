import os
import string
import re
from os.path import join, exists, abspath
# shutil模块高级文件操作
from shutil import ignore_patterns, copy2, copystat, move
from importlib import import_module
from jsfscrapy.commands import ScrapyCommand
from jsfscrapy.exceptions import UsageError
from jsfscrapy.utils.template import render_templatefile, string_camelcase
import jsfscrapy

#替换生存路径
TEMPLATES_TO_RENDER = (
    ('scrapy.cfg',),
    ('${project_name}', 'settings.py.tmpl'),
    ('${project_name}', 'items.py.tmpl'),
    ('${project_name}', 'piplines.py.tmpl'),
    ('${project_name}', 'middlewares.py.tmpl'),
    )

#指定需要忽略的后缀名
IGNORE = ignore_patterns('*.pyc', '.svn')


class Command(ScrapyCommand):
    default_settings = {
        'LOG_ENABLED': False,
        'SPIDER_LOADER_WARN_ONLY': True}
    
    def syntax(self):
        return "<project_name>[project_dir]"
    
    def short_desc(self):
        return "Create new project"
    
    def _is_valid_name(self, project_name):
        #检查项目名是否和模块名重名
        def _module_exists(module_name):
            try:
                #使用模块加载
                import_module(module_name)
                return True
            except ImportError:
                return False
        #检查是否符合命名规范：下划线或大小写字母开头的任意包含字母数字和下划线的名字    
        if not re.search(r'^[_a-zA-Z]\w*$', project_name):
            print('Error:Project names must begin with a letter and contain'\
                  ' only\nletters, numbers and underscores.')
        elif _module_exists(project_name):
            print('Error:Module %r already exists'%project_name)
        else:
            return True
        return False

    #从源文件夹中复制需要的文件到目标文件夹中，忽略指定后缀名的文件
    def _copytree(self, src, dst):
        ignore = IGNORE
        #目录中的文件夹和文件(不递归)
        names = os.listdir(src)
        #指定被忽略后缀的文件
        ignored_names = ignore(src, names)
        
        if not os.path.exists(dst):
            os.makedirs(dst)
        
        for name in names:
            #跳过需要忽略的文件
            if name in ignored_names:
                continue
            
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            print()
            if os.path.isdir(srcname):
                self._copytree(srcname, dstname)
            else:
                copy2(srcname, dstname)
        copystat(src, dst)
        
    def run(self, args, opts):
        if len(args) not in (1,2):
            raise UsageError()
        
        project_name = args[0]
        project_dir = args[0]
        
        if len(args) == 2:
            project_dir = args[1]
        
        #通过判断scrapy.cfg文件是否存在，来判断项目是否已经存在
        if exists(join(project_dir, 'scrapy.cfg')):
            self.exitcode = 1
            print('Error:scrapy.cfg already exists in %s'%abspath(project_dir))
            return 
        
        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return
        
        self._copytree(self.templates_dir, abspath(project_dir))
        move(join(project_dir, 'module'), join(project_dir, project_name))
        for paths in TEMPLATES_TO_RENDER:
            path = join(*paths)
            tplfile = join(project_dir, string.Template(path).substitute(project_name=project_name))
            render_templatefile(tplfile, project_name=project_name, ProjectName=string_camelcase(project_name))
        
        print("New Scrapy project %r, using template directory %r, created in:"%\
              (project_name, self.templates_dir))
        print("    %s\n"%abspath(project_dir))
        print("You can start your first spider with:")
        print("    cd %s"%project_dir)
        print("    scrapy genspider example example.com")
        
    #装饰器设置只读属性
    @property
    def templates_dir(self): 
        try:
            _templates_base_dir = self.settings['TEMPLATES_DIR'] or join(jsfscrapy.__path__[0], 'templates')
        except:
            self.settings = {'TEMPLATES_DIR':''}
            _templates_base_dir = self.settings['TEMPLATES_DIR'] or join(jsfscrapy.__path__[0], 'templates')
        return join(_templates_base_dir, 'project')

if __name__ == '__main__':
    com = Command()
    com.run(args=["mydiy",], opts='')