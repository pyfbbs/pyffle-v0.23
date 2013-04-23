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
from pyffle_question import PyffleQuestion
from pyffle_exception import PyffleException
from datetime import datetime
import signal
import sys
import getpass
import os
import copy
import traceback
from pyffle_dispatch import PyffleDispatch

class PyffleMain:
	warnOnSecurity = False					## If True, prints warning to user on permission failure
	failQuietly = True						## If False, exits on unhandled exceptions
	words = {}
	info = {}
	help = {}
	menus = {}
	system = {}
	text = {}

	petsciiSupport = False					## EXPERIMENTAL. FIXME: Pull out of static
	errorCount = 0							## Used by the error logger, if it catches more than
	maxErrors  = 5 							## maxErrors without seeing a prompt, we're probably in 
											## an error loop and should terminate
	
	## CONFIG: Configure any additional plugins here
	##		   Format: <keyword> : ["module name", "description", Permissions ]
	
	modulelist = {"gui" :  ["pyffle_ui", "Graphical menu", [] ],
				  "page" :  ["pyffle_voice", "Voice", [] ],
				  "mail" : ["pyffle_mail", "Mail",[]],
				  "sethost" : ["pyffle_sethost","Connect to a HECNET host, HECNET to see list of hosts",[]],
				  "llogin" : ["pyffle_lat","Connect to a LAT host, ^LSERVICES^ to see list of hosts",[]],
				  "lservices" : ["pyffle_lat","List LAT hosts",[]],
				  "!decnode" : ["pyffle_doors","Run DOS doors",[{"LEVEL":90},"OPERATOR"]],
				  "doors" : ["pyffle_doors","Run DOS doors",[]],
				  "all" : ["pyffle_allboard","Show ALL boards",[{"LEVEL":90},"OPERATOR"]],
				  "validate" : ["pyffle_useradmin","Validate users",[{"LEVEL":90},"OPERATOR"]],
				  "useredit" : ["pyffle_useradmin","Edits users",[{"LEVEL":90},"OPERATOR"]],
				  "acledit" : ["pyffle_useradmin","Edits ACLs",[{"LEVEL":90},"OPERATOR"]],
				  "example" : ["pyffle_example","Development example",[{"LEVEL":90},"OPERATOR"]],
				  "sims" : ["pyffle_sims","Development example",[{"LEVEL":90},"OPERATOR"]],
				  "chat" : ["pyffle_chat","PyffleChat",[]],
				  "kill" : ["pyffle_useradmin","Deletes user",[{"LEVEL":90},"OPERATOR"]],
				  "empty" : ["pyffle_boardadmin","Empties board",[{"LEVEL":90},"OPERATOR"]],
				  "drop" : ["pyffle_boardadmin","Drops board",[]],
				  "iuser" : ["pyffle_inspector","Object inspector (users)",[{"LEVEL":90},"OPERATOR"]],
				  "iboard" : ["pyffle_inspector","Object inspector (boards)",[{"LEVEL":90},"OPERATOR"]],
				  "_dispatchcheck" : ["pyffle_dispatchtest","<Event handler: Debug>",[{"LEVEL":90},"OPERATOR"]],
				  "_mailcheck" : ["pyffle_mailcheck","<Event handler: New Mail Check>",[{"LEVEL":90},"OPERATOR"]],
				  "create" : ["pyffle_boardadmin","Creates new board",[]],
				  "pgstats" : ["pyffle_stats","Database statistics",[{"LEVEL":90},"OPERATOR"]],
				  "menutest" : ["pyffle_menutest","Database statistics",[{"LEVEL":90},"OPERATOR"]],
				  "systats" : ["pyffle_stats","OS statistics",[{"LEVEL":90},"OPERATOR"]],
				  "stats" : ["pyffle_stats","System statistics",[{"LEVEL":90},"OPERATOR"]],
				  "finger" : ["pyffle_finger", "Show information on other users",[]],
				  "plan" : ["pyffle_finger", "Post a plan",[]],
				  "mission" : ["pyffle_mission", "Generate instant Corporate Bullshit",[]],
				  "select" : ["pyffle_boards", "Select a board",[]],
				  "reset" : ["pyffle_boards", "Resets the last NEW scan",[]],
				  "new" : ["pyffle_boards", "Shows new messages in boards",[]],
				  "online" : ["pyffle_online", "Currently logged in users",[]],
				  "!reset" : ["pyffle_online", "System reset - %41%37WARNING!%0 kills all messages, flushes the tubes",[{"LEVEL":90},"OPERATOR"]],
##				  "_dump" : ["pyffle_pm", "Reset currently logged in users",[{"LEVEL":90},"OPERATOR"]],
				  "join" : ["pyffle_join", "Configure your NEW scan",[]],
				  "post" : ["pyffle_boards", "Post a message",[]],
				  "searchall" : ["pyffle_boards", "Search posts",[]],
				  "search" : ["pyffle_boards", "Search posts",[]],
				  "adminsearch" : ["pyffle_boards", "Search posts",[{"LEVEL":90},"OPERATOR"]],
				  "addmember" : ["pyffle_groupadmin", "Adds member to group",[{"LEVEL":90},"OPERATOR"]],
				  "dropmember" : ["pyffle_groupadmin", "Drops member from group",[{"LEVEL":90},"OPERATOR"]],
				  "dropgroup" : ["pyffle_groupadmin", "Drops group",[{"LEVEL":90},"OPERATOR"]],
				  "creategroup" : ["pyffle_groupadmin", "Creates group",[{"LEVEL":90},"OPERATOR"]],
				  "showgroups" : ["pyffle_groupadmin", "Creates group",[{"LEVEL":90},"OPERATOR"]],
				  "read" : ["pyffle_boards", "Read posts",[]],
				  "scan" : ["pyffle_boards", "Scan for new posts",[]],
				  "pm": ["pyffle_pm", "Send an online PM to another user",[]],
				  "yoof": ["pyffle_yoof", "Scribble on wall",[]],
				  "wall": ["pyffle_pm", "Spam an online PM to all logged in users",[]],
##				  "addcookie" : ["pyffle_cookie", "Stores a cookie",[]],
				  "oreo" : ["pyffle_cookie", "A tasty wholesome snack",[]],
				  "date" : ["pyffle_os","Calls OS date",[{"LEVEL":90},"OPERATOR"]],
				  "pcerase" : ["pyffle_os","Changes erase character to PC backspace",[]],
				  "unixerase" : ["pyffle_os","Changes erase character to UNIX backspace",[]],
				  "status" : ["pyffle_status","Show/edit user's account information",[]],				  
				  "users" : ["pyffle_userlist","Shows list of users",[]],				  
				  "bash" : ["pyffle_os","Calls OS bash",[{"LEVEL":90},"OPERATOR"]],
				  "nethack" : ["pyffle_os","Calls OS nethack",[{"LEVEL":90},"OPERATOR"]],
				  "backgammon" : ["pyffle_os","Calls OS backgammon",[{"LEVEL":90},"OPERATOR"]],
				  "alpine" : ["pyffle_os","Calls OS alpine",[{"LEVEL":90},"OPERATOR"]],
				  "ls" : ["pyffle_os","Calls OS ls",[{"LEVEL":90},"OPERATOR"]],
				  "clear" : ["pyffle_os","Clears the screen",[]],
				  "google" : ["pyffle_os","Search the Interwebs",[]],
				  "uptime" : ["pyffle_os","Calls OS uptime",[{"LEVEL":90},"OPERATOR"]],
				  "cpm" : ["pyffle_os","Connects you to the CP/M-O-Tron (Once CP/M is running, you can't exit.)",[]],
				  "feedback" : ["pyffle_feedback","Feedback",[]],
				  "version" : ["pyffle_version","Version information",[]],
				  "cookie" : ["pyffle_cookie","Cookie",[]]}
	modules = {}
	for moduleName in modulelist.keys():
		theModule = __import__(modulelist[moduleName][0])
		modules[moduleName] = theModule
	
	def operatorModule(self,name):
		rv = False
		module = self.modulelist[name]
		#print "Security=" + str(module[2])
		security = module[2]
		if len(security) == 2:
			#print "Security tagged"
			if security[1] == "OPERATOR":
				#print "Operator command"
				rv = True
		return rv
		
	def moduleSecurityCheck(self,name):
		self.data.util.debugln("Security check for " + name)
		## load our ACL
		theAcl = self.data.getAcl(self.currentUser.aclid)
		## do we have the SYSOP priv?
		if self.data.isGranted(theAcl,self.currentUser.username,"SYSOP"):
			## we're a sysop, don't need to process anything more
			self.data.logEntry(self.data.LOGINFO,"INVOKE/SYSOP/PASS",str(self.currentUser.username),"SYSOP: %s invoked %s" % (str(self.currentUser.username),str(name)))
			return True
		self.data.util.debugln("Not sysop")
		rv = True
		## ["pyffle_useradmin","Edits users",[{"LEVEL":90},"OPERATOR"]]
		moduleEntry = self.modulelist[name]
		moduleSecurity = moduleEntry[2]
		if moduleSecurity == []:
			rv = True
		else:
			## We assume that we are to ignore the level, and only look at ACLs
			minLevel = -1
			
			self.data.util.debugln("Checking level..")
			## Look for the level in the general requirements dictionary
			generalReqs = moduleSecurity[0]
			if not generalReqs == None:
				for key in generalReqs.keys():
					if key == "LEVEL": ## Got it?
						self.data.util.debugln("Level found")	
						minLevel = generalReqs["LEVEL"] ## Yup, this is the minimum level for access
						self.data.util.debugln("current=%s, required=%s" % (self.currentUser.accesslevel , minLevel))

						if  self.currentUser.accesslevel < minLevel: ## Does the user have it?
							self.data.logEntry(self.data.LOGNORMAL,"INVOKE/FAIL/NOLEVEL",str(self.currentUser.username),"%s failed to invoke %s, does not meet level req" % (str(self.currentUser.username),str(name)))
							rv = False 
							self.data.util.debugln("Level too low, failing")
							return rv					## No, stop processing
			## User meets level requirements				
			## now let's look to see if the user has the required ACL entries?
			for i in range(1,len(moduleSecurity)):
				perm = moduleSecurity[i]
				self.data.util.debugln("Checking perm " + str(perm))
				if not self.data.isGranted(theAcl,self.currentUser.username,perm):
					self.data.logEntry(self.data.LOGNORMAL,"INVOKE/FAIL/NOLEVEL",str(self.currentUser.username),"%s failed to invoke %s, does not have %s" % (str(self.currentUser.username),str(name),str(perm)))
					rv = False
					return rv
		## if we get here, we should be returning true.
		self.data.logEntry(self.data.LOGINFO,"INVOKE/PASS",str(self.currentUser.username),"%s invoked %s" % (str(self.currentUser.username),str(name)))

		return rv
					 
				
	mtalist = [["pyffle_mta_uucp","Pyffle UUCP","UUCP MTA for Pyffle"],
				["pyffle_mta_ftn","Pyffle FTN","FTN MTA for Pyffle"]]
	
	session = None
	data = None
	currentUser = None
	
	def welcomeMessage(self):
		self.data.stateChange("welcomemsgstart")
		self.data.util.cls()
		self.data.util.println(self.text['entry'])
		self.data.stateChange("welcomemsgend")
		
	
	def registerUser(self):
		self.data.stateChange("registerstart")
		questions = PyffleQuestion()
		questions.data = self.data
		answers = questions.go(self.system["signup"])
		self.data.stateChange("registerpostsignup")

		userOk = self.data.registerUser(answers)				
		if not userOk == None:
			## Data didn't like the answers
			self.data.stateChange("registerproblem")		
			self.data.util.println("Problem with your registration: " + userOk)
			self.data.util.prompt("\nPress Return..")
		else:
			self.data.stateChange("registerok")
			self.data.util.prompt("\nThanks for that. Press Return to continue.")	
			self.data.util.cls()
			self.data.util.printPaged(self.text["newusers"])
			self.data.util.prompt("")
		self.data.stateChange("registerdone")
		
		
		
	def logError(self,s,exc):
		rv = True
		if not self.data == None:
			self.data.stateChange("errorstart")		
			if not self.data.util == None:
				self.data.util.println("\nHmm, bork. " + s)
				tbContents = traceback.format_exc(exc)
				self.data.util.debugln(tbContents)
				self.data.logEntry(self.data.LOGCRIT,"ERROR/CAUGHT",str(self.currentUser.username),tbContents)
			self.data.stateChange("errorend")		

		self.errorCount = self.errorCount + 1
		if self.errorCount > self.maxErrors:
			self.data.logEntry(self.data.LOGCRIT,"ERROR/PHAIL",str(self.currentUser.username),"***** IN AN ERROR LOOP ***** ABORTING, EPIC LULZ!")
			rv = False ## We're in an error loop, let's get out of here

		else:
			print "\nHmm, bork. " + s
		return rv
		

	def login(self):
		self.data.stateChange("loginstart")		

		self.welcomeMessage()
		
		loggedIn = False

		while not loggedIn:
			self.data.stateChange("loginloopstart")		

			
			self.data.stateChange("loginpromptstart")		
			enteredName = self.data.util.prompt(self.data.static.options["login"])
			enteredName = enteredName.strip()
			enteredName = enteredName.lower()
			self.data.stateChange("loginpromptend")		
			if enteredName == "new":
				self.data.stateChange("loginnewuser")		
				self.registerUser()
				continue
			else:
				self.data.stateChange("loginnormaluser")		
				user = self.data.getUser(enteredName)			
				self.data.stateChange("loginpasswordprompt")		
				p = self.data.util.readPassword(prompt="Password: ")
				self.data.stateChange("loginpostpasswordprompt")		
				if not user == None:		
					self.data.stateChange("loginfounduser")		
					if user.password.lower() == p.lower():
						self.data.stateChange("loginpasswordok")		
						
						## check for DISUSER flag
						userAcl = self.data.getAcl(user.aclid)
						if self.data.isDenied(userAcl,user.username,"LOGIN"):
							self.data.stateChange("loginfaildisuserstart")								
							self.data.logLoginFail(enteredName,"DISUSER")
							self.data.stateChange("loginfaildisuserend")		
						else:
							loggedIn = True
							self.currentUser = user
							self.data.currentUser = self.currentUser
							self.data.util.currentUser = self.currentUser
							self.data.stateChange("loginlogcallstart")								
							self.data.logCall()
							self.data.stateChange("loginlogcallend",[user.username])								
							self.data.util.cls()
							self.data.util.println(self.text["welcome"])
							self.data.stateChange("loginwelcomeend")								
							
							## Pick the first board in the systme to be current
							boards = self.data.getBoards()
							for board in boards:
								if not board.name.startswith('__'):
									self.data.setCurrentBoard(board.name)
									break 
					else:
						self.data.stateChange("loginfailbaduserstart")								
						self.data.logLoginFail(enteredName)
						self.data.stateChange("loginfailbaduserend")								
						
				else:
					self.data.stateChange("loginfailnouserstart")								
					if enteredName == "":
						enteredName = "<none>"
					self.data.logLoginFail(enteredName)	
					self.data.stateChange("loginfailbaduserend")								

			if not loggedIn:
				self.data.stateChange("loginprinterrorstart")								
				self.data.util.println("Incorrect credentials. Try again.")
				self.data.stateChange("loginprinterrorend")								

			self.data.stateChange("loginloopend")								
		self.data.stateChange("loginend")								

	def printLogoutMessage(self):		
		self.data.stateChange("logoutmsgstart")								
		self.data.util.println(self.text["logout"])
		self.data.stateChange("logoutmsgend")								
		
		
	def mainmenu(self):
		self.data.stateChange("mainmenustart")
		userQuits = False
		while not userQuits:
			try:
				self.data.stateChange("mainmenuloopstart")
				self.data.stateChange("mainmenupromptstart")
				self.data.stateChange("mainmenuprompt")
				s = self.data.util.prompt(self.data.static.options["prompt"])
				self.data.stateChange("mainmenupromptend")
				## managed to get user input, reset the error count as we're not in an error loop
				self.errorCount = 0
				s = s.strip()
				choice = ""
				args = []
				if not s == "":
					args = s.split()
					choice = args[0].lower()
				validChoice = False

				if choice == "!eval":
					if self.data.currentUser.username == "system":
						code = ""
						for arg in args[1:]:
							code = code + arg + " "
						print "!EVAL |%s| -> " % (code)
						print "  " + str(eval(code))
						validChoice = True
						
				## Boardnames are case sensitive for now
				boardNames = self.data.getBoardNames()
				if choice in boardNames:
					self.data.stateChange("mainmenupromptchangeboardstart")
					validChoice = self.data.setCurrentBoard(choice)
					self.data.stateChange("mainmenupromptchangeboardend")
					if validChoice:
						continue
						
				## Commands are case insensitive
				choice = choice.lower()	
				if choice in self.modulelist.keys():
					if self.moduleSecurityCheck(choice):
						self.data.stateChange("mainmenuinvokestart " + str(choice))
						###self.data.util.prompt("Running " + choice + "..")
						chosenModule = self.modules[choice]
						pyfflePluginInstance = chosenModule.PyffleModule()
						pyfflePluginInstance.currentUser = self.currentUser
						pyfflePluginInstance.data = self.data
						pyfflePluginInstance.go(choice,args)
						validChoice = True
						self.data.stateChange("mainmenuinvokeend " + str(choice))
						
					else:
						if self.warnOnSecurity:
							self.data.stateChange("mainmenuinvokesecuritystart " + str(choice))
							self.data.util.printn("\nPERMISSION DENIED: %s. \nThat's like, verboten, man.\n\n" % (choice))
							validChoice = True
							self.data.stateChange("mainmenuinvokesecurityend " + str(choice))
	
				if choice == "?":
					self.data.stateChange("mainmenuhelpstart")
					self.data.util.printn(self.menus["main"])				
					validChoice = True
					self.data.stateChange("mainmenuhelpend")
	
				if choice == "!logs":
					self.data.stateChange("mainmenulogsstart")

					validChoice = True
					numEntries = 22
					level = -1
					if len(args) >= 2:
						numEntries = int(args[1])
					if len(args) >= 3:
						level = int(args[2])
					entries = self.data.getLog(num=numEntries,level=level)
					for entry in entries:
						for s in entry:
							if len(str(s)) > 2:
								self.data.util.printn("{0:20} ".format(str(s)))
							else:
								self.data.util.printn("{0:5} ".format(str(s)))
						self.data.util.println("")
					self.data.stateChange("mainmenulogsend")

				if choice == "petscii":
					self.data.util.petsciiMode = not self.data.util.petsciiMode 
					validChoice = True
		
				if choice == "list":
					self.data.stateChange("mainmenuliststart")
					validChoice = True
					callers = self.data.getLastUsers()
					for caller in callers:
						self.data.util.println("{0:<12}  ".format(caller[0]) + self.data.util.formatDateTimeString(caller[1]))
					self.data.stateChange("mainmenulistend")
					
				if choice == "help":
					self.data.stateChange("mainmenuhelpstart")
					self.data.util.helpMenu(self.help)
					validChoice = True	
					self.data.stateChange("mainmenuhelpend")
	
				if choice == "info":
					self.data.stateChange("mainmenuinfostart")
					self.data.util.helpMenu(self.info,header=self.info["menu"],prompt="Topic? ",listwords=False)
					validChoice = True	
					self.data.stateChange("mainmenuinfoend")
					
				if choice == "!!error":
					self.data.stateChange("mainmenuerrorstart")
					
					## This will raise an error, used to test the error logging functions
					foo = [0,1]
					bar = foo[2]
					self.data.stateChange("mainmenuerrorend")
					
					
				if choice == "!loadtxts":
					self.words =  self.data.util.loadWords("WORDS")		## FIXME should be from static
					self.info =   self.data.util.loadWords("INFO")
					self.help =   self.data.util.loadWords("HELP")
					self.menus =  self.data.util.loadWords("MENUS")
					self.text =   self.data.util.loadWords("TEXT")
					self.system = self.data.util.loadWords("SYSTEM")
					self.data.util.texts["WORDS"] = self.words
					self.data.util.texts["INFO"] = self.info
					self.data.util.texts["HELP"] = self.help
					self.data.util.texts["MENUS"] = self.menus
					self.data.util.texts["TEXT"] = self.text
					self.data.util.texts["SYSTEM"] = 	self.system	
					validChoice = True
					
				if choice == "!!phail":
					self.data.stateChange("mainmenuphailstart")

					## This will raise an error, used to test the error logging functions
					self.errorCount = self.maxErrors + 1
					foo = [0,1]
					bar = foo[2]
					self.data.stateChange("mainmenuphailend") # shoud NEVER be here, but hey

					
				if choice == "commands":
					self.data.stateChange("mainmenucommandsstart")
					try:
						self.modulelist["bye"] = ["___","Log off the system",[]]
						self.modulelist["modules"] = ["___","Show loaded modules",[{"LEVEL":90},"OPERATOR"]]
						moduleNames = self.modulelist.keys()
						moduleNames.sort()
						self.data.util.println("")
						outs = ""
						for moduleName in moduleNames:
							if self.moduleSecurityCheck(moduleName):
								if self.operatorModule(moduleName):	
									outs = outs + "%37{0:20}%0".format(moduleName.upper()) + self.modulelist[moduleName][1] + "\n"
								else:
									outs = outs + "%36{0:20}%0".format(moduleName.upper()) + self.modulelist[moduleName][1] + "\n"
						outs = self.data.util.expandText(outs)
						self.data.util.printPagedRaw(outs + "\n")
						validChoice = True
					except KeyboardInterrupt:
						## we don't want to propagate the event state in case
						## the user breaks in the pager - we have badly defined
						## modules in the list
						pass
					finally:
						del self.modulelist["bye"]
						del self.modulelist["modules"]

					self.data.stateChange("mainmenucommandsend")
				
					
						
				if choice == "modules":
					self.data.stateChange("mainmenumodulesstart")
				
					moduleNames = self.modulelist.keys()
					moduleNames.sort()
					self.data.util.println("\nModules loaded:\n")
	
					for moduleName in moduleNames:
						m = self.modules[moduleName]
						self.data.util.println("%35{0:20}%0".format(moduleName.upper()) + m.getIdentity())
					self.data.util.println("\n^Total^ " + str(len(moduleNames)) + " modules")	
					validChoice = True								
					self.data.stateChange("mainmenumodulesend")
				
				if choice == "bye":
					self.data.stateChange("mainmenubyestart")
				
					self.printLogoutMessage()
					self.data.logLogout()
					userQuits = True
					validChoice = True		
					self.data.stateChange("mainmenubyeend")
				
				if choice in self.words.keys():
					self.data.stateChange("mainmenuwordsstart")
					self.data.util.printPaged(self.words[choice])
					validChoice = True
					self.data.stateChange("mainmenuwordsend")
				
				if choice == "":
					self.data.stateChange("mainmenuempty")				
					validChoice = True 		## It's not a choice, but dont error either ..		
				
				self.data.util.lastInput = choice	
				
				if not validChoice:
					self.data.stateChange("mainmenuerrorstart")				

					self.data.util.println(self.data.static.options["error"])
					self.data.stateChange("mainmenuerrorend")				

			except KeyboardInterrupt: 
				self.data.stateChange("mainmenubreakstart")				

				self.data.util.println("\n\n^BREAK^")
				self.data.stateChange("mainmenubreakend")
					
			except PyffleException:
				pass

			except:
				self.data.stateChange("mainmenuborkstart")				

				theError = sys.exc_info()
				loopStatus = self.logError("Unexpected error: " + str(theError[0]) + " " + str(theError[1]),theError[2])
				if not loopStatus:
					self.data.stateChange("mainmenuborkenloop")				

					print "***** ERROR LOOP, EXITING *****"
					return
				if not self.failQuietly:
					self.data.stateChange("mainmenuborkdie")				
					## We're going down, print the stack trace
					## FIXME: this should really go to a logfile
					print "\n\n\n***** GURU MEDITATION: " + str(theError[0]) + " " + str(theError[1]) + " *****\n\n"
					traceback.print_tb(theError[2])
					return
				self.data.stateChange("mainmenuborkend")				
	

		
	def go(self):
		static = PyffleStatic()
		## FIXME read this from a env var or something
		static.parse("/pyffle/static")
		
		Session = sessionmaker()
		
		##		engine = create_engine('postgresql://postgres:f00btron@localhost/pyffledev', echo=False)
		engine = create_engine(static.options['pyffle.dburl'], echo = False)
		Session.configure(bind=engine)
		
		self.session = Session()
		util = PyffleUtil()
		self.data = PyffleData()
		self.data.LOGLEVEL = self.data.LOGNORMAL;
		self.data.static = static
		self.data.session = self.session
		self.data.util = util
		util.data = self.data
		dispatcher = PyffleDispatch()
		dispatcher.setup(self.data,self.modules,self.modulelist)
		self.data.setDispatcher(dispatcher)
		self.data.stateChange("startup")

		self.words =  util.loadWords("WORDS")		## FIXME should be from static
		self.info =   util.loadWords("INFO")
		self.help =   util.loadWords("HELP")
		self.menus =  util.loadWords("MENUS")
		self.text =   util.loadWords("TEXT")
		self.system = util.loadWords("SYSTEM")
		util.texts["WORDS"] = self.words
		util.texts["INFO"] = self.info
		util.texts["HELP"] = self.help
		util.texts["MENUS"] = self.menus
		util.texts["TEXT"] = self.text
		util.texts["SYSTEM"] = 	self.system	
		self.data.stateChange("wordsloaded")

		mtalist = [["pyffle_mta_uucp","Pyffle UUCP","UUCP MTA for Pyffle"],
				["pyffle_mta_ftn","Pyffle FTN","FTN MTA for Pyffle"]]
		self.data.loadMtaList(mtalist)
		#msg1 = self.data.createMessage("fooble","sampsa","Test from py","Hello earth")
		#msg2 = self.data.createMessage("foo@bar.com","sampsa","Test to outside","Hello sky")
		self.data.stateChange("mtasloaded")

		if self.petsciiSupport:
			choice = self.data.util.prompt("\n[P]ETSCII / [A]SCII?")
			choice = choice.lower().strip()
			if choice == "p":
				self.data.util.petsciiMode = True
				## Enable shift on the remote terminal
				print chr(0x0e)
			
		self.data.stateChange("prelogin")
		self.login()
		
		self.data.stateChange("premainmenu")
		self.mainmenu()
		self.data.stateChange("postmainmenu")
		self.data.stateChange("exit")
		
		
def handler(signum, frame):
    print 'Signal handler called with signal', signum
    raise IOError("We're done here")


def runmain():
	### Main program
	pyffleMain = PyffleMain()
	signal.signal(signal.SIGHUP, handler)	
	try:
		pyffleMain.go()
	finally:
		if not pyffleMain.data == None:
			if pyffleMain.data.loggedIn:
				pyffleMain.data.logLogout()


import cProfile
cProfile.run("runmain()","/pyffle/data/main.profile")
