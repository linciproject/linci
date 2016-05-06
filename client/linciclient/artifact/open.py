#! /usr/bin/env python
#coding=utf-8

from linciclient import LinciClient, log
import sys
import json

ERR_BAD_PARAM = 1
ERR_FAIL_TO_CREATE = 2
ERR_FAIL_TO_OPEN = 3

class LinciArtifactClient(LinciClient):
    def main(self):
        from optparse import OptionParser

        parser = OptionParser()
        parser.add_option('--context-file', dest='context_file', default='.linci_artifact_context', help='context file path for linci artifact operation, default is .linci_artifact_context')
        parser.add_option('--new','-n', dest='new', default=False, action='store_true', help='create new artifact')
        parser.add_option('--artifact-id','--aid', dest='artifact_id', default=None, help='artifact id of which to open')

        self.options, args = parser.parse_args()

        contextd = {
            "aid" : None
        }

        def _exit(ret):
            with open(self.options.context_file,"wb") as f:
                json.dump(contextd,f,indent=2)
            sys.exit(ret)

        if self.options.new:
            data = {}
            if self.options.artifact_id:
                try:
                    asite, aindex = self.options.artifact_id.split("-")
                    aindex = int(aindex)
                    data["asite"]=asite
                    data["aindex"]=aindex
                except ValueError as e:
                    log.error("wrong artifact id: %s, should be 'ASITE-AINDEX', AINDEX should be integer, for example 'EXAMPLE-1'"%(self.options.artifact_id))
                    _exit(ERR_BAD_PARAM)

            r = self.request_post("linci/artifact/api_new",data=data)
            if r.status_code==200:
                rjson = r.json()
                success = rjson.get("success")
                if success:
                    aid = rjson["aid"]
                    contextd["aid"] = aid
                    log.info("create a new artifact: %s"%(aid))
                else:
                    log.error("create new artifact fail, return error message: '%s'"%(rjson.get("msg")))
                    _exit(ERR_FAIL_TO_CREATE)
            else:
                log.error("create new artifact fail, return status code :%s ,text: %s"%(r.status_code,r.text))
                _exit(ERR_FAIL_TO_CREATE)
        else:
            if self.options.artifact_id:
                r = self.request_post("linci/artifact/api_get",data={"aid":self.options.artifact_id})
                if r.status_code==200:
                    rjson = r.json()
                    success = rjson.get("success")
                    if success:
                        log.info("open %s successfully"%(self.options.artifact_id))
                        contextd["aid"] = self.options.artifact_id
                    else:
                        log.error("open artifact fail, return error message: '%s'"%(rjson.get("msg")))
                        _exit(ERR_FAIL_TO_OPEN)
                else:
                    log.error("open artifact fail, return status code :%s ,text: %s"%(r.status_code,r.text))
                    _exit(ERR_FAIL_TO_OPEN)
            else:
                log.error("if you want to create new, you should use --new, if you want to open existing artifact, you should use --artifact-id")
                _exit(ERR_BAD_PARAM)
        _exit(0)

def main():
    c = LinciArtifactClient()
    c.main()

if __name__ == '__main__':
    main()
