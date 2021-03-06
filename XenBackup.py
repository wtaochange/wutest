#!/usr/bin/pyton

###########################################
# File      :  XenBackup.py
# Project   :  Xen Server Backup
# Author    :  Lauro Frei
#
# Created   :  november'10
#
# Copyright :  Raptus AG
#
# Description:
#   this is the backend for the Xen Server
#   backup script.
#
############################################

import os, sys, time
import XenAPI
import logging
import datetime
import smtplib
import base64
import string
import urllib2
import re
from email.mime.text import MIMEText

from XenError import XenError

class XenBackup(object):

	# DEFAULT VALUES
	session = None
	xenerror = None
	
	hostfqdn = None	
	username = None
	password = None
	vmname = None
	backuppath = None
	tag_label = None


	def __init__(self, hostfqdn, username, password, vmname, backuppath, frommail, notifymail, logpath, tag_label):

		logfile = hostfqdn + "_" + vmname + "_" + str(datetime.date.today()) + ".log"
		self.xenerror = XenError(notifymail, frommail, logpath, logfile)

		self.xenerror.info("Script started.")

		self.setHostFQDN(hostfqdn)
		self.setUsername(username)
		self.setPassword(password)
		self.setVMName(vmname)
		self.setBackupPath(backuppath)
		self.tag_label = tag_label

		self.xenLogin()
		self.backupVM()
		


	def xenLogin(self):

		try:
			self.session = XenAPI.Session("https://" + self.hostfqdn)
			self.session.xenapi.login_with_password(self.username, self.password)

			self.xenerror.info("Successfully logged in with " + self.username)
		
		except Exception, e:
			try:
				self.xenerror.error("xenLogin: ", e)
			except Exception, e:
				raise


	def backupVM(self):

		try:
			#backing up
			self.xenerror.info("Backup process started")
			vms = self.session.xenapi.VM.get_all()
			name_temp = ""

			vm = self.session.xenapi.VM.get_by_name_label(self.vmname)[0]
			print "vm====%s" % (vm)

			record = self.session.xenapi.VM.get_record(vm)
			if not(record["is_a_template"]) and not(record["is_control_domain"]):
				name = record["name_label"]
				name_temp = "_" + self.tag_label + "_" + name
				status = record["power_state"]
				print "status====%s" % (status)
				if( status == "Running" ):
					self.xenerror.info("Shutdown VM: " + vm)
					print "shutdown====%s" % (vm)
					self.session.xenapi.VM.clean_shutdown(vm)
					print "shutdown is done====%s" % (vm)

			print "generate xva file from vm_temp====%s" % (vm)
                        #HTTP-GET export
                        self.xenerror.info("Exporting VM per HTTP-GET method, this may take a lot of time")

                        urldict = dict(
                                user = self.username,
                                login = self.password,
                                srv = self.hostfqdn,
                                uuid = record["uuid"],
                                name = record["name_label"],
                                ex1 = "https://",
                                ex2 = "/export?uuid=",
                                ex3 = self.backuppath + "/",
                                ex4 = ".xva")

                        #authorization
                        auth = base64.encodestring("%s:%s" % (urldict["user"], urldict["login"])).strip()
                        headers = {"Authorization" : "Basic %s" % auth}

                        #request
                        request = urllib2.Request(urldict["ex1"] + urldict["srv"] + urldict["ex2"] + urldict["uuid"])
                        request.add_header("Authorization", "Basic %s" % auth)
                        result = urllib2.urlopen(request)

                        #file write
                        filepath = urldict["ex3"] + urldict["srv"] + urldict["name"] + urldict["ex4"]
                        outputfile = open(filepath, "wb")

                        for line in result:
                                outputfile.write(line)

                        outputfile.close()

                        #log filesize
                        try:
                                filesize = str(os.path.getsize("%(ex3)s\
                                %(srv)s\
                                %(ex4)s\
                                %(name)s\
                                " % urldict)/1024) + " KB"

                        except:
                                filesize = "filesize unk"

                        self.xenerror.info("VM Exported - Filesize: " + filesize)


			print "gererate xva file is done====%s" % (vm)
			self.xenerror.info("Start VM: " + vm)
                        print "start orignal vm====%s" % (vm)
                        self.session.xenapi.VM.start(vm, False, True)
                        print "start orignal vm is done====%s" % (vm)

			self.xenerror.sendConclusion()


		except Exception, e:
			try:
				# cleanup
				self.xenerror.info("all good!")
				#os.unlink(filepath)

				#self.xenerror.error("backupVM: ", e)
			except Exception, e:
				raise



# setters

	def setHostFQDN(self, hostfqdn):

		if re.search('^.+\..+\..+$', hostfqdn) or re.search('^(\d{1,3}\.){3}\d{1,3}$', hostfqdn):
			self.hostfqdn = hostfqdn

		else:
			try:
				self.xenerror.error('setHostFQDN: Hostname or IP invalid!', "")
			except Exception, e:
				raise



	def setUsername(self, username):

		if len(username) > 1:
			self.username = username

		else:
			try:
				self.xenerror.error('setUsername: too short username!', "")
                        except Exception, e:
                                raise



	def setPassword(self, password):

		if password == None:
			password = ""

		self.password = password



	def setVMName(self, vmname):

                if len(vmname) > 1:
                        self.vmname = vmname

                else:
			try:
	                        self.xenerror.error('setVMName: too short VM name!', "")
                        except Exception, e:
                                raise



	def setBackupPath(self, backuppath):

		if len(backuppath) > 1:

			if backuppath[-1] == "/":
				backuppath = backuppath[0:-1]

			if not os.path.exists(backuppath):
				os.mkdir(backuppath)

			self.backuppath = backuppath

		else:
			try:
				self.xenerror.error('setBackupPath: no valid path!', "")
                        except Exception, e:
                                raise


# eof
