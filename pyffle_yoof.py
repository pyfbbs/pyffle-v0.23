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
	return "pyffle_yoof v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None
		
		
	def eventDispatched(self, event):
		if event[0] == "loginend":
			self.data.stateChange("yoofshowstart")
			self.showWall()
			self.data.stateChange("yoofshowend")
			
		if event[0] == "mainmenubyestart":
			self.msgNextUser()

	def msgNextUser(self):
		self.post(thePrompt = "\nLeave message for next user? ")
		
	def post(self,thePrompt="\nScribble on wall? "):
		wants = self.data.util.prompt(thePrompt)
		if wants.lower() == "y" or wants.lower() == "yes":
			message = self.data.util.prompt("Msg (50 chars max will be displayed)> ")
			msgid = self.data.createMessage(self.data.currentUser.username,None,message,"<PM>",board='__pyffle_yoof')
			self.data.util.println("\nScribbled..")
			#msg = self.data.getMessage(msgid)
			#msgAcl = self.data.getAcl(msg.aclid)
			#self.data.grant(msgAcl,user,"READ")
			#self.data.grant(msgAcl,user,"DELETE")
		else:
			self.data.util.println("OK then..")
			 
	## prints all pms for the current user and deletes them
	MAXYOOF = 10
	def parseDate(self,thedate):
		return format("%s" % (self.data.util.formatDateString(thedate)))
		
	def showWall(self):
		pmBoard = self.data.getBoardByName("__pyffle_yoof")
		msgids = self.data.getMessagesByBoardid(pmBoard.id)
		msgids.reverse()
		maxMsg = self.MAXYOOF ## FIXME read from static
		
		topmsg = len(msgids)
		if topmsg > maxMsg:
			topmsg = maxMsg
			
		self.data.util.println("\n\n%35Graffiti%0 for your amusement:\n")
		for i in range(0,topmsg):
			msg = self.data.getMessage(msgids[i])
			self.data.util.println("%36" + "{0:10}".format(msg.fromname[0:10]) + ":%0 %37  " + "{0:55}".format(msg.subject[0:55]) + "%0 @ " + self.parseDate(msg.sentdate))
		self.data.util.println("")
		self.post()
					
	def go(self, command, args):
		command = command.strip()
		if command == "_dump":
##			self.data._dumpMessages()
			pass

		if command == "yoof":
			self.showWall()


			