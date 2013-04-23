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
	return "pyffle_voice v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True



class PyffleModule(pyffle_module.PyffleModule):
	
## Catches main user events and runs OS scripts - could be used to play a sound
## or something

	def eventDispatched(self, event):
		if event[0] == "registerdone":
			## launch sound for new user registered
			os.system("/pyffle/registerscript")
			pass
		if event[0] == "loginend":
			## launch sound for new user registered
			os.system("/pyffle/loginscript")			
			pass

		if event[0] == "logoutmsgend":
			## launch sound for new user registered
			os.system("/pyffle/logoutscript")			
			pass

## If invoked, runs a script to page the sysop.

	def go(self, command, args):		
		cmdstr = "User " + self.data.currentUser.username + " is paging the sysop.."
		os.system("/pyffle/pagescript " + "'" + cmdstr + "'")