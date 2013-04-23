

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
import base64
from threading import Timer
import pyfflermi 
import sys
class pyfflermiserver:
	cmd = None
	cmddata = None
	loggedIn = False
	actionTable = {}
	currentUser = None


	def setupPyffleConnection(self):
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
		self.data.static = static
		self.data.session = self.session
		self.data.util = util
		util.data = self.data
		dispatcher = PyffleDispatch()
		dispatcher.setup(self.data,{},{})
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
		self.data.stateChange("mtasloaded")
		self.lastCheck = datetime.now()
	def setAction(self,msg,method):
		self.actionTable[msg] = method


	def processData(self,line):
		line = line.strip()
		isCommand = False
		if line.find("!|!") == 0:
			isCommand = True
			if isCommand:
				self.cmd = line
				#print "New command: |" + self.cmd + "|"
				self.alive = True
		else:
			if self.cmd == None:
				pass	#print "Spurious data"
			else:
				self.cmddata = line
				#print "Data: |" + self.data + "|"
				if self.cmd == "!|!Logout":
					## other side is logging out
					return False
				if self.cmd in self.actionTable.keys():
					cmdMethod = self.actionTable[self.cmd]
					cmdMethod(self.cmddata)
					self.cmd = None
		return True
		
	def processMessageHeader(msgdata):
	 	#print "GOT MESSAGEHEADER: " + str(msgdata)
		msg = MessageHeader()
		msg.dejsonify(msgdata)
		msg.foo()
	
	def processMessage(msgdata):
		#print "GOT MESSAGE: " + str(msgdata)
		msg = Message()
		msg.dejsonify(msgdata)
		msg._dump()

	alive = True
	deathTimer = None
	TIMEOUT = 60.0
	def checkDeath(self):
		if self.alive:
			self.alive = False
			self.deathTimer = Timer(self.TIMEOUT,self.checkDeath) 
			self.deathTimer.start()
		else:
			print '!*!CLIENTDIED\n{reason: "timeout"}'
			os._exit(-1)
			
	def mainloop(self):
		## read input
		print "!|!PYFFLEGUI 0.23 wtf"
		LoggedOut = False
		self.deathTimer = Timer(self.TIMEOUT,self.checkDeath) 
		self.deathTimer.start()
		while not LoggedOut:
			line = sys.stdin.readline()
			loggedIn = self.processData(line)
			if not loggedIn:
				LoggedOut = True
		logoutMessage = pyfflermi.ServerResult(0,"Goodbye.")
		response = pyfflermi.getMessage(logoutMessage)
		print response
		os._exit(0)
		
			
	def userlist(self,s):
		usernamelist = []
		users = self.data.getUsers()
		for user in users:
			usernamelist.append(user.username)
		thelist = pyfflermi.Userlist(usernamelist)
		response = pyfflermi.getMessage(thelist)
		print response
	
	import datetime
	
	def addToChatList(self,username):			
		chatlist = self.data.pluginReadSystem("pyffle_chat_list")
		if chatlist == None:
			chatlist = username + "\n"
		else:
			chatlist = chatlist + username + "\n"
		self.data.pluginWriteSystem("pyffle_chat_list",chatlist)
		self.removeFromChatList("None")

	def getChatList(self):
		chatlist = str(self.data.pluginReadSystem("pyffle_chat_list"))
		users = chatlist.split("\n")
		rv = []
		for user in users:
			user = user.strip()
			if not user == "":
				rv.append(user)
		return rv
		
	def removeFromChatList(self,username):
		chatlist = str(self.data.pluginReadSystem("pyffle_chat_list"))
		users = chatlist.split("\n")
		newchatlist = ""
		for user in users:
			if not user.strip() == username.strip():
				newchatlist = newchatlist + user + "\n"
		self.data.pluginWriteSystem("pyffle_chat_list",newchatlist)
	
	def chatupdaterequest(self,s):
		## we don't care about the data in the request, we don't do rooms yet
		req = pyfflermi.ChatUpdateRequest()
		req.dejsonify(s)
		status = req.room
		print "STATUS |" + status + "|"
		if status.strip().lower() == "enter":
			self.addToChatList(self.currentUser.username)
		if status.strip().lower() == "exit":
			self.removeFromChatList(self.currentUser.username)

		res = pyfflermi.ChatUpdateResult()
		## except if this is an enter or exit message
			
		chatBoard = self.data.getBoardByName("__pyffle_chat")
		self.newmsgids = self.data.getMessagesSince(chatBoard,self.lastCheck,checkSrm = False)
		newmessages = []
		for msgid in self.newmsgids:
			msg = self.data.getMessage(msgid)
			msgtext = []
			while msgtext == []:  ## due to DB delays, the msg text might not be stored yet whilst the messge is..
				msgtext = self.data.getMessagetexts(msgid)
			newmessages.append((msg.fromname,msgtext[0]))
		self.lastCheck = datetime.now()	
		res.newmessages = newmessages

		users = self.getChatList()
		res.users = users
		
		response = pyfflermi.getMessage(res)
		print response
		
	def boardlist(self,s):
		print "DATA=" + str(self.data)
		thelist = pyfflermi.Boardlist(self.data.getBoardNames())
		response = pyfflermi.getMessage(thelist)
		print response
	
	def chatmessage(self,s):
		chatmsg = pyfflermi.ChatMessage("")
		chatmsg.dejsonify(s)
		self.data.createMessage(self.currentUser.username,None,"chat message",chatmsg.msg,board='__pyffle_chat')	
		sysres = pyfflermi.ChatMessageResult(0,"")
		response = pyfflermi.getMessage(sysres)
		print response				
		
	def onlinelist(self,s):
		names = []
		for entry in self.data.getCurrentlyonEntries():
			names.append(entry.username)
		thelist = pyfflermi.Onlinelist(names)
		response = pyfflermi.getMessage(thelist)
		print response
	
	def messagecount(self,s):
		print "S=" + str(s)
		req = pyfflermi.MessagecountRequest()
		req.dejsonify(s)
		#print "Looking at board: " + req.boardname
		count = self.data.getBoardMessageCount(req.boardname)
		msg = pyfflermi.MessagecountResult(count,req.boardname)
		response = pyfflermi.getMessage(msg)
		print response


	def messagelist(self,s):
		print "S=" + str(s)
		req = pyfflermi.MessagelistRequest()
		req.dejsonify(s)
		#print "Looking at board: " + req.boardname
		msgids = []
		if req.boardname == "__pyffle_email":
			#print "Username=" + self.currentUser.username
			msgids = self.data.getMessagesByUser(self.currentUser.username)
			#print "SENDING MSGIDS " + str(msgids)
		else:
			msgids = self.data.getMessagesByBoardname(req.boardname)
			print "Non email board, ids: " + str(msgids)
		thelist = pyfflermi.Messagelist(msgids)
		response = pyfflermi.getMessage(thelist)
		print response


	def clientmessage(self,s):
		print "S=" + str(s)
		req = pyfflermi.ClientMessage()
		req.dejsonify(s)
		print "Posting to board " + req.boardname
		self.data.createMessage(req.fromHdr,req.toHdr,req.subject,req.text,req.boardname)
		sysres = pyfflermi.ServerResult(100,"Posted")
		response = pyfflermi.getMessage(sysres)
		print response

	def checkLogin(self,username,password):
		rv = False
		user = self.data.getUser(username)			
		if user == None:
			#print "No such user: " + username
			rv = False
		else:
			#print "Found user"
			if user.password.lower() == password.lower():
				print "Passwords match, we're good"
				self.currentUser = user
				self.data.currentUser = self.currentUser
				self.data.util.currentUser = self.currentUser
				self.data.logCall()
				rv = True
			else:
				rv = False
				#print "Password mismatch"
		return rv
	def loginrequest(self,s):
		#print "S=" + str(s)
		req = pyfflermi.LoginRequest("","")
		req.dejsonify(s)
		#print "Username: " + str(req.username)
		#print "Password: " + str(req.token)
		outmsg = None
		if self.checkLogin(req.username,req.token):
			outmsg = pyfflermi.LoginResult(1,"Welcome to hq.pyffle.com")
			self.loggedIn = True
			self.data.setCurrentlyonActivity("GUI Mode")
		else:
			outmsg = pyfflermi.LoginResult(-1,"Invalid credentials")
		response = pyfflermi.getMessage(outmsg)	
		print response


	def messagerequest(self,s):
		print "S=" + str(s)
		req = pyfflermi.MessageRequest()
		req.dejsonify(s)
		print "Getting message texts: " + str(req.msgid)
		msgtexts = self.data.getMessagetexts(req.msgid)
		msgattaches = []
		outmsg = pyfflermi.Message(req.msgid,msgtexts,msgattaches)
		response = pyfflermi.getMessage(outmsg)	
		print response

	def messageheader(self,s):
		print "S=" + str(s)
		req = pyfflermi.MessageHeaderRequest()
		req.dejsonify(s)
		print "Getting message: " + str(req.msgid)
		msg = self.data.getMessage(req.msgid)
		outmsg = pyfflermi.MessageHeader(req.msgid,msg.fromname,msg.toname,msg.subject,msg.readbyrecipient,str(msg.sentdate))
		response = pyfflermi.getMessage(outmsg)	
		print response

	images = {"logo" : "hqlogo.png"}
	
	def imagerequest(self,s):
		print "S=" + str(s)
		req = pyfflermi.ImageRequest()
		req.dejsonify(s)
		filename = self.images[req.imagename]
		f = open(filename)
		data = f.read()
		f.close()
		payload = base64.b64encode(data)
		payload = payload.replace("\n","")
		outmsg = pyfflermi.Image(payload)
		response = pyfflermi.getMessage(outmsg)	
		print response


	def getPms(self):
		pmBoard = self.data.getBoardByName("__pyffle_pm")
		msgids = self.data.getMessagesByBoardByToUsername(pmBoard,self.currentUser.username)
		rv = None
		if len(msgids) > 0:
			msgid = msgids[0]
			msg = self.data.getMessage(msgid)
			rv = pyfflermi.PrivateMessage()
			rv.fromName = msg.fromname
			rv.toName = msg.toname
			rv.text = msg.subject
			self.data.toolMode = True
			self.data.deleteMessage(msgid)
			self.data.toolMode = False			  
		return rv
		
	def privatemessage(self,s):
		msg = pyfflermi.PrivateMessage()
		msg.dejsonify(s)
		self.data.createMessage(msg.fromName,msg.toName,msg.text,"<PM>",board='__pyffle_pm')
		resmsg = pyfflermi.ServerResult(110,"PM sent")
		response = pyfflermi.getMessage(resmsg)
		print response
		
	def poll(self,s):
		pm = self.getPms()
		themsg = None
		if pm == None:	
			themsg = pyfflermi.ServerResult(0,"Ping")
		else:
			themsg = pm
		response = pyfflermi.getMessage(themsg)
		print response
		
	def foo(self,s):
		print "!*!FOO\n" + s + ""
	def bar(self,s):
		print "!*!BAR\n" + s + ""



	
server = pyfflermiserver()
server.setupPyffleConnection()
server.setAction("!|!Userlist",server.userlist)
server.setAction("!|!Onlinelist",server.onlinelist)
server.setAction("!|!Boardlist",server.boardlist)
server.setAction("!|!ClientMessage",server.clientmessage)
server.setAction("!|!MessagecountRequest",server.messagecount)
server.setAction("!|!ChatUpdateRequest",server.chatupdaterequest)
server.setAction("!|!ChatMessage",server.chatmessage)
server.setAction("!|!MessagelistRequest",server.messagelist)
server.setAction("!|!MessageHeaderRequest",server.messageheader)
server.setAction("!|!MessageRequest",server.messagerequest)
server.setAction("!|!ImageRequest",server.imagerequest)
server.setAction("!|!LoginRequest",server.loginrequest)
server.setAction("!|!PrivateMessage",server.privatemessage)
server.setAction("!|!Poll",server.poll)
server.setAction("!|!Foo",server.foo)
server.setAction("!|!Bar",server.bar)
server.mainloop()

	
