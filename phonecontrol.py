#!/usr/bin/python

"""
Stop the music when Snom IP phone rings
https://service.snom.com/display/wiki/Action+URLs

Requires Python 2
"""


import BaseHTTPServer,os

class PhoneStatus():
    status={}
    def process_update(this,k):
        if k=='/offhook':
            this.status['hook']='off'
        elif k=='/onhook':
            this.status['hook']='on'
        elif k=='/connect':
            this.status['connect']='on'
        elif k=='/disconnect':
            this.status['connect']='off'

            

    def set_mixer(this):
        if 'connect' in this.status:
            if this.status['connect']=='on':
                os.system('amixer sset PCM 0')
            elif this.status['connect']=='off':
                os.system('amixer sset PCM 215')

        
global myPhoneStatus
myPhoneStatus = PhoneStatus()
        
class ControlHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(arg):
        myPhoneStatus.process_update(arg.path)
        myPhoneStatus.set_mixer()
    

def run_while_true():

    
    server_address = ('', 9999)
    httpd = BaseHTTPServer.HTTPServer(server_address, ControlHandler)
    while 1:
        httpd.handle_request()

run_while_true()
