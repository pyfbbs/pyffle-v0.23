#! /usr/bin/python
###
###    This file is part of Pyffle BBS.
###
###    Pyffle BBS is free software: you can redistribute it and/or modify
###    it under the terms of the GNU General Public License as published by
###    the Free Software Foundation, either version 3 of the License, or
###    (at your option) any later version.
###
###    Pyffle BBS is distributed in the hope that it will be useful,
###    but WITHOUT ANY WARRANTY; without even the implied warranty of
###    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
###    GNU General Public License for more details.
###
###    You should have received a copy of the GNU General Public License
###    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
###
###



## Models for SqlAlchemy version 6
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import sessionmaker
from pyffle_tables import *
from pyffle_data import *
import pyffle_mail
from pyffle_util import PyffleUtil
from pyffle_static import PyffleStatic
from datetime import datetime
import sys
import getpass
import os
import copy
import email
import warnings

class PyffleRmail:

	session = None
	data = None
	currentUser = None
	## Clears the message base and writes two messages, dumps them to screen,
	## deletes them
	def parseIncomingAddress(self,toAddress):
		print "PARSE INPUT=" + str(toAddress)
		username = toAddress
		hostname = ""
		if toAddress.find("@") >= 0:
		    username,hostname = toAddress.lower().split("@")
		print "Parsed USER, HOST = " + str([username,hostname])
		return username,hostname
		
	def incomingAddressIsLocal(self,toAddress):
		## FIXME
		return True
		aliases = [self.data.static.options["node"].strip().lower()]
		for alias in self.data.static.options["alias"].split(" "):
			aliases.append(alias.strip().lower())
		username,hostname = self.parseIncomingAddress(toAddress.strip().lower())
		if hostname in aliases:
			return True
		else:
			return False
			
	def debugMessageTest(self):
		self.data.clearMessages()
		msg1 = self.data.createMessage("fooble","sampsa","Test from py","Hello earth")
		msg2 = self.data.createMessage("foo@bar.com","sampsa","Test to outside","Hello sky")
		self.data.dumpMessages()
		self.data.deleteMessage(msg1)
		self.data.deleteMessage(msg2)

	def go(self,finalDestination):	
		## Initialise the main controller, load static file
		##self.data.util.debugln("in go with final destination " + str(finalDestination))
		self.data = PyffleData()
		util = PyffleUtil()
		self.data.util = util
		self.words =  self.data.util.loadWords("WORDS")		## FIXME should be from static
		self.info =   self.data.util.loadWords("INFO")
		self.help =   self.data.util.loadWords("HELP")
		self.menus =  self.data.util.loadWords("MENUS")
		self.text =   self.data.util.loadWords("TEXT")
		self.system = self.data.util.loadWords("SYSTEM")
		self.data.util.texts["WORDS"] = self.words
		self.data.util.texts["INFO"] = self.info
		self.data.util.texts["HELP"] = self.help
		self.data.util.texts["MENUS"] = self.menus
		self.data.util.texts["TEXT"] = self.text
		self.data.util.texts["SYSTEM"] = 	self.system			
		self.data.toolMode = True 	## Turn on Tool Mode so that we override security restrictions
		static = PyffleStatic()		## FIXME read this from a env var or something
		static.parse("/pyffle/static")
		self.data.static = static

		## Setup the DB connection
		Session = sessionmaker()
		engine = create_engine(static.options["pyffle.dburl"], echo=False) ### FIXME pull this out of static
		Session.configure(bind=engine)	
		self.session = Session()
		self.data.session = self.session
		
		## Setup up the utility class
		util = PyffleUtil()
		util.data = self.data
		self.data.util = util
		
		## Load the MTA plugins
		mtalist = [["pyffle_mta_uucp","Pyffle UUCP","UUCP MTA for Pyffle"]]
		self.data.loadMtaList(mtalist)

		## parse the incoming message
		msgString = sys.stdin.read()
		rfcMsg = email.message_from_string(msgString)
		payload = rfcMsg.get_payload()		
		
		toAddress = finalDestination

		## is this a local message?
		self.data.util.debugln("*******************------------------------****************")
		self.data.util.debugln("Checking in the incoming address is local or not" + str(finalDestination))
		if self.incomingAddressIsLocal(toAddress):
			self.data.util.debugln("it is, let's parse the address")	
			toname,hostname = self.parseIncomingAddress(toAddress)
			self.data.util.debugln(str([toname,hostname]))
			## Ask an MTA to parse the incoming address
			if (not toname == "") and (not toname == None):
				self.data.util.debugln("RMAIL F=%s T=%s S=%s\n" % (rfcMsg['From'],toname,rfcMsg['Subject']))
				self.data.util.debugln("Creating message")				
				## Store the message
				if rfcMsg.is_multipart():
					parts = rfcMsg.get_payload()
					payload = ""
					partnum = 1
					for part in parts:
						payload = payload + part.get_payload()
						payload = payload + "\nMIME segment %s begins: \n" % (str(partnum))
						partnum = partnum + 1
				#os.system("Sending message to " + toname + " >> /tmp/rmail ")			
				self.data.util.debugln("Sending message")
				self.data.createMessage(rfcMsg['From'],toname,rfcMsg['Subject'],payload)		
				self.data.logEntry(self.data.LOGINFO,"IMPORT/MESSAGE/RMAIL",str(toname),"Received mail for %s from %s" % (str(toname),str(rfcMsg['From'])))		

		else: 
			pass
			self.data.util.debugln("RMAIL Sending to external rmail")
			## Pass to external rmail
			with warnings.catch_warnings(record=True) as warn:
				## FIXME CRITICAL: need to sanitize the To header here...Shell injection
				rmail = self.data.static.options["pyffle.extrmail"] + " " + finalDestination
				mailin, mailout = os.popen2(rmail)
				mailin.write(msgString)
				mailout.close()
				mailin.close()
			
	
		
### Main program



args = sys.argv
print args
if len(args) >= 2:
	print "Running Pyffle rmail with args " + str(args)
	pyffleRmail = PyffleRmail()
	#self.data.util.debugln("Got good args, lets go: " + str(args))
	#os.sytem("echo running at `date` with args >> /tmp/rmail " + str(args))
	print "Executing go " + str(args)
	pyffleRmail.go(args[1])
	print "Go done" + str(args)

else:
	print "Invalid command line arguments. Usage: pyffle_rmail <final destination address>"
	
