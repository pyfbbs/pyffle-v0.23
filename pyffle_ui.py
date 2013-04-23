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
import pyffle_module

def getIdentity():
	return "pyffle_ui v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

## Catches event "mainmenupromptstart" and does a mail check

class PyffleModule(pyffle_module.PyffleModule):
	currentUser = None
	data = None

	def getMenuState(self):
		username = self.data.currentUser.username
		state = self.data.pluginReadUser(username,"__pyffle_ui")
		if state == None:
			state = "OFF"
		return state
		
		
	def setMenuState(self,state):
		username = self.data.currentUser.username
		self.data.pluginWriteUser(username,"__pyffle_ui",state)


	def displayUi(self):
		if self.getMenuState() == "ON":
			self.data.stateChange("ui_start")					
			#self.data.util.cls()			
			self.data.util.printn(self.data.util.texts["MENUS"]["main"])
	#		self.data.util.printn(str(self.data.util.texts["MENUS"].keys()))
			self.data.stateChange("ui_end")

		
	def eventDispatched(self, event):
		##print event
		if event[0] == "mailcheck_end":
			self.displayUi()
	
	def go(self, command, args):
		state = self.getMenuState()
		if state == "ON":
			state = "OFF"
		else:
			state = "ON"
		self.setMenuState(state)
	
		