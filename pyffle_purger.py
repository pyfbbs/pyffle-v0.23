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
import datetime
import time

class PyfflePurger:

	session = None
	data = None
	purgeType = None
	currentUser = None
	daysToKeepMsgs = 100
	daysToKeepLogs = 10
	maxMsgsPerBoard = 300
	maxLogEntries = 1000
	immuneUsers = ["system"]
	immuneBoards = ["0","__pyffle_email"
,"__pyffle_journal"
,"__pyffle_cookie"
,"__pyffle_plan"
,"__pyffle_pm"
,"__pyffle_chat"
]
	VERSION = "Pyffle purger v0.23"
	
		
		
	def purgeAcls(self):
		## We're looking for orphaned ACLs
		self.data.loggingOff = True
		aclsInUse = []
		print "#Usergroup ACLs..	"

		for object in self.session.query(Usergroup):
			aclsInUse.append(object.aclid)
			sys.stdout.write(".")
		print "## Users.."
		for object in self.session.query(Users):
			aclsInUse.append(object.aclid)
			sys.stdout.write(".")

		print "## Boards.."
		for object in self.session.query(Board):
			aclsInUse.append(object.aclid)
			sys.stdout.write(".")

		## Messages and contents
		for object in self.session.query(Message):
			aclsInUse.append(object.aclid)
			sys.stdout.write(".")

		print "TexT"
		for object in self.session.query(Messagetext):
			aclsInUse.append(object.aclid)
			sys.stdout.write(".")
	
		print "Attachments"
		for object in self.session.query(Messageattachment):
			aclsInUse.append(object.aclid)
			sys.stdout.write(".")
		
		print "Found " + str(len(aclsInUse)) + " ACLs in use"
		
		print "Killing orphaned ACLs"
		for object in self.session.query(Acl):
			if not object.id in aclsInUse:
				print object.id
				sys.stdout.write(".")
				try:
					## get all the ACEs under this ACL
					for ace in self.session.query(Ace).filter(Ace.aclid == object.id):
						aceid = ace.id
						self.session.delete(ace)
					## now delete the ACL
					self.session.delete(object)
					sys.stdout.write("*")
					self.session.commit()
				except:
					print "\nBORK! ACL in use" 
					self.session.rollback()
		
	def purgeMessages(self):
		# calculate time delta
		self.data.loggingOff = True
		purgeDate = datetime.datetime.now() - datetime.timedelta(days=self.daysToKeepMsgs)
		
		boards = self.data.getBoards()
		for board in boards:
			try:
				if board.name in self.immuneBoards:
					print "Immune " + board.name
				else:
					purgeIds = self.data.getMessageIdsOlderThan(purgeDate, board.name)
					for id in purgeIds:
						print "Purging old message " + str(id)
						try:
							self.data.deleteMessage(id)
						except:
							print "BORK!" + board.name + str(sys.exc_info()) 
							pass ### FIXME UGLY HACK
					if purgeIds==[]:
						print "No old messages to purge in board " + board.name
					try:
						overflowIds = self.data.getOldMessagesOver(board.name, self.maxMsgsPerBoard)
						for id in overflowIds:
							print "Purging overflow message " + str(id)
							self.data.deleteMessage(id)
					except:
						print "BORK!" + board.name + str(sys.exc_info())
						pass ### FIXME UGLY HACK
	
	
					if purgeIds==[]:
						print "Board not full " + board.name
			except:
				print "BORK!" + str(sys.exc_info())
				pass ### FIXME UGLY HACK
			
	def purgeLogs(self):
		self.data.purgeLogentries(self.maxLogEntries)
	
	def go(self):	
		## Initialise the main controller, load static file
		self.data = PyffleData()
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
		self.data.loglevel = self.data.LOGCRIT
		## Setup up the utility class
		util = PyffleUtil()
		util.data = self.data
		self.data.util = util
		if self.purgeType == "msgs":
			self.purgeMessages()
		elif self.purgeType == "logs":
			self.purgeLogs()
		elif self.purgeType == "acls":
			self.purgeAcls()
			
					


### main program starts here
args = sys.argv
pyfflePurger = None
print "\n\n\n\n" + PyfflePurger.VERSION + " started at " + str(datetime.datetime.now())
if (len(args) == 2):
	pyfflePurger = None
	if args[1] ==  "acls":
		print "Doing acls"
		pyfflePurger = PyfflePurger()
		pyfflePurger.purgeType = "acls"
	if args[1] ==  "logs":
		print "Doing logs"
		pyfflePurger = PyfflePurger()
		pyfflePurger.purgeType = "logs"
	elif args[1] == "msgs":
		pyfflePurger = PyfflePurger()
		pyfflePurger.purgeType = "msgs"
	else:
		print "weird args, man\n"
		print "Usage: pyffle_purger.py [msgs|logs|users]"

pyfflePurger.go()
	
