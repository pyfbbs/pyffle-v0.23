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
import random
import copy

def getIdentity():
	return "pyffle_stats v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule:
	currentUser = None
	data = None
	
	
	def displayTable(self, table):
		self.data.util.println("")
		keys = table.keys()
		keys.sort()
		for key in keys:
			row = "%35{0:30}%0".format(str(key))
			row = row + " | %37{0:>15}%0".format(str(table[key]))
			self.data.util.println(row)
		self.data.util.println("")
	
	
	
	def emailStats(self):
		board = self.data.getBoardByName("__pyffle_email")
		emailCount = self.data.session.query(Message).filter(Message.boardid == board.id).count()
		
		table = {}
		table["Email count"] = emailCount
		self.displayTable(table)
	
			
	
	def specialBoardStats(self):
		board = self.data.getBoardByName("__pyffle_chat")
		chatCount = self.data.session.query(Message).filter(Message.boardid == board.id).count()
		board = self.data.getBoardByName("__pyffle_cookie")
		cookieCount = self.data.session.query(Message).filter(Message.boardid == board.id).count()
		board = self.data.getBoardByName("__pyffle_journal")
		journalCount = self.data.session.query(Message).filter(Message.boardid == board.id).count()
		board = self.data.getBoardByName("__pyffle_pm")
		pmCount = self.data.session.query(Message).filter(Message.boardid == board.id).count()
		
		table = {}
		table["Chat count"] = chatCount
		table["Journal count"] = journalCount
		table["Cookie count"] = cookieCount
		table["PM count"] = pmCount
		self.displayTable(table)
	
	
	def dataStats(self):
		mtas = []					## mta entry = [mta module name to be loaded, mta name, mta description]
		mtaString = "" 
		for mta in self.data.mtas:
			mtaString = mtaString + " %33[%0" + mta[1] + "%33]%0"
		table = {}
		table["MTAs"] = mtaString
		table["System Calls"] = self.data.getSystemCalls()
		self.displayTable(table)
	
	
	def postgresStats(self):
		
		
		backendquery = "SELECT pg_stat_get_backend_pid(s.backendid) AS procpid,       pg_stat_get_backend_activity(s.backendid) AS current_query    FROM (SELECT pg_stat_get_backend_idset() AS backendid) AS s;"
		rv = self.data.session.execute(backendquery).fetchall()
		for row in rv:
			self.data.util.println("%36" + "%s" % ("PG_BACKEND") + " %0 "  + str(row))
			
		statTables = [	"pg_stat_all_tables",
				"pg_statio_all_sequences",
				"pg_stat_database",
				"pg_stat_activity",
				"pg_stat_all_indexes",
				"pg_statio_all_tables"]
		
		for statTable in statTables:
			rv = self.data.session.execute("select * from %s;" % statTable).fetchall()
			for row in rv:
				self.data.util.println("%36" + "%s" % (statTable.upper()) + " %0 "  + str(row))
			##
		
	
	def osDicts(self):
		names = os.sysconf_names
		self.data.util.println("\n%36sysonf%0")
		try:
			for name in names:
				self.data.util.println("%35" + name + "%0 => %37" + str(os.sysconf(name)))
		except:
			pass
		
		names = os.confstr_names
		self.data.util.println("\n%36confstr%0")
		try:
			for name in names:
				self.data.util.println("%35" + name + "%0 => %37" + str(os.confstr(name)))
		except:
			pass
		self.data.util.println("%0")
		
	def sysPoll(self,poll):
		self.data.util.println("\n%36" + poll[0] + "%0")
		f = os.popen(poll[1])
		rv = f.read()
		f.close()
		self.data.util.println(rv)		
	
	def sysStats(self):
		self.data.util.println("\n%36Pyffle version%0")
		self.data.util.println("%&")
		self.data.util.println("\n%36pyffle_stats version%0")
		self.data.util.println(getIdentity())
		self.data.util.println("\n%36Python version%0")
		self.data.util.println(sys.version)
		self.data.util.println("\n%36Platform%0")
		self.data.util.printn(sys.platform)
		self.data.util.println("  %36maxint: %37" + str(sys.maxint) + "%0")
		
		
		
		syspoll = [	["OS details","uname -a"],
				["uptime","uptime"],
				["Google ping","ping -c 1 www.google.com"],
				["Free memory","free -m"],
				["Process count","ps aux | wc -l"]]
		
		for poll in syspoll:
			self.sysPoll(poll)
			
	
	def generalStats(self):
		msgCount = self.data.session.query(Message).count()
		boardCount = self.data.session.query(Board).count()
		userCount = self.data.session.query(Users).count()
		msgtextCount = self.data.session.query(Messagetext).count()
		msgattachCount = self.data.session.query(Messageattachment).count()
		aclCount = self.data.session.query(Acl).count()
		aceCount = self.data.session.query(Ace).count()
		logentryCount = self.data.session.query(Logentry).count()
		currentlyonCount = self.data.session.query(Currentlyon).count()
		pluginsystemCount = self.data.session.query(Pluginsystem).count()
		pluginuserCount = self.data.session.query(Pluginuser).count()
		accesslevelCount = self.data.session.query(Accesslevel).count()
		
		joinedboardCount = self.data.session.query(Joinedboard).count()
		table = {}
		table["Message count"] = msgCount
		table["Board count"] = boardCount
		table["Messagetext count"] = msgtextCount
		table["Messageattachment count"] = msgattachCount
		table["Acl count"] = aclCount
		table["Ace count"] = aceCount
		table["Log entry count"] = logentryCount
		table["Currentlyon count"] = currentlyonCount
		table["Plugin user count"] = pluginuserCount
		table["Plugin system count"] = pluginsystemCount
		table["Joined board count"] = joinedboardCount
		table["Access level count"] = accesslevelCount
		table["User count"] = userCount

		self.displayTable(table)
		
	
	def eventDispatched(self, event):
		pass

	
	def go(self, command, args):
		if command=="systats":
			self.sysStats()
			self.osDicts()
		
		if command=="pgstats":
			self.postgresStats()
		
		if command=="stats":
			self.data.stateChange("stats_statsstart")
			self.generalStats()
			self.emailStats()
			self.specialBoardStats()
			self.dataStats()
			self.data.stateChange("stats_statsend")			
