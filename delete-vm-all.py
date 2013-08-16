#!/usr/bin/env python

###########################################
# Description:
#   Backup vm  tags = backup
############################################

import sys, time
import XenAPI
import re
import commands
import os
from XenBackup import XenBackup

hostfqdn = "10.0.6.200"
username = "root"
password = "haha"
backuppath = "/xenimages"
notifymail = "support@prodosec.com"
vms = [] #all backup vm here
tag_label = "pbx" # match vm tags
#tag_label = "wutest" # match vm tags

frommail = "no-reply@prodosec.com"
#logpath = "/var/xenbackup"

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
        print "%s:tag:%s" % (record["name_label"], record["uuid"])
        #vms.append(record["uuid"])
        session.xenapi.VM.destroy(vm)
session.xenapi.session.logout()


