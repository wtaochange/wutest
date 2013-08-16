#!/usr/bin/env python

import os, glob
import re, commands
import smtplib
from email.mime.text import MIMEText
import sys, time
import datetime
import XenAPI

hostfqdn = "10.0.6.100"
username = "root"
password = "haha"
vms = [] #all backup vm here
backup_path = "/xenbackup/pbx/backup"
restore_path = "/xenbackup/pbx/restore"
textfile = "/tmp/log"


def logger(line):
    FILE = open(textfile,"a")
    FILE.write(line)
    FILE.write("\n")
    FILE.write("timestamp ==> " + get_time())
    FILE.write("\n\n")
    FILE.close()

def get_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def mail():
    fp = open(textfile, 'rb')
    msg = MIMEText(fp.read())
    fp.close()

    from_mail = "no-reply@prodosec.com"
    to_mail = "wu@prodosec.com"

    msg['Subject'] = 'Pbx restore '
    msg['From'] = from_mail
    msg['To'] = to_mail

    s = smtplib.SMTP("localhost")
    s.sendmail(from_mail, to_mail, msg.as_string())
    s.quit()

def del_copy(file, vm_label):
    # put vm list in array vms
    url = "http://" + hostfqdn
    session = XenAPI.Session(url)
    session.xenapi.login_with_password(username, password)

    # import machine now
    cmd = "/usr/local/bin/curl -T " + restore_path + "/\"" + file + "\" http://" + username +":"+password+"@" + hostfqdn + "/import?restore=true "
    logger(cmd)
    commands.getstatusoutput(cmd)

    # delete file after import
    #os.remove(restore_path + '/' + file)


if __name__ == "__main__":

    # kill the old process, which possilbe phantom
    # os.getpid()
 
    # move files to restore directory
    cmd = "/bin/mv " + backup_path + "/*.xva " + restore_path
    commands.getstatusoutput(cmd)


    # create log file
    FILE = open(textfile, "w")
    #FILE.write("Start ==> " + get_time())
    FILE.write("\n")
    FILE.close()

    for file in os.listdir(restore_path):
        if glob.fnmatch.fnmatch(file, "*.xva"):
            m = re.search('^(\d{1,3}\.){3}\d{1,3}(.*)\.xva', file).groups()
            vm_label = m[1]
            del_copy(file, vm_label)

    # write timestamp
    FILE = open(textfile, "a")
    #FILE.write("End ==> " + get_time())
    FILE.write("\n")
    FILE.close()

    # send mail
    mail();
