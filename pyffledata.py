## Models for SqlAlchemy version 6
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import sessionmaker
from pyffle_tables import *
from datetime import datetime

global session 

### ACL/ACE ops
def grant(acl, subject, object):
	## FIXME: add checking of pre-existing ACE
	global session
	if isGranted(acl,subject,object):
		return;		## This ACE already exists, we don't need to do anything
	myAce = Ace()
	myAce.aclid = acl.id
	myAce.subjectid = subject
	myAce.permission = object
	myAce.grantordeny = "GRANT"
	session.add(myAce)
	session.commit()
	
def deny(acl, subject, object):
	global session
	if isDenied(acl,subject,object):
		return;		## This ACE already exists, we don't need to do anything
	myAce = Ace()
	myAce.aclid = acl.id
	myAce.subjectid = subject
	myAce.permission = object
	myAce.grantordeny = "DENY"
	session.add(myAce)
	session.commit()

def isDenied(acl, subject, object):
	global session
	denied = False
	for myAce in session.query(Ace).filter(Ace.aclid==acl.id).filter(Ace.subjectid==subject).filter(Ace.permission == object).filter(Ace.grantordeny == "DENY"):
		denied = True
	return denied
	
def isGranted(acl, subject, object):
	global session
	granted = False
	for myAce in session.query(Ace).filter(Ace.aclid==acl.id).filter(Ace.subjectid==subject).filter(Ace.permission == object).filter(Ace.grantordeny == "GRANT"):
		granted = True		
	return granted

def userExists(name):
	global session

	found = False
	for myUser in session.query(Users).filter(Users.username == name):
		found = True
	return found
	
def getMessage(msgid):
	global session
	theMessage = session.query(Message).filter(Message.id == msgid)[0]
	return theMessage
	
	
def deleteAces(aclid):
	global session
	for ace in session.query(Ace).filter(Ace.aclid == aclid):
		session.delete(ace)
		session.commit()
		
def deleteAcl(aclid):
	## delete any ACEs under this id
	deleteAces(aclid)
	
	## delete the ACL
	theAcl = session.query(Acl).filter(Acl.id == aclid)[0]
	session.delete(theAcl)
	session.commit()
	
def deleteMessagetexts(msgid):
	for msgText in session.query(Messagetext).filter(Messagetext.messageid == msgid):
		session.delete(msgText)
		session.commit()
	
def deleteMessage(msgid):
	global session
	## let's get the message first so that we can delete it's components
	msg = getMessage(msgid)
	
	## now delete any text
	deleteMessagetexts(msgid)
	
	## remember the acl id for the step after this
	aclid = msg.aclid
	
	## delete the message itself
	session.delete(msg)
	session.commit()
	
	## finally we delete the ACL
	deleteAcl(aclid)
	
def clearMessages():
	global session
	for instance in session.query(Message).order_by(Message.id): 
		print "Deleteing MsgID: " + str(instance.id) + " received at " + str(instance.sentdate)
		deleteMessage(instance.id)
		
def dumpMessages():
	global session
	for instance in session.query(Message).order_by(Message.id): 
		print "MsgID: " + str(instance.id) + " received at " + str(instance.sentdate)
		print "From: " + instance.fromname.strip()
		print "To: " + instance.toname.strip()
		print "Subj: " + instance.subject
		print "--------------------------------------------------------------"
		for msgtext in session.query(Messagetext).filter(Messagetext.messageid == instance.id).order_by(Messagetext.id):
			print msgtext.msgtext
		print " " 
	
	
## Creates a  message (in board __pyffle_email), with standard ACLs
## i.e. if recipient exists, grant him R+D
def createMessage(fromname,toname,subject,text,board='__pyffle_email'):
	## Create an ACL for the message to start with
	global session
	msgAcl = Acl()
	session.add(msgAcl)
	session.commit()

	## If the recipient is local, setup the permissions for this message 
	if userExists(toname):
		grant(msgAcl,toname,"READ")
		grant(msgAcl,toname,"DELETE")
		print "Recipient can R/D: " + str(isGranted(msgAcl,toname,"READ")) + str(isGranted(msgAcl,toname,"DELETE"))
	else:
		print "User not local, ACL not needed"
				
	## Find the board id for the requested board
	for emailBoard in session.query(Board).filter(Board.name==board).order_by(Board.id):
		pass
		
	emailId = emailBoard.id
	
	msg = Message()
	msg.fromname = fromname
	msg.toname = toname
	msg.subject = subject
 	msg.aclid = msgAcl.id
 	msg.boardid = emailId
 	msg.sentdate = datetime.now()
 	session.add(msg)
 	session.commit()
		 	
 	msgtext = Messagetext()
 	msgtext.messageid = msg.id
 	msgtext.aclid = msgAcl.id
 	msgtext.msgtext = text
 	session.add(msgtext)
 	session.commit() 
 	
 	return msg.id  

