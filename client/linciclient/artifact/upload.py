#! /usr/bin/env python
#coding=utf-8

from linciclient import LinciClient, log
import os
import sys
import json
import re
from fnmatch import translate

ERR_BAD_PARAM = 1
ERR_PATH_NOT_FOUND = 2
ERR_API_FAIL = 3

#http://stackoverflow.com/questions/1025214/with-pythons-optparse-module-how-do-you-create-an-option-that-takes-a-variable
def cb(option, opt_str, value, parser):
    args=[]
    for arg in parser.rargs:
        if arg[0] != "-":
            args.append(arg)
        else:
            del parser.rargs[:len(args)]
            break
    if getattr(parser.values, option.dest):
        args.extend(getattr(parser.values, option.dest))
    setattr(parser.values, option.dest, args)

class LinciArtifactClient(LinciClient):
    def main(self):
        from optparse import OptionParser

        parser = OptionParser()
        parser.add_option('--context-file', dest='context_file', default='.linci_artifact_context', help='context file path for linci artifact operation, default is .linci_artifact_context')
        parser.add_option('--basepath','-b', dest='basepath', default='.', help='base path for files')
        parser.add_option('--include', '-i', dest='include', default=None, action='callback', callback=cb, help='include pattern')
        parser.add_option('--exclude', '-e', dest='exclude', default=None, action='callback', callback=cb, help='exclude pattern')
        parser.add_option('--dry', dest='dry', default=False, action='store_true', help='dry run')

        options, args = parser.parse_args()

        self.context = {}
        with open(options.context_file) as f:
            self.context = json.load(f)
        if not self.context.get("aid"):
            log.error("err: not open an artifact yet")
            sys.exit(ERR_BAD_PARAM)

        def get_re(arg):
            if arg[0]=='^':
                re_str = arg[1:]
            else:
                re_str = translate(arg)
            return re.compile(re_str)

        include = options.include
        if not include:
            log.error("bad param, no include option")
            sys.exit(ERR_BAD_PARAM)
        if not isinstance(include,list):
            include = [include]
        re_include_list = [get_re(arg) for arg in include]
        exclude = options.exclude or []
        re_exclude_list = [get_re(arg) for arg in exclude]
        def match(fpath):
            for reobj in re_include_list:
                mobj = reobj.search(fpath)
                if mobj:
                    return bool(mobj)
            return False
        def match_exclude(fpath):
            for reobj in re_exclude_list:
                mobj = reobj.search(fpath)
                if mobj:
                    return bool(mobj)
            return False

        for dpath, dnames, fnames in os.walk(options.basepath):
            for fname in fnames:
                fpath = os.path.join(dpath,fname)
                if match(fpath) and (not match_exclude(fpath)):
                    relpath = os.path.relpath(fpath,options.basepath)
                    log.info("uploading to %s: '%s'"%(self.context["aid"],relpath))

                    if not options.dry:
                        fobj = open(fpath,"rb")
                        finfo = (relpath,fobj)
                        r = self.request_post("linci/artifact/api_upload",
                            data={"aid":self.context["aid"]},
                            files={"file":finfo}
                        )
                        if r.status_code==200:
                            rjson = r.json()
                            if rjson.get("success"):
                                log.info("file %s upload successfully, message: %s"%(fpath,rjson.get("msg")))
                            else:
                                log.error("file %s fail to upload, message: %s"%(fpath,rjson.get("msg")))
                                sys.exit(ERR_API_FAIL)
                        else:
                            log.error("file %s fail to upload, http code: %s"%(fpath,r.status_code))
                            sys.exit(ERR_API_FAIL)

def main():
    c = LinciArtifactClient()
    c.main()

if __name__ == '__main__':
    main()
