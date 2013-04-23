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

class PyffleLogger:

	session = None
	data = None
	purgeType = None
	currentUser = None
	daysToKeepMsgs = 100
	daysToKeepLogs = 10
	maxMsgsPerBoard = 1000
	maxLogEntries = 1000
	immuneUsers = ["system"]
	immuneBoards = ["0","__pyffle_email"
,"__pyffle_journal"
,"__pyffle_cookie"
,"__pyffle_plan"
,"__pyffle_pm"
,"__pyffle_chat"
]
	VERSION = "Pyffle logs v0.23"



		
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
		
		## Setup up the utility class
		util = PyffleUtil()
		util.data = self.data
		self.data.util = util

		entries = self.data.getLog(num=10000,level=-1)
		for entry in entries:
			outs = ""
			for s in entry:
				if len(str(s)) > 2:
					outs = outs + "{0:20} ".format(str(s))
				else:
					outs = outs + "{0:5} ".format(str(s))
			print outs
					

logger = PyffleLogger()
logger.go()
