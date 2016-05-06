#! /usr/bin/env python
#coding=utf-8

from linciclient import LinciClient, log
import os
import sys
import json

ERR_NOT_OPENED = 1

class LinciArtifactClient(LinciClient):
    def main(self):
        from optparse import OptionParser

        parser = OptionParser()
        parser.add_option('--context-file', dest='context_file', default='.linci_artifact_context', help='context file path for linci artifact operation, default is .linci_artifact_context')

        self.options, args = parser.parse_args()

        if os.path.isfile(self.options.context_file):
            with open(self.options.context_file) as f:
                self.context = json.load(f)
            log.info("close artifact: %s"%(self.context.get("aid")))
            os.remove(self.options.context_file)
        else:
            log.error("not artifact opened to be closed")
            sys.exit(ERR_NOT_OPENED)

def main():
    c = LinciArtifactClient()
    c.main()

if __name__ == '__main__':
    main()
