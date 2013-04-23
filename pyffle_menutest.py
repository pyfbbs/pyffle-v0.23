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

## Returns an identity string describing out module
def getIdentity():
	return "pyffle_example v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	rv = True
	if version == "ReallyBadVersion":
		rv = False
	return rv



class PyffleModule(pyffle_module.PyffleModule):

	def eventDispatched(self, event):
		## We react to whenever the main menu prompt is about to be
		## displayed and say hello
		if event[0] == "mainmenupromptstart":
			self.data.util.debugln("\n^Hello^\n")
		
	def go(self, command, args):
		menu = [ 	["Menu Test","MENUTEST> ","Borkyt. Try again"],
				["A","Alpha\n"],
				["","-------\n"],
				["B","Beta\n"],
				["1","One\n"] ]
		self.data.util.menuChoice(menu)
		