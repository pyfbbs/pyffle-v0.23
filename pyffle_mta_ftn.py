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
# Import the email modules we'll need
from email.mime.text import MIMEText

import warnings


		
def getIdentity():
	return "pyffle_mta_ftn v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleMta:
	currentUser = None
	data = None	 

	def matchIncomingAddress(self,s):
		## Returns true if we can process this kind of address
		if s.find("|") > 0:
			return True
		else:
			return False

	def getName(self):
		return "Pyffle FTN MTA"
		
	def parseIncomingAddress(self,s):
		## Returns tuple with the local user and system specified by this incoming address
		elements = s.split("!")
		username = elements[len(elements)-1]
		username = username.strip()
		system = elements[len(elements)-2]
		system = system.strip()
		return username,system
	
	def processAddress(self,s):
		## Often you get an address like foo@bar.com (Foo Bar) - we want to 
		## Break the address down by spaces
		realaddress = s
				
		realaddress = realaddress.replace("<","")
		realaddress = realaddress.replace(">","")
		realaddress = realaddress.replace("&","")
		realaddress = realaddress.replace("!","")
		realaddress = realaddress.replace(";","")

		toname = ""
		tohost = ""
		elements = realaddress.split("|")
		toname = elements[0]
		print "process, Got name " + toname
		tohost = elements[1]
		print "process, Got host " + tohost
		return toname,tohost

		
	def matchAddress(self,s):
		## Returns true if we can process this kind of address
		if (s.find("|")) > 0:
			return True
		else:
			return False

	def sendMessage(self,instance):
		## Sends the supplied message
		self.data.util.debugln("FTN SEND")
		
		sender = self.data.getUser(instance.fromname.strip())
		
		fromname = instance.fromname.strip()
		fromhost = self.data.static.options['pyffle.ftnnode']
		toname,tohost 	= self.processAddress(instance.toname.strip())
		subject = instance.subject
		print "AAARGH"
		payload = ""
		for msgtext in self.data.getMessagetexts(instance.id):
			payload = payload + msgtext
				 

		with warnings.catch_warnings(record=True) as warn:
			## FIXME CRITICAL: need to sanitize the To header here...Shell injection
			sendmail = self.data.static.options["pyffle.ftnsendmail"]
			msgpath = "/tmp/" + str(instance.id) + ".msg"
			print "Running FTN sendmail"

			sendmail = "%s --from '%s' --orig '%s' --to '%s' --dest '%s' --subject '%s' --output '%s'" %						(sendmail,fromname,fromhost,toname,tohost,subject,msgpath)

			print "sendmail= " + sendmail
			mailin, mailout = os.popen2(sendmail)
			mailin.write(payload)
			mailout.close()
			mailin.close()
			pktout = self.data.static.options["pyffle.ftnoutbound"] + "/00fa0007.out." + str(instance.id) + ".pkt"
			pakcmd = "ftn-pack %s -o '2:250/99.100' -d '2:250/7.0' --out %s ; chmod og+rxw %s" % (msgpath,pktout,pktout)
			print pakcmd
			os.system(pakcmd)
		self.data.util.println("Accepted for delivery (%s)\n" % (self.getName()))
		self.data.logEntry(self.data.LOGCRIT,"DELIVER/MESSAGE/FTN",str(fromname),"Sent mail to %s for %s" % (str(tohost),str(fromname)))		
		return		

	