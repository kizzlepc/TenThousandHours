# optparse模块功能强大，而且易于使用，可以方便的生成标准的、符合Unix/Posix规范的命令行说明。
from optparse import OptionGroup


class ScrapyCommand(object):
    requires_project = False
    crawler_process = None
    
    default_settings = {}
    
    exitcode = 0
    
    def __init__(self):
        self.settings = None
        
    def set_crawler(self, crawler):
        assert not hasattr(self, '_crawler'), "crawler already set"
        self._crawler = crawler
        
    def syntax(self):
        return ""
    
    def short_desc(self):
        return ""
    
    def long_desc(self):
        return self.short_desc()
    
    def help(self):
        return self.long_desc()
    
    def add_options(self, parser):
        group = OptionGroup(parser, "Global Options")
        group.add_option("--logfile", metavar="FILE", default=None,
            help="log file. if omitted stderr will be used")
        group.add_option("-L", "--loglevel", metavar="LEVEL", default=None,
            help="log level(default:%s)"%self.settings["LOG_LEVEL"])
        group.add_option("--nolog", action="store_true", 
            help="disable logging completely")
        group.add_option("--profile", metavar="FILE", default=None,
            help="write python cProfile stats to FILE")
        group.add_option("--pidfile", metavar="FILE",
            help="write process id to FILE")
        group.add_option("-s", "--set", action="append", default=[], metavar="NAME=VALUE",
            help="set/override setting(may be repeated)")
        group.add_option("--pdb", action="store_true",
            help="enable pdb on failure")
        
        parser.add_option_group(group)
        
    def process_options(self, args, opts):
        pass
    
    def run(self, args, opts):
        return NotImplementedError