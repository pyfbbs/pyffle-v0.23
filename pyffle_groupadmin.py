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
from pyffle_editor import Editor
from datetime import datetime
import sys
import getpass
import os
import tempfile

def getIdentity():
	return "pyffle_groupadmin v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None

	def eventDispatched(self, event):
		pass
		

	def showGroups(self):
		for group in self.data.getGroups():
			self.showGroup(group)
	
	def showGroup(self,group):
		self.data.util.println("^%s^ - %s - ACL ID: %s" % (str(group.groupname),str(group.description),str(group.aclid)))
		members = self.data.getGroupMembers(group.groupname)
		if not members == None:
			self.data.util.printn("   ^=>^ ")
			for member in members:
				self.data.util.printn("%s  " % (str(member)))
			self.data.util.println("")
			
		
			
	def dropGroup(self):
		self.data.util.println(getIdentity() + "\n")
		self.data.stateChange("groupadmin_dropgroupstart")
		self.data.util.println("Dropping group...")
		self.data.stateChange("groupadmin_dropgrouppromptstart")
		name = self.data.util.prompt("Group Name: ")
		self.data.stateChange("groupadmin_dropgrouppromptend")
		self.data.stateChange("groupadmin_dropgroupconfirmstart")
		confirm = self.data.util.yesnoprompt("Proceed? ")
		if confirm:
			self.data.stateChange("groupadmin_dropgroupdeletestart")
			self.data.util.printn("Dropping group...")
			self.data.deleteGroupByGroupname(name)
			self.data.util.println("Group dropped.")
			self.data.stateChange("groupadmin_dropgroupdeleteend")
		self.data.stateChange("groupadmin_dropgroupconfirmend")
		self.data.stateChange("groupadmin_dropgroupend")

		
	def createGroup(self):	
		self.data.util.println(getIdentity() + "\n")

		self.data.stateChange("groupadmin_creatgrouppromptsstart")
		self.data.util.println("Creating group...")
		name 		= 	self.data.util.prompt("Group Name:          ")
		description = 	self.data.util.prompt("Description:			")
		self.data.stateChange("groupadmin_creatgrouppromptsend")
		
		self.data.stateChange("groupadmin_creatgroupconfirmstart")		
		confirm = self.data.util.yesnoprompt("Proceed? ")
		if confirm:
			self.data.stateChange("groupadmin_creatgroupaddstart")		
			self.data.util.printn("\nAdding group...")
			grouppid = self.data.createGroup(name, description)
			group = self.data.getGroup(grouppid)
			self.data.util.println("Group added, ACL %s." % (str(group.aclid)))
			self.data.stateChange("groupadmin_creatgroupaddend")
		else:
			self.data.stateChange("groupadmin_creatgroupcancel")
		self.data.stateChange("groupadmin_creatgroupconfirmend")
		self.data.stateChange("groupadmin_creatgroupend")
		
	
	def go(self, command, args):
		self.data.stateChange("groupadmin_start")
		command = command.strip()
			
		if command == "creategroup":
			self.data.stateChange("groupadmin_createstart")
			if self.data.srmcheck(self.currentUser.aclid,self.currentUser.username,"CREATEGROUP"):
				self.createGroup()
			else:
				self.data.stateChange("groupadmin_creategroupsecurityfailstart")
				self.data.util.println("You do not have the permission to add groups.")
				self.data.stateChange("groupadmin_creategroupsecurityfailend")
			self.data.stateChange("groupadmin_createend")

		if command == "addmember":
			self.data.stateChange("groupadmin_addmemberstart")
			if self.data.srmcheck(self.currentUser.aclid,self.currentUser.username,"ADDMEMBER"):
				group = self.data.util.prompt("Group to add member to:   ")
				member = self.data.util.prompt("Member's username:           ")
				if self.data.addGroupMember(group,member):
					self.data.util.println("%s added to %s" % (str(member),str(group)))
				else:
					self.data.util.println("Add member failed.")
			else:
				self.data.stateChange("groupadmin_addgmembersecurityfailstart")
				self.data.util.println("You do not have the permission to add members.")
				self.data.stateChange("groupadmin_addmembersecurityfailend")
			self.data.stateChange("groupadmin_addmemberend")


		if command == "dropmember":
			self.data.stateChange("groupadmin_dropmemberstart")
			if self.data.srmcheck(self.currentUser.aclid,self.currentUser.username,"DROPMEMBER"):
				group = self.data.util.prompt("Group to drop member from:   ")
				member = self.data.util.prompt("Member's username:           ")
				if self.data.dropGroupMember(group,member):
					self.data.util.println("%s dropped from %s" % (str(member),str(group)))
				else:
					self.data.util.println("Drop member failed.")

			else:
				self.data.stateChange("groupadmin_dropgmembersecurityfailstart")
				self.data.util.println("You do not have the permission to drop members.")
				self.data.stateChange("groupadmin_dropmembersecurityfailend")
			self.data.stateChange("groupadmin_dropmemberend")
			
		if command == "dropgroup":
			self.data.stateChange("groupadmin_dropstart")
			if self.data.srmcheck(self.currentUser.aclid,self.currentUser.username,"DROPGROUP"):
				self.dropGroup()
			else:
				self.data.stateChange("groupadmin_dropgroupsecurityfailstart")
				self.data.util.println("You do not have the permission to drop groups.")
				self.data.stateChange("groupadmin_dropgroupsecurityfailend")
			self.data.stateChange("groupadmin_dropend")

		if command == "showgroups":
			self.data.stateChange("groupadmin_showstart")
			if self.data.srmcheck(self.currentUser.aclid,self.currentUser.username,"SHOWGROUPS"):
				self.showGroups()
			else:
				self.data.stateChange("groupadmin_showroupsecurityfailstart")
				self.data.util.println("You do not have the permission to show groups.")
				self.data.stateChange("groupadmin_showgroupsecurityfailend")
			self.data.stateChange("groupadmin_showend")
