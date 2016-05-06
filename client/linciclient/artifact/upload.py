#! /usr/bin/env python
#coding=utf-8

from linciclient import LinciClient, log
import os
import sys
import json

ERR_PATH_NOT_FOUND = 1
ERR_UPLOAD_FAIL = 2

class LinciArtifactClient(LinciClient):
    def main(self):
        from optparse import OptionParser

        parser = OptionParser()
        parser.add_option('--context-file', dest='context_file', default='.linci_artifact_context', help='context file path for linci artifact operation, default is .linci_artifact_context')
        parser.add_option('--file','-f', dest='file', default=None, help='file path to upload')
        parser.add_option('--server-side-path', dest='server_side_path', default=None, help='file path to upload')

        self.options, args = parser.parse_args()

        with open(self.options.context_file) as f:
            self.context = json.load(f)

        if self.options.file:
            if os.path.isfile(self.options.file):
                fobj = open(self.options.file,"rb")
                if self.options.server_side_path:
                    finfo = (self.options.server_side_path,fobj)
                else:
                    finfo = fobj
                r = self.request_post("linci/artifact/api_upload",
                    data={"aid":self.context["aid"]},
                    files={"file":finfo}
                )
                if r.status_code==200:
                    rjson = r.json()
                    if rjson.get("success"):
                        log.info("file %s upload successfully, message: %s"%(self.options.file,rjson.get("msg")))
                    else:
                        log.error("file %s fail to upload, message: %s"%(self.options.file,rjson.get("msg")))
                        sys.exit(ERR_UPLOAD_FAIL)
                else:
                    log.error("file %s fail to upload, http code: %s"%(self.options.file,r.status_code))
                    sys.exit(ERR_UPLOAD_FAIL)
            else:
                log.error("%s is not a file"%(self.options.file))
                sys.exit(ERR_PATH_NOT_FOUND)

def main():
    c = LinciArtifactClient()
    c.main()

if __name__ == '__main__':
    main()
