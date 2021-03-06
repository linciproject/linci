#! /usr/bin/env python
#coding=utf-8

from linciclient import LinciClient, log
import sys
import json

ERR_BAD_PARAM = 1
ERR_API_FAIL = 2

class LinciArtifactClient(LinciClient):
    def main(self):
        from optparse import OptionParser

        parser = OptionParser()
        parser.add_option('--context-file', dest='context_file', default='.linci_artifact_context', help='context file path for linci artifact operation, default is .linci_artifact_context')

        options, args = parser.parse_args()

        self.context = {}
        with open(options.context_file) as f:
            self.context = json.load(f)
        if not self.context.get("aid"):
            log.error("err: not open an artifact yet")
            sys.exit(ERR_BAD_PARAM)

        r = self.request_post("linci/artifact/api_fix",
            data={"aid":self.context["aid"]},
        )
        if r.status_code==200:
            rjson = r.json()
            if rjson.get("success"):
                log.info("%s fix successfully, message: %s"%(self.context["aid"],rjson.get("msg")))
            else:
                log.error("%s fail to fix, message: %s"%(self.context["aid"],rjson.get("msg")))
                sys.exit(ERR_API_FAIL)
        else:
            log.error("%s fail to fix, http code: %s"%(self.context["aid"],r.status_code))
            sys.exit(ERR_API_FAIL)

def main():
    c = LinciArtifactClient()
    c.main()

if __name__ == '__main__':
    main()
