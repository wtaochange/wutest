#!/usr/bin/pyton

###########################################
# File      :  XenError.py
# Project   :  Xen Server Backup
# Author    :  Lauro Frei
#
# Created   :  november'10
#
# Copyright :  Raptus AG
#
# Description:
#   This does some error handling and 
#   notifying
#
############################################

import logging
import datetime
import smtplib
import string
import re
import os
import sys
import logging
from email.mime.text import MIMEText

class XenError(object):

	logger = None
	logfile = None

	frommail = None
	notifymail = None
	logpath = "/var/log/xenbackup"


	def __init__(self, notifymail, frommail, logpath, filename):

		self.setLogPath(logpath)	

                if not(os.path.exists(self.logpath)):
                        os.mkdir(self.logpath)

                self.logfile = self.logpath + "/" + filename
                self.logger = logging.getLogger("xenBackup")
                self.logger.setLevel(logging.INFO)
                fh = logging.FileHandler(filename=self.logfile)
                fh.setLevel(logging.INFO)
                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

                fh.setFormatter(formatter)
                self.logger.addHandler(fh)
		
		self.setNotifyMail(notifymail)
		self.setFromMail(frommail)



	def info(self, desc):

		self.logger.info(desc)



	def error(self, desc, e):

		self.logger.error(desc + " - Details: " + str(e))
		self.sendConclusion()
		raise Exception(desc + " - Details: " + str(e))



	def sendConclusion(self):

		try:
			fp = open(self.logfile, "rb")
	                msg = MIMEText(fp.read())
        	        fp.close()

			if self.frommail == None:
				self.frommail = "backuper@xenserver.local"

	                msg["Subject"] = "Backup %s" % self.logfile
        	        msg["From"] = self.frommail
                	msg["To"] = self.notifymail

	                s = smtplib.SMTP("localhost")
        	        s.sendmail(self.frommail, self.notifymail, msg.as_string())
                	s.quit()

		except Exception, e:
			self.logger.error("Failed to send notification email! - Details: " + str(e))
			raise Exception("Failed to send notification email! - Details: " + str(e))





# setters

        def setNotifyMail(self, notifymail):

                if re.search('(\w+@\w+(?:\.\w+)+)(?(1))', notifymail):
                        self.notifymail = notifymail

                else:
                        self.error("setNotifyMail: not a valid email-address!", "")


        def setLogPath(self, logpath):

                if len(logpath) > 1:

			if logpath[-1] == "/":
				logpath = logpath[0:-1]

                        if not os.path.exists(logpath):
                                os.mkdir(logpath)

                        self.logpath = logpath

                else:
                        raise Exception('setLogPath: no valid path!')


        def setFromMail(self, frommail):

                if re.search('(\w+@\w+(?:\.\w+)+)(?(1))', frommail):
                        self.frommail = frommail

                else:
                        self.error("setFromMail: not a valid email-address!", "")


# eof
