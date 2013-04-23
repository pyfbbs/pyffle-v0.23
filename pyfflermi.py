### pyffle RMI

import json

def deliverBody(s):
	print str(s) 
def deliverHeader(s):
	print "!*!" + str(s) 

def getBody(s):
	return str(s) 
def getHeader(s):
	return "!*!" + str(s) 

def getClientBody(s):
	return str(s) 
def getClientHeader(s):
	return "!|!" + str(s) 

def getMessage(msg):
	s = msg.jsonify()
	rv = getHeader(msg.msgname) + "\n"
	rv = rv + getBody(s) + "\n"
	return rv

def getClientMessage(msg):
	s = msg.jsonify()
	rv = getClientHeader(msg.msgname) + "\n"
	rv = rv + getClientBody(s) + "\n"
	return rv

class PyffleRmi:
	msgname = ""

class MessagelistRequest(PyffleRmi):
	boardname = ""
	
	def __init__(self,boardname="__pyffle_mail"):
		self.msgname = "MessagelistRequest"
		self.boardname = boardname	
	
	def jsonify(self):
		thedict = { "boardname" :		self.boardname}
		return json.dumps(thedict)
	
	def _dump(self):
		pass
		
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.boardname = d["boardname"]


class MessagecountRequest(MessagelistRequest):
	def __init__(self,boardname="__pyffle_mail"):
		self.msgname = "MessagecountRequest"
		self.boardname = boardname	
	



class ChatMessage(PyffleRmi):
	def __init__(self,msg):
		self.msgname = "ChatMessage"
		self.msg = msg

	def jsonify(self):
		thedict = { "msg" :		self.msg}
		return json.dumps(thedict)
	
	def _dump(self):
		pass
		
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.msg = d["msg"]


class Messagelist(PyffleRmi):
	messages = []
	
	def __init__(self,messages=[]):
		self.msgname = "Messagelist"
		self.boards = messages	
	
	def jsonify(self):
		thedict = { "messages" :		self.boards}
		return json.dumps(thedict)
	
	def _dump(self):
		pass
		
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.boards = d["messages"]

class Boardlist(PyffleRmi):
	boards = []
	
	def __init__(self,boards=[]):
		self.msgname = "Boardlist"
		self.boards = boards
	
	def jsonify(self):
		thedict = { "boards" :		self.boards}
		return json.dumps(thedict)
	
	def _dump(self):
		pass
		
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.boards = d["boards"]



class Userlist(PyffleRmi):
	users = []
	
	def __init__(self,users = []):
		self.msgname = "Userlist"
		self.users = users	
	def jsonify(self):
		thedict = { "users" :		self.users}
		return json.dumps(thedict)
	
	def _dump(self):
		pass
		
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.users = d["users"]


class ChatUpdateRequest(PyffleRmi):
	room = ""
	def __init__(self):
		self.msgname = "ChatUpdateRequest"
		
	def jsonify(self):
		thedict = { "room" :		self.room}
		return json.dumps(thedict)
	
	def _dump(self):
		pass
		
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.room = d["room"]

class ChatUpdateResult(PyffleRmi):
	room = ""
	users = []
	newmessages = []
	def __init__(self):
		self.msgname = "ChatUpdateResult"
		
	def setusers(self,users):
		self.users = users
	
	def addmessage(user,msg):
		self.newmessages.append((user,msg))
		
	def jsonify(self):
		thedict = { "room" :		self.room,
					"users" : 		self.users,
					"newmessages":	self.newmessages}
		return json.dumps(thedict)
	
	def _dump(self):
		pass
		
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.room = d["room"]
		self.users = d["users"]
		self.newmessages = d["newmessages"]
		


class Onlinelist(PyffleRmi):
	users = []
	
	def __init__(self,users = []):
		self.msgname = "Onlinelist"
		self.users = users	
	def jsonify(self):
		thedict = { "users" :		self.users}
		return json.dumps(thedict)
	
	def _dump(self):
		pass
		
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.users = d["users"]



class PrivateMessage(PyffleRmi):
	fromName = ""
	toName = ""
	text = ""
	
	def __init__(self,msgid=0,fromName="",toName="",text=""):
		self.msgname = "PrivateMessage"
		self.text = 	text
		self.fromName =	fromName
		self.toName =	toName
	
	def jsonify(self):
		thedict = { "toName" : self.toName,
					"fromName" : self.fromName,
					"text" : self.text}
		return json.dumps(thedict)
	
	def _dump(self):
		print "text " + str(self.text)
		print "atta " + str(self.attachments)

	def dejsonify(self,rv):
		d = json.loads(rv)
		self.fromName = d["fromName"]
		self.toName = d["toName"]
		self.text = d["text"]



class Message(PyffleRmi):
	boardname = ""
	msgid = 0
	text = []
	attachments = []
	
	def __init__(self,msgid=0,text=None,attachments=None):
		self.msgname = "Message"
		self.msgid = msgid
		self.text = 	text
		self.attachments =	attachments
	
	def jsonify(self):
		thedict = { "boardname" : self.boardname,
					"msgid"	 : self.msgid,
					"text" : self.text,
					"attachments" :		self.attachments}
		return json.dumps(thedict)
	
	def _dump(self):
		print "ID   " + str(self.msgid)
		print "text " + str(self.text)
		print "atta " + str(self.attachments)

	def dejsonify(self,rv):
		d = json.loads(rv)
		self.boardname = d["boardname"]
		self.msgid = d["msgid"]
		self.text = d["text"]
		self.attachments = d["attachments"]



class ImageRequest(PyffleRmi):
	imagename = ""
	msgname = "ImageRequest"
	
	def __init__(self,imagename=""):
		self.imagename = imagename
	
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.imagename = d["imagename"]
	
	def jsonify(self):
		thedict = { "imagename"	 : self.imagename }				
		return json.dumps(thedict)		


class Image(PyffleRmi):
	payload = ""
	msgname = "Image"
	
	def __init__(self,payload=""):
		self.payload = payload
	
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.payload = d["payload"]
	
	def jsonify(self):
		thedict = { "payload"	 : self.payload }				
		return json.dumps(thedict)		


class MessageRequest(PyffleRmi):
	msgid = -1
	msgname = "MessageRequest"
	
	def __init__(self,msgid=-1):
		self.msgid = msgid
	
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.msgid = d["msgid"]
	
	def jsonify(self):
		thedict = { "msgid"	 : self.msgid }				
		return json.dumps(thedict)		

class MessageHeaderRequest(PyffleRmi):
	msgid = 0
	msgname = "MessageHeaderRequest"
	
	def __init__(self,msgid=-1):
		self.msgid = msgid
	
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.msgid = d["msgid"]
	
	def jsonify(self):
		thedict = { "msgid"	 : self.msgid }				
		return json.dumps(thedict)		
		
class ClientMessage(PyffleRmi):
	boardname = ""
	fromHdr = ""
	toHdr = ""
	subject = ""
	text = ""
	def __init__(self,boardname=None,fromHdr=None,toHdr=None,subject=None,text=""):
		self.boardname = boardname
		self.fromHdr = 	fromHdr
		self.toHdr =	toHdr
		self.subject =	subject
		self.text = text
		self.msgname = "ClientMessage"

	def jsonify(self):
		thedict = { "boardname" : self.boardname,
					"fromHdr" : self.fromHdr,
					"toHdr" :		self.toHdr,
					"subject" : 		self.subject,
					"text" :		self.text}				
		return json.dumps(thedict)
	
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.fromHdr = d["fromHdr"]
		self.toHdr = d["toHdr"]
		self.subject  = d["subject"]
		self.text  = d["text"]
		self.boardname = d["boardname"]
		
		
class MessageHeader(PyffleRmi):
	boardname = ""
	msgid = ""
	fromHdr = ""
	toHdr = ""
	subject = ""
	read = False
	date = ""
	
	def __init__(self,msgid=None,fromHdr=None,toHdr=None,subject=None,read=None,date=None):
		self.msgid = msgid
		self.fromHdr = 	fromHdr
		self.toHdr =	toHdr
		self.subject =	subject
		self.read = read
		self.date =		date	
		self.msgname = "MessageHeader"
	
	def jsonify(self):
		thedict = { "boardname" : self.boardname,
					"msgid"	 : self.msgid,
					"fromHdr" : self.fromHdr,
					"toHdr" :		self.toHdr,
					"subject" : 		self.subject,
					"read" :		self.read,				
					"date" :		self.date}				
		return json.dumps(thedict)
	
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.msgid = d["msgid"]
		self.fromHdr = d["fromHdr"]
		self.toHdr = d["toHdr"]
		self.subject  = d["subject"]
		self.date = d["date"]
		self.read = d["read"]
		self.boardname = d["boardname"]


	def foo(self):
		print "msgid   " + str(self.msgid)
		print "fromHdr " + str(self.fromHdr)
		print "toHdr   " + str(self.toHdr)
		print "subject " + str(self.subject)
		print "read    " + str(self.read)
		print "date    " + str(self.date)	

			
class ServerResult(PyffleRmi):
	
	status = 0
	description = ""
	
	def _dump(self):
		print self.status
		print self.description

	def __init__(self,status,description):
		self.status = status
		self.description = description
		self.msgname = "ServerResult"
		
	def jsonify(self):
		rv = {"status" : self.status, "description" : self.description}
		return json.dumps(rv)
		
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.status = d["status"]
		self.description = d["description"]
		
class LoginRequest(PyffleRmi):
	msgname = "LoginRequest"
	username = ""
	token = ""
	
	def __init__(self,username,token):
		self.username = username
		self.token = token
	
	def dejsonify(self,rv):
		d = json.loads(rv)
		self.username = d["username"]
		self.token = d["token"]
	
	def jsonify(self):
		thedict = { "username"	 : self.username,
					"token" : self.token }				
		return json.dumps(thedict)		


class MessagecountResult(ServerResult):
	def __init__(self,status,description):
		self.status = status
		self.description = description
		self.msgname = "MessagecountResult"

class LoginResult(ServerResult):
	def __init__(self,status,description):
		self.status = status
		self.description = description
		self.msgname = "LoginResult"


class ChatMessageResult(ServerResult):
	def __init__(self,status,description):
		self.status = status
		self.description = description
		self.msgname = "ChatMessageResult"


class RegistrationResult(ServerResult):
	def __init__(self,status,description):
		self.status = status
		self.description = description
		self.msgname = "RegistrationResult"



