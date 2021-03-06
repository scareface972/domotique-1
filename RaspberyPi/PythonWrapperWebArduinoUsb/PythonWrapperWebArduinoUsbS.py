#!/usr/bin/python
# -*- coding: utf-8 -*-

#import socket
import xmlrpclib
import logging
import os
from optparse import OptionParser

#class Command:
#    """A simple command"""
#    
#    def __init__(self):
#        self.idTo = ""
#        self.idFrom = ""
#        self.message = ""
#        self.speak = ""
#        self.isReadOrWrite = ""
#        
#    def dumpAsString(self):
#        if(self.speak == "test"):
#            return  "MSG:" + self.message + "_ORIGIN:" + self.idFrom +"_"+self.isReadOrWrite
#        else:
#            return "MSG:999" + self.message + "_ORIGIN:" + self.idFrom +"_"+self.isReadOrWrite

parser = OptionParser(usage="usage: %prog [options]",version="%prog 1.0")
parser.add_option("-p", "--port",action="store",dest="aPortToUse",default="50007",help="the port to listen")
parser.add_option("-s", "--send",action="store",dest="aMsgToSend",default="20",help="Command to send to Arduino Leonardo")
parser.add_option("-o", "--originator",action="store",dest="aOriginator",default="UNKNOW",help="Originator of the request")
parser.add_option("-t", "--type",action="store",dest="aCmdType",default="WRITE",help="Write or Read command")
(options, args) = parser.parse_args()

#Create a unique ID
aProcessId = str(os.getpid())

#The logging API 
logging.basicConfig(filename='/home/pi/Usb_Arduino_Leonardo/PythonWrapperWebArduinoUsbS.log',level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('Daemon starting with pid : ' + aProcessId + " and string is : " + options.aMsgToSend + " and command type is : " + options.aCmdType)

# There is 2 possibilities to communicate with the server
# 1/ We send a string on TCP port. String format is like :
# aMsgToSend2 = "MSG:" + options.aMsgToSend + "_ORIGIN:" + options.aOriginator
# 2/ We use RPC 
# 2/ is much more simple since there is no string to parse but I kept 1/ as backup if needed later
#aCmdToSend = Command()
#aCmdToSend.message = options.aMsgToSend
#aCmdToSend.idFrom = options.aOriginator
#aCmdToSend.speak = options.aSpeakStrings
#aCmdToSend.isReadOrWrite = options.aCmdType
#aMsgToSend2 = aCmdToSend.dumpAsString()
#aMsgToSend2 = "READ"
#HOST = ''
#PORT = int(options.aPortToUse)
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST, PORT))
#s.send(aMsgToSend2)
#data = s.recv(1024)
#s.close()
#print(repr(data))

s2 = xmlrpclib.Server('http://localhost:49007/')
if(options.aCmdType == "READ"):
    print (repr(s2.readDeviceStatus(options.aMsgToSend)))
elif(options.aCmdType == "WRITE"):
    print (s2.sendCommand(options.aMsgToSend,options.aOriginator))
elif(options.aCmdType == "SPEAK"):
    logging.info('SPEAK command with : ' + str(options.aMsgToSend))
    print (s2.translateVocalAction(str(options.aMsgToSend)))
else:
    print("Unknow command")

logging.info('Daemon finish with pid : ' + aProcessId)
