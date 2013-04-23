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
import pyffle_editor
from datetime import datetime
import sys
import getpass
import os
import tempfile

def getIdentity():
	return "pyffle_useradmin v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None

	def eventDispatched(self, event):
		pass
	
	def stringEdit(self,prompt,default):
		return self.data.util.promptDefault(prompt,default)

	def intEdit(self,prompt,default):
		s = self.stringEdit(prompt,str(default))
		if s.isdigit():
			return int(s)
		else:
			return default

	def toggle(self,b):
		if b == None or b == False:
			b = True
		else:
			b = False
		return b
	
	def editAcl(self,aclid,username=""):
		self.data.stateChange("useredit_editaclstart")		
		theAcl = self.data.getAcl(aclid)
		userQuits = False
		while not userQuits:
			self.data.stateChange("useredit_editaclloop")
			self.data.util.cls()
			self.data.stateChange("useredit_editaclheaderstart")
			self.data.util.println("{0:29} ".format("ACL: ^" + str(aclid) + "^") + str(theAcl.description))
			grants = self.data.getAclGrants(aclid)
			denies = self.data.getAclDenies(aclid)
			groupdenies = []
			groupgrants = []
			if not username == "":
				groupgrants = self.data.getGroupAces(username,"GRANT")
				groupdenies = self.data.getGroupAces(username,"DENYS")
			self.data.stateChange("useredit_editaclgrantsstart")
			self.data.util.println("{0:15} ".format("\nGRANT: "))
			for theGrant in grants:
				self.data.util.printn("  " + theGrant[0])
			self.data.util.println("{0:15} ".format("\nGRANT (Group): "))
			for theGrant in groupgrants:
				self.data.util.printn("  " + theGrant[0])
			self.data.stateChange("useredit_editaclgrantsend")
			
			self.data.stateChange("useredit_editacldeniesstart")
			self.data.util.println("{0:15} ".format("\nDENY: "))
			for deny in denies:
				self.data.util.println("  " + deny[0])
			self.data.util.println("{0:15} ".format("\nDENY (Group): "))
			for deny in groupdenies:
				self.data.util.println("  " + deny[0])
			self.data.util.println("\n")
			self.data.stateChange("useredit_editacldeniesend")
			self.data.stateChange("useredit_editaclheaderend")
			
			self.data.stateChange("useredit_editaclmenustart")
			self.data.util.println("[^1^] Add GRANT")
			self.data.util.println("[^2^] Drop GRANT")
			self.data.util.println("[^3^] Add DENY")
			self.data.util.println("[^4^] Drop DENY")
			self.data.stateChange("useredit_editaclmenu")
			self.data.stateChange("useredit_editaclpromptstart")
			choice = self.data.util.prompt("\n[^X^]  Exit ACLEDIT> ")		
			self.data.stateChange("useredit_editaclpromptend")
			choice = choice.strip()
			choice = choice.upper()
			
			self.data.stateChange("useredit_editaclchoicestart %s" % (choice))
			if choice == "1":
				permission = self.data.util.prompt("Grant what? ")
				subject =    self.data.util.promptDefault("Subject?  ",username)
				permission = permission.strip().upper()
				subject = subject.strip()
				if not permission == "":
					self.data.grant(theAcl, subject, permission)


			if choice == "2":
				permission = self.data.util.prompt("Drop which grant? ")
				subject =    self.data.util.promptDefault("Subject?  ",username)
				permission = permission.strip().upper()
				subject = subject.strip()
				if not permission == "":
					self.data.dropGrant(theAcl, subject, permission)


			if choice == "3":
				permission = self.data.util.prompt("Deny what? ")
				subject =    self.data.util.promptDefault("Subject?  ",username)
				permission = permission.strip().upper()
				subject = subject.strip()
				if not permission == "":
					self.data.deny(theAcl, subject, permission)

			if choice == "4":
				permission = self.data.util.prompt("Drop which deny? ")
				subject =    self.data.util.promptDefault("Subject?  ",username)
				permission = permission.strip().upper()
				subject = subject.strip()
				if not permission == "":
					self.data.dropDeny(theAcl, subject, permission)


			if choice == "X":
				userQuits = True
				break	
			self.data.stateChange("useredit_editaclchoiceend %s" % (choice))
			self.data.stateChange("useredit_editaclloopend")
		self.data.stateChange("useredit_editaclend")


				
	def printEditMenu(self,theUser):
		self.data.stateChange("useredit_printeditusermenustart")
		menu = [["{0:29} ".format("User:") + "^" + str(theUser.username) + "^","USEREDIT> ","Borkyt. Try again"]]
		menu.append(["A","{0:30} ".format(" ACL") + str(theUser.aclid) + "\n"])
		menu.append(["B",  "{0:30} ".format(" Identity") +   str(theUser.fullidentity) + "\n"])
		menu.append(["D","{0:30} ".format(" Password") + str(theUser.password) + "\n"]) #*PASSWORD"].strip()
		menu.append(["E","{0:30} ".format(" Real Name") + str(theUser.realname) + "\n"]) #*FIRST"].strip()
		menu.append(["F","{0:30} ".format(" Comment") + str(theUser.comment) + "\n"]) #*ASK BACKGROUND"].strip()
		menu.append(["G","{0:30} ".format(" Times Called") + str(theUser.timescalled) + "\n"]) # = 0
		menu.append(["H","{0:30} ".format(" Messages Posted") + str(theUser.messagesposted) + "\n"]) # = 0
		menu.append(["I","{0:30} ".format(" Access Level") + str(theUser.accesslevel) + "\n"]) # = 10 ## FIXME grab from static
		menu.append(["J","{0:30} ".format(" Fake Level") + str(theUser.fakelevel) + "\n"]) # = "10"
		menu.append(["K","{0:30} ".format(" Protocol") + str(theUser.transferprotocol) + "\n"]) # = "K"
		menu.append(["L","{0:30} ".format(" KB Uploaded") + str(theUser.kbuploaded) + "\n"]) # = 0
		menu.append(["M","{0:30} ".format(" LB Downloaded") + str(theUser.kbdownloaded) + "\n"]) # = 0
		menu.append(["N","{0:30} ".format(" Last NEW SCAN") + str(theUser.datelastnewscan) + "\n"]) # = None
		menu.append(["O","{0:30} ".format(" Editor") + str(theUser.externaleditor) + "\n"]) #
		menu.append(["P","{0:30} ".format(" Console Editor") + str(theUser.consoleeditor) + "\n"]) #
		menu.append(["Q","{0:30} ".format(" Terminal") + str(theUser.terminal) + "\n"]) #
		menu.append(["S","{0:30} ".format(" Page Length") + str(theUser.pagelength) + "\n"]) #
		menu.append(["T","{0:30} ".format(" Disable paged msgs") + str(theUser.disablepagedmsgs) + "\n"]) # = False
		menu.append(["U","{0:30} ".format(" Minutes/today") + str(theUser.minutesontoday) + "\n"]) # = -1
		menu.append(["V","{0:30} ".format(" Splash File") + str(theUser.splashfile) + "\n"]) # = None
		menu.append(["V","{0:30} ".format(" Splash File") + str(theUser.splashfile) + "\n"]) # = None
		menu.append(["","\n"]) # = None
		menu.append(["X","{0:30} ".format(" Exit")]) # = None
		choice = self.data.util.menuChoice(menu,menuName="useredit_printmenu")
		
		self.data.stateChange("useredit_printeditusermenuend")
		return choice 
	def userEdit(self, username):
		self.data.stateChange("useredit_edituserstart")
		theUser = self.data.getUser(username)
		if theUser == None:
			self.data.stateChange("useredit_editusernosuchuserstart")
			self.data.util.println("No such user: " + username)
			self.data.stateChange("useredit_editusernosuchuserend")
			self.data.stateChange("useredit_edituserend")
			return
		userQuits = False
		while not userQuits:
			self.data.stateChange("useredit_edituserloopstart")
			choice = self.printEditMenu(theUser)
			choice = choice.upper()		## fix this 
			self.data.stateChange("useredit_edituserchoice %s" % (choice))
			if choice == "X":
				userQuits = True
				break
			if choice == "A":	
				self.editAcl(theUser.aclid,username=username)
			if choice == "B": 	
				theUser.fullidentity = self.stringEdit("Full Identity:",theUser.fullidentity)

			if choice == "D": 	
				theUser.password = self.stringEdit("Password:",theUser.password)
			if choice == "E":	
				theUser.realname = self.stringEdit("Real Name:",theUser.realname)

			if choice == "F":	
				theUser.comment = self.stringEdit("Comment:",theUser.comment)
			if choice == "G":	
				theUser.timescalled = self.intEdit("Times called:",theUser.timescalled)
			if choice == "H":	
				theUser.messagesposted = self.intEdit("Messages posted",theUser.messagesposted)
			if choice == "I":	
				theUser.accesslevel = self.intEdit("Access level:",theUser.accesslevel)
			if choice == "J": 	
				theUser.fakelevel = self.stringEdit("Fake level:",theUser.fakelevel)
			if choice == "K": 	
				theUser.transferprotocol = self.stringEdit("Protocol:",theUser.transferprotocol)
			if choice == "L":	
				theUser.kbuploaded = self.intEdit("KB up:",theUser.kbuploaded)
			if choice == "M":	
				theUser.kbdownloaded = self.intEdit("KB down:",theUser.kbdownloaded)
			if choice == "N":	
				theUser.datelastnewscan = datetime.now()
			if choice == "O":	
				theUser.externaleditor = self.stringEdit("Editor:",externaleditor)
			if choice == "P":	
				theUser.consoleeditor = self.stringEdit("Console editor:",theUser.consoleeditor)
			if choice == "Q": 	
				theUser.terminal = self.stringEdit("Terminal:",theUser.terminal)
			if choice == "S":	
				theUser.pagelength = self.intEdit("Page length:",theUser.pagelength)
			if choice == "T":	
				##theUser.disablepagedmsgs = self.toggle(theUser.disablepagedmsgs)
				pass
			if choice == "U":	
				theUser.minutesontoday = self.intEdit("Minutes/Today:",theUser.minutesontoday)
			if choice == "V":	
				theUser.splashfile = self.stringEdit("Splash File:", theUser.terminal)
			self.data.stateChange("useredit_edituserloopend")
					
		self.data.stateChange("useredit_editsavepromptstart")
		if self.data.util.yesnoprompt("Save changes? "):
			self.data.storeUser(theUser)
			self.data.stateChange("useredit_editusersaved")
		else:
			self.data.stateChange("useredit_editusernotsaved")
		self.data.stateChange("useredit_editsavepromptend")
		self.data.stateChange("useredit_edituserend")
		
	

	def validate(self):
		users = self.data.getUsers()
		self.data.stateChange("useredit_validateloopstart")
		for user in users:
			userAcl = self.data.getAcl(user.aclid)
			if not self.data.isGranted(userAcl,user.username,"VALIDATED"):
				self.data.stateChange("useredit_validatepromptstart")
				if self.data.util.yesnoprompt("\nValidate ^%s^? " % (user.username)):	
					self.data.grant(userAcl,user.username,"VALIDATED")
					self.data.util.printn("\nUser validated")	
					self.data.logEntry(self.data.LOGNORMAL,"ALTER/USER/VALIDATED",str(user.username),"%s validated" % (str(user.username)))					
					self.data.stateChange("useredit_uservalidated")
				self.data.stateChange("useredit_validatepromptend")
		self.data.stateChange("useredit_validateloopend")
			
	def userKill(self, username):
		self.data.stateChange("useredit_killpromptstart")
		if self.data.util.yesnoprompt("\nKILL ^%s^, sure? " % (username)):
			self.data.stateChange("userkill_killstart")
			self.data.util.printn("\nDeleting user..")
			self.data.deleteUser(username)
			self.data.util.println("Done.\n")
			self.data.stateChange("useredit_killend")
		else:
			self.data.stateChange("useredit_cancelled")
		self.data.stateChange("useredit_killpromptend")
		
	def go(self, command, args):
		self.data.stateChange("useredit_start")
		if command == "validate":
			self.data.stateChange("useredit_validatestart")
			self.validate()
			self.data.stateChange("useredit_validateend")

		if command == "acledit":
			if len(args) >= 2:
				self.editAcl(int(args[1]))		
			else:
				self.data.stateChange("useredit_usernamepromptstart")
				choice = self.data.util.prompt("ACL: ")
				self.data.stateChange("useredit_usernamepromptend")
				self.editAcl(int(choice))		

		if command == "useredit":
			if len(args) >= 2:
				self.userEdit(args[1])		
			else:
				self.data.stateChange("useredit_usernamepromptstart")
				choice = self.data.util.prompt("Username: ")
				self.data.stateChange("useredit_usernamepromptend")
				self.userEdit(choice)		
		if command == "kill":
			if len(args) >= 2:
				self.userKill(args[1])		
			else:
				self.data.stateChange("userkill_usernamepromptstart")
				choice = self.data.util.prompt("Username: ")
				self.data.stateChange("userkill_usernamepromptend")
				self.userKill(choice)		
			
				