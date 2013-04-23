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
from pyffle_exception import *
import pyffle_mail
from datetime import datetime

from curses.ascii import isprint
import random
import sys
import getpass
import os
import re
import petscii
import time
import copy

class PyffleUtil:
	data = None
	currentUser = None
	bold = False
	lastInput = ""
	zippy = None 
	texts = {}
	petsciiMode = False

	pagingMode = True
	
	def togglePaging(self):
		self.pagingMode = not self.pagingMode
		return ""	
	
	
	def pet2asc(self,s):
		rv =	petscii.pet2asc(s,True)
		self.debugn("PETSCII RV= |" + rv + "|")
		return rv

	def asc2pet(self,s):
		return petscii.asc2pet(s,True)
		
		
	def getZippy(self):
		rv = ""
		if self.zippy == None:
			self.zippy = self.texts["SYSTEM"]["zippy"].split("|") 

		if len(self.zippy) > 0:
			random.seed()
			rv = random.choice(self.zippy)

		return rv
	
	
	def printable(self,theinput):
		return ''.join([char for char in theinput if isprint(char)])
	
	def helpMenu(self,words,header="\nInformation Available:",maxCols = 4,prompt = "\n\nHelp> ",listwords=True):
		userQuits = False
		while not userQuits:
			self.cls()
			self.println(header)
			self.println("")
			col = 0
			if listwords:
				for word in words:
					if not word.startswith("."):
						self.printn(word.upper() + "    ")
						col = col + 1
						if col > maxCols:
							self.println("")
							col = 0
			choice = self.prompt(prompt)
			choice = choice.lower()
			if choice in words.keys():
				self.println("")
				self.printPaged(words[choice])
				self.prompt("\nPress ENTER..")
			if choice == "q":
				userQuits = True
			if choice == "?":
				self.data.util.println("Select a topic from above or Q to quit..")				
				self.prompt("\nPress ENTER..")
				validChoice = True

	def eventDispatched(self, event):
		## We react to whenever the main menu prompt is about to be
		## displayed and say hello
		print event
		
	def menuChoice(self,menu,menuName="Menu"):
		header = menu[0][0]
		choicePrompt = menu[0][1]
		invalidChoice = menu[0][2]
		## get the options
		keys = []
		for entry in menu[1:]:
			key = entry[0]
			if not key == "":
				keys.append(key.lower())
		## loop until we get a valid choice
		validChoice = False
		choice = ""
		self.data.stateChange(menuName + "loopstart")
		while not validChoice:
			self.cls()
			outLine = ""
			self.data.stateChange(menuName + "printstart")
			outLine = outLine + header + "\n"
			outLine = outLine + "\n"
			for entry in menu[1:]:
				if not entry[0] == "":
					outLine = outLine + "^%s^  %s" % (entry[0],entry[1])
				else:
					outLine = outLine + "%s" % (entry[1])
			outLine = outLine + "\n"
			self.println(outLine)
			self.data.stateChange(menuName + "printend")
			self.data.stateChange(menuName + "promptstart")
			choice = self.prompt(choicePrompt)
			self.data.stateChange(menuName + "promptend")
			choice = choice.lower()
			if choice in keys:
				self.data.stateChange(menuName + "validchoice")
				validChoice = True
			else:
				self.data.stateChange(menuName + "invalidchoice")
				self.prompt(invalidChoice)
		self.data.stateChange(menuName + "loopend")
		return choice
	
				
		
	##### FIXME this is hardcodded to /pyffle.
	#####	
	def loadWords(self,path):
		path = "/pyffle/" + path
		words =  os.listdir(path)
		
		self.debugln("Loading words: " + str(words))
		rv = {}
		for word in words:
			if not word.startswith("."):
				f = open(path + "/" + word) ## FIXME portable path separator
				wordContent = f.read()
				word = word.lower()
				rv[word] = wordContent
				f.close()
		return rv
	def toggleBold(self):
		rv = ""
		if self.bold:
			## Turn bold off
			if self.petsciiMode:
				rv = petscii.getpetspecial("{RVSON}")
			else:
				rv = "\x1b[0m"
			self.bold = False
		else:
			if self.petsciiMode:
				rv = petscii.getpetspecial("{RVSOFF}")
			else:
				rv = "\x1b[7m"
			self.bold = True
		return rv
		
	curRow = 0
	def resetPager(self):
		self.curRow = 0
	
	def addToPager(self,i):
		self.curRow = 		self.curRow + i

	def checkPager(self):
		wantContinue = True
		if self.pagingMode and (not self.currentUser == None):
			if self.curRow >= self.currentUser.pagelength - 1:
				choice = self.prompt("-- ^more^ --            [^RET^] / [^BRK^]")
				choice = choice.lower().strip()
				if choice.lower() == "n":
					wantContinue = False
					raise PyffleException("User break")
				self.resetPager()
		return wantContinue
		
	def cls(self):
		##os.system("clear")
		self.printn("\x1b[2J\x1b[H")
		self.resetPager()
	
	def readline(self):
		return sys.stdin.readline()
		

	def formatTimeString(self,date):
		return str(date.strftime("%H:%M"))

	def formatDateString(self,date):
		return str(date.strftime("%Y-%m-%d"))

	def formatDateTimeString(self,date):
		return str(date.strftime("%Y-%m-%d %H:%M"))
	def getCurrentTimeString(self):
		return self.formatTimeString(datetime.now())

	def getCurrentDateString(self):
		return self.formatDateString(datetime.now())


	def yesnoprompt(self,s,bold=True):
		if bold:
			s = s + "^Y^/^N^ "
		choice = self.prompt(s)
		choice = choice.lower()
		if choice == 'y' or choice == 'yes':
			return True
		return False
	
	
	def bezel(self,s):
		lines = s.split("\n")

		maxlen = 0
		for line in lines:
			newline = self.expandText(copy.copy(line))
			if len(newline) > maxlen:
				maxlen = len(newline)
		bz = "\n"
		bz = bz + "\t."
		for i in range(0,maxlen+2):		## leave space on each side
			bz = bz + str("-")
		bz = bz + str(".")
		bz = bz + str("\n")
		
		for line in lines:
			bz = bz + str("\t| " + line)
			newline = self.expandText(copy.copy(line))
			diff = maxlen - len(newline)
			if not diff == 0:
				for i in range(0,diff):
					bz = bz + str(" ")
			bz = bz + str(" |\n")

		bz = bz + str("\t'")
		for i in range(0,maxlen+2):		## leave space on each side
			bz = bz + str("-")
		bz = bz + str("'")
		bz = bz + str("\n")
		self.printn(bz)
		
		
			
 		
	def readPassword(self,prompt=""):
		password =	getpass.getpass(prompt)	
		if self.petsciiMode:
			choice = self.pet2asc(password)
		return  password
		
	def promptDefault(self,s,default):
		choice = self.prompt(s + " [%s] " % (default))
		if choice == "":
			choice = default
		return choice

	def prompt(self,s):
		self.resetPager()
		self.debugn("ROW=" + str(self.curRow) + "|")
		self.printn(s)
		choice = self.readline()
		choice = choice.strip()
		if self.petsciiMode:
			choice = self.pet2asc(choice)
		self.addToPager(1)
		return choice

	def doBolds(self,s):
		rv = ""
		wasPercent = False
		for c in s:
			if c == "%":
				wasPercent = True
			else:
				if c == "^":
					if wasPercent:
						rv = rv + "^"
					else:
						rv = rv + self.toggleBold()
					wasPercent = False
				else:
					rv = rv + c
					wasPercent = False
		return rv
	
	def setColor(self,n):
		rv = "\x1b[" + str(n) + "m"
		
		return rv
		
	def expandText(self,text):
		newText = re.sub(r'%$',r'',text);
		newText = newText.replace("%|","\n")
		if newText.count("%999") > 0:
			newText = newText.replace("%999",self.togglePaging());
		newText = newText.replace("%30",self.setColor(30));
		newText = newText.replace("%31",self.setColor(31));
		newText = newText.replace("%32",self.setColor(32));
		newText = newText.replace("%33",self.setColor(33));
		newText = newText.replace("%34",self.setColor(34));
		newText = newText.replace("%35",self.setColor(35));
		newText = newText.replace("%36",self.setColor(36));
		newText = newText.replace("%37",self.setColor(37));
		newText = newText.replace("%40",self.setColor("40"));
		newText = newText.replace("%41",self.setColor("41"));
		newText = newText.replace("%42",self.setColor("42"));
		newText = newText.replace("%43",self.setColor("43"));
		newText = newText.replace("%44",self.setColor("44"));
		newText = newText.replace("%45",self.setColor("45"));
		newText = newText.replace("%46",self.setColor("46"));
		newText = newText.replace("%47",self.setColor("47"));

		newText = newText.replace("%0",self.setColor(0));
		newText = newText.replace("%00",self.setColor(0));
		newText = newText.replace("%1",self.setColor(1));
		newText = newText.replace("%4",self.setColor(4));
		newText = newText.replace("%5",self.setColor(5));
		newText = newText.replace("%7",self.setColor(7));
		newText = newText.replace("%8",self.setColor(8));

		if not self.currentUser == None:
			newText = newText.replace("%c",str(self.currentUser.timescalled));
			newText = newText.replace("%!",str(self.data.getSystemCalls()));
			newText = newText.replace("%@",str(self.currentUser.datefastlogin));
			newText = newText.replace("%A",self.currentUser.username);
			newText = newText.replace("%F",self.currentUser.realname)
			newText = newText.replace("%G","<n/a>")
			newText = newText.replace("%L",self.currentUser.fakelevel)
			newText = newText.replace("%M","14")	## FIXME WTF is this? 'Moves'? 
			newText = newText.replace("%N",self.data.getCurrentBoard())	
			newText = newText.replace("%O",self.data.getTimeLeft())
			newText = newText.replace("%P",str(self.currentUser.accesslevel))
			newText = newText.replace("%R",self.currentUser.comment)
			newText = newText.replace("%S","<n/a>")
			newText = newText.replace("%U","<n/a>")
			newText = newText.replace("%W",self.currentUser.fullidentity)			
			newText = newText.replace("%Z",self.getZippy())		## FIXME add Zippy cookies
			newText = newText.replace("%a",str(self.data.currentUser.accesslevel))
			newText = newText.replace("%b","LOCAL")		## FIXME 
			newText = newText.replace("%c",str(self.currentUser.timescalled));
			newText = newText.replace("%d","<n/a>");## FIXME, get the TTY somehow
			newText = newText.replace("%e",self.currentUser.externaleditor);## FIXME, get the TTY somehow
			newText = newText.replace("%f","<n/a>");## FIXME, get the TTY somehow
			newText = newText.replace("%m",str(len(self.data.getNewMessages())))
			newText = newText.replace("%p",str(self.currentUser.messagesposted))
			newText = newText.replace("%r",str(self.currentUser.kbdownloaded))
			newText = newText.replace("%s",str(self.currentUser.kbuploaded))
			newText = newText.replace("%t",str(self.currentUser.terminal))
			newText = newText.replace("%v","<n/a>")
			newText = newText.replace("%t",str(self.currentUser.transferprotocol))
			newText = newText.replace("%#","<n/a>")
			newText = newText.replace("%?","<n/a>")

		if not self.data == None:
			newText = newText.replace("%l",self.data.getLastUser()[0])
			newText = newText.replace("%n",self.data.getNodename())
			newText = newText.replace("%o",self.data.static.options["organ"])
			newText = newText.replace("%u",self.data.static.options["uucpname"])
			newText = newText.replace("%&",self.data.getPyffleVersionString())
			newText = newText.replace("%V",self.data.getPyffleVersionShortString())
			newText = newText.replace("%B",self.data.getCurrentBoardString())
			newText = newText.replace("%Z",self.getZippy())
			newText = newText.replace("%$",str(self.data.getTotalMessageCount()))


		newText = newText.replace("%T",self.getCurrentTimeString())
		newText = newText.replace("%D",self.getCurrentDateString())
		newText = newText.replace("%i",self.lastInput)
		newText = newText.replace("~*","\x1b[2J") 
		newText = newText.replace("~","") 
		newText = newText.replace("%%","%")
		newText = self.doBolds(newText)
		return newText
		
	DEBUG = True
	
				
	def debugln(self,s):
		self.debugn(s + "\n")

	def debugn(self, s):
		if self.DEBUG:
			f = open("/pyffle/data/debugout","a")
			f.write(s)		
			f.close()
			
	def println(self,s):		
		self.printn(self.expandText(s)+"\n")
	
	def printraw(self,s):
		self.printrawn(s+"\n")

	def printrawn(self,s):
		self.addToPager(s.count("\n"))
		if self.petsciiMode:
			s = self.asc2pet(s)
		sys.stdout.write(s)
		self.checkPager()
		
	def printn(self,s):
		s = self.expandText(s)		
		self.printrawn(s)
	
	def printPaged(self,s):
		for line in s.split("\n"):
			self.println(line)	

	def printPagedRaw(self,s):
		for line in s.split("\n"):
			self.printraw(line)	
				
###    %	Description          Example

###    %A	account              "john"
###    %B	name of board        "[#1: the Meeting Place]"
###    %C	print a cookie       <prints a cookie>
###    %D	date                 "27-Jul-92"
###    %F	first name           "Francesco"
###    %G	group(s)             "42"
###    %L	fake level           "NiNE"
###    %M	moves                "14"
###    %N	message base         "1"
###    %O	time left online     "58"
###    %P	privilege            "0"
###    %R	rank or remark       "100 billion bottles"
###    %S    time spent online    "2"
###    %T	time                 "6:29p"
###    %U	user index in pw     "61"
###    %V    version              "1.65"
###    %W	who (identity)       "Jose Jimenez"
###    %Z	print Zippy cookie   <prints a cookie>

###    %a	access level         "6"
###    %b	modem speed "baud"   "2400", or "LOCAL"
###    %c	user calls           "56"
###    %d	device number        "1"
###    %e	editor		     "vi"
###    %f    file directory       "/files"
###    %i	input line           "something someone typed"
###    %l	last caller          "Dan Quayle"
###    %m	new local messages   "31"
###    %n	node name            "unknown.UUCP"
###    %o	organization         "Kentucky Fried BBS +1 408 245 SPAM"
###    %p	user posts           "5"
###    %r	k received (UL'd)    "315"
###    %s	k sent (DL'd)        "1771"
###    %t	terminal type        "vt100"
###    %u	UUCP name            "vegas"
###    %v	voting number        "91"
###    %x	transfer protocol    "X"

###    %!	system calls         "51455"
###    %$	system posts	     "14201"
###    %#	user's telephone     "408/767-1506"
###    %@	last call date       "22-Jul-89  5:08"
###    %?	[chat] attempted     "[chat]"

###    %[	lowest message       "1401"
###    %=	current message      "1457"
###    %+	next message         "1458"
###    %]	highest message      "1460"

###    %|	carriage return      <carriage return>
###    %^	caret                "^"
###    %%	percent sign         "%"

###  ^	toggle inverse on/off, ONLY if vt100 mode (DOS) or
### 	the terminal supports emphasized printing (Unix termcap).

###    %j	is used only if you have the voting booth, and will
###     	display a message if there is a new topic.
		