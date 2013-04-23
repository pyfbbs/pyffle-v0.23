## Models for SqlAlchemy version 6
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import sessionmaker
from pyffle_tables import *
from pyffle_data import *
from pyffle_editor import Editor
from datetime import datetime
import sys
import getpass
import os
import tempfile

def getIdentity():
	return "pyffle_online v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None
		
		
	def eventDispatched(self, event):
		if event[0] == "mainmenuloopstart":
			self.data.stateChange("pmcheckstart")
			self.printAllPms()
			self.data.stateChange("pmcheckend")
			
			
	## checks if a user is currently online
	def isOnline(self,username):
		rv = False
		entries = self.data.getCurrentlyonEntries() 
		for entry in entries:
			if username == entry.username:
				rv = True
				break
		return rv

	## attempts to send a PM to target
	def pm(self,target=None):
		targets = []
		if target == None:
			entries = self.data.getCurrentlyonEntries() 
			for entry in entries:
				if not entry.username in targets: # append each user just once, otherwise we get multiple messages if logged in more than once
					targets.append(entry.username)
		else:
			targets = [target]
		
		message = self.data.util.prompt("Msg> ")
		for user in targets:	
			if self.isOnline(user):
				msgid = self.data.createMessage(self.data.currentUser.username,user,message,"<PM>",board='__pyffle_pm')
				msg = self.data.getMessage(msgid)
				msgAcl = self.data.getAcl(msg.aclid)
				self.data.grant(msgAcl,user,"READ")
				self.data.grant(msgAcl,user,"DELETE")
			 
	## prints all pms for the current user and deletes them
	def printAllPms(self):
		pmBoard = self.data.getBoardByName("__pyffle_pm")
		msgids = self.data.getMessagesByBoardByToUsername(pmBoard,self.data.currentUser.username)
		for msgid in msgids:
			msg = self.data.getMessage(msgid)
			self.data.util.prompt("^Incoming PM^ - Press Return to read..")
			self.data.util.println("\n^PM=>^   " + msg.fromname + ": %37" + msg.subject + "%0\n")
			self.data.toolMode = True
			self.data.deleteMessage(msgid)
			self.data.toolMode = False			  
			
			
	def go(self, command, args):
		command = command.strip()
		if command == "_dump":
##			self.data._dumpMessages()
			pass


		if command == "wall":
			self.pm()


		if command == "pm":
			destination = None
			if (len(args) >= 2):
				destination = args[1]
			else:
				destination = self.data.util.prompt("Send to: ")
		
			self.pm(destination.strip())
		if command == "!check_pms":
			self.printAllPms()
			