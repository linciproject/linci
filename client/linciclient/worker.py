#! /usr/bin/env python
#coding=utf-8

import json
import logging
import httplib
import types

import gevent
from gevent import monkey
from gevent.subprocess import Popen, PIPE
from gevent.queue import Queue
import requests
from requests.exceptions import ConnectionError

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)s %(name)s: %(message)s',
                datefmt='%y%m%d%H%M%S')
log = logging.getLogger('worker')

monkey.patch_socket()

class Worker(object):
    def __init__(self):
        self.jobs = {}
        self.wait_secs = 10
        self.pipe_connected = False
    def worker_pipe(self):
        while 1:
            try:
                r = requests.get('%s/job/api_worker_pipe?worker_name=%s'%(self.options.master_base_url,self.options.worker_name), stream=True)
                if r.status_code !=200:
                    self.wait_secs = 5
                    log.error("response not 200: %s, wait %d seconds"%(r,self.wait_secs))
                else:
                    for line in r.iter_lines():
                        # filter out keep-alive new lines
                        if not line:
                            log.debug("keep alive new line")
                        else:
                            msg = json.loads(line)
                            log.info("receive msg: %s"%(msg))
                            if msg.has_key("method"):
                                mname = "method_%s"%(msg["method"])
                                func = getattr(self,mname)
                                if isinstance(func,types.UnboundMethodType):
                                    func(**msg)
                                else:
                                    log.error("discard unknown msg: %s"%(msg))
                            if not self.pipe_connected:
                                break

            except httplib.IncompleteRead as e:
                self.wait_secs = 1
                log.error("err: %s,it seems lost connection of server, wait %d seconds"%(e,self.wait_secs))

            except (ConnectionError,ValueError) as e:
                self.wait_secs = 20
                log.error("err: %s, wait %d seconds"%(e,self.wait_secs))
            
            gevent.sleep(self.wait_secs)
    
    def method_pipe_connect(self,success,errmsg="",*args,**kwargs):
        print "method_pipe_connect",success,errmsg
        self.pipe_connected = bool(success)
        if not success:
            log.error("connect fail,err:'%s' ,wait %d seconds"%(errmsg,self.wait_secs))
            self.wait_secs = 5
    
    def method_job(self,job,*args,**kwargs):
        log.info("spawn a job")
        gevent.spawn(self.do_job,msg["job"])
    
    def do_job(self,jobid,props,*args,**kwargs):
        log.info("do job: %s"%(job))
        if props:
            props = json.loads(props)
        else:
            props = {}

        payload = {"id":jobid,"status":"building"}
        r = requests.post('%s/api/job'%(self.options.master_base_url),data=payload)
        log.info("update job %s status,result:%s"%(jobid,r))

        if props.has_key("steps"):
            steps = props["steps"]
            for step in steps:
                if step.has_key("shell"):
                    shell = step["shell"]
                    log.info("shell: %s"%(shell[:256]))
                    sub = Popen([shell], stdout=PIPE, stderr=PIPE, shell=True)

                    stdio_q = Queue()
                    def handle_stdout():
                        for l in sub.stdout:
                            stdio_q.put_nowait((0,l))
                    def handle_stderr():
                        for l in sub.stderr:
                            stdio_q.put_nowait((1,l))
                    def handle_stdio_q():
                        #stdout 0 stderr 1 extra 2 end 255
                        current_text_type = None
                        stdio_list = []
                        need_flush = False
                        timeout = None
                        while 1:
                            ttype,text = stdio_q.get()
                            if ttype!=current_text_type and len(stdio_list)>0:
                                need_flush = True
                            if len(stdio_list)>50:
                                need_flush = True
                            if need_flush:
                                text2flush = "".join(stdio_list)
                                payload = {"id":jobid,"text_type":current_text_type,"stdio_text":text2flush}
                                r = requests.post('%s/api/job'%(self.options.master_base_url),data=payload)
                                need_flush = False
                            if ttype==255:
                                break
                            current_text_type = ttype
                            stdio_list.append(text)
                    glet_stdout = gevent.spawn(handle_stdout)
                    glet_stderr = gevent.spawn(handle_stderr)
                    glet_stdio_q = gevent.spawn(handle_stdio_q)

                    sub.wait()
                    stdio_q.put_nowait((255,""))
                    glet_stdout.kill()
                    glet_stderr.kill()

        payload = {"id":jobid,"status":3}#JOB_STATUS_FINISHED
        r = requests.post('%s/api/job'%(self.options.master_base_url),data=payload)
        log.info("update job %d status,result:%s"%(jobid,r))

    def main(self):
        from optparse import OptionParser

        parser = OptionParser()
        parser.add_option('-m','--master', dest='master_base_url', default="http://localhost:8000/linci", help="master base url")
        parser.add_option('--worker', dest='worker_name', default="worker1", help="worker name")

        self.options, self.args = parser.parse_args()

        glet_worker_pipe = gevent.spawn(self.worker_pipe)
        gevent.joinall([glet_worker_pipe])

def main():
    worker = Worker()
    worker.main()


if __name__ == '__main__':
    main()