#!/usr/bin/env python

###########################################
# Description:
#   Backup vm  tags = backup
############################################

import sys, time
import XenAPI
import commands
import datetime
import os
import re
import multiprocessing
from XenBackup import XenBackup

hostfqdn = "10.0.6.90"
username = "root"
password = "omega1"
backuppath = "/xenimages"
notifymail = "support@prodosec.com"
vms = [] #all backup vm here
tag_label = "wutest" # match vm tags

frommail = "no-reply@prodosec.com"
logpath = "/var/xenbackup"


def create_backuppath():
    global backuppath
    # create backup directory
    now = datetime.datetime.now()
    backuppath = backuppath + "/" + now.strftime("%Y-%m-%d")
    cmd = "/bin/mkdir " + backuppath
    print cmd
    print backuppath
    commands.getstatusoutput(cmd)

def main():

    create_backuppath()

    # clear log files
    #cmd = "/bin/rm -rf " + logpath + "/*"
    #commands.getstatusoutput(cmd)

    # put vm list in array vms
    url = "http://" + hostfqdn
    session = XenAPI.Session(url)
    session.xenapi.login_with_password(username, password)
    all = session.xenapi.VM.get_all()
    for vm in all:
        record = session.xenapi.VM.get_record(vm)
        if tag_label in record["tags"]:
            #print "%s:tag:%s" % (record["name_label"], record["tags"])
            vms.append(record["name_label"])
    session.xenapi.session.logout()

    #backup each single vm
    # mutiple process, max mp = 4 
    mp = 3
    print "total number of vm: %s" % (len(vms),)
    for i in range(0, len(vms), mp):


        p = multiprocessing.Process(name='daemon', target=daemon, args=(vms[i],))
        p.daemon = True
        p.start()



	###################################################

        mp1.join()
        if (i+1) < len(vms):
            mp2.join()

        if (i+2) < len(vms):
            mp3.join()

        if (i+3) < len(vms):
            mp4.join()

def daemon(vm_label):

    global hostfqdn, username, password, backuppath, frommail, notifymail, logpath, tag_label

    try:
        print "haha%s" % (vm_label)
        backup1 = XenBackup(hostfqdn, username, password, vm_label, backuppath, frommail, notifymail, logpath, tag_label)
    except Exception, e:
        print "FATAL ERROR: " + str(e)

if __name__ == "__main__":
    main()


