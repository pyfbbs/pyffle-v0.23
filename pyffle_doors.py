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


## BEGIN TEMPLATE 
## This is template code for all plugins 
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
## END TEMPLATE

def getIdentity():
	return "pyffle_doors v0.23"

## Returns True if the version of pyffle is compatible this version of module
def confirmVersion(version): 
	return True

class PyffleModule(pyffle_module.PyffleModule):
	
	doors = []
	menu = None
	
	## We don't respond to any events
	def eventDispatched(self, event):
		pass
	
	## Gets a node number from the system plugin value pyffle_doors_maxnode
	def getNode(self):	
		self.node = self.data.pluginReadSystem("pyffle_doors_maxnode")
		if self.node == None:
			self.node = "1"
		else:
			nodeint = int(self.node)
			nodeint = nodeint + 1
			self.node = str(nodeint)
		self.data.pluginWriteSystem("pyffle_doors_maxnode",self.node)
					
	## Releases a node number from the system plugin value pyffle_doors_maxnode
	def releaseNode(self):
		maxnode = self.data.pluginReadSystem("pyffle_doors_maxnode")
		if maxnode == None:
			maxnode = "1"
		else:
			nodeint = int(maxnode)
			nodeint = nodeint - 1
			if nodeint <= 0:
				nodeint = 0
			maxnode = str(nodeint)
		self.data.pluginWriteSystem("pyffle_doors_maxnode",maxnode)

	## Displays a menu of doors, and invokes createDropFile for the chosen door
	def runMenu(self):
		try:
			self.getNode()
			if not self.doors == []:
				basemenu = [ 	
								["Doors available","DOORS (Node: " + self.node + ")> ","Borkyt. Try again"],
						   ]			
				i = 0
				for door in self.doors:
					menuEntry = [str(i),self.doors[i][0] + "\n"]
					basemenu.append(menuEntry)
					i = i + 1
				basemenu.append(["","-------\n"])
				basemenu.append(["Q","Quit"])
				userQuits = False
				while not userQuits:
					choice = self.data.util.menuChoice(basemenu)
					if choice == "q":
						userQuits = True
						break
					else:
						self.createDropFile(self.doors[int(choice)][1])
		finally:
			self.releaseNode()
		
	## Creates a DORINFO1.DEF file and sets up the door to be run, 
	## and runs dosemu to run the chosen door.
	def createDropFile(self,doorName):
		doorName = doorName.strip()
		tmpdir = tempfile.mkdtemp()
		f = open(tmpdir + "/dorinfo1.def","w")
		## FIXME hardcoded values
		f.write("hq.pyffle.com\r\n")
		f.write("System\r\n")
		f.write("0perator\r\n")
		f.write("COM1\r\n")
		f.write("57600 BAUD,N,8,1\r\n")
		f.write("0\r\n")
		f.write(self.data.currentUser.username + "\r\n")
		f.write("Fake\r\n")
		f.write("Town\r\n")
		f.write("1\r\n")
		f.write("99\r\n")
		f.write("525\r\n")
		f.write("-1\r\n")
		f.close()
		
		f = open(tmpdir + "/door.sys","w")	
		f.write("COM1:\r\n") # Comm Port - COM0: = LOCAL MODE
		f.write("38400\r\n") # Baud Rate - 300 to 38400
		f.write("8\r\n") # Parity - 7 or 8
		f.write("1\r\n") # Node Number - 1 to 99                    (Default to 1)
		f.write("38400\r\n") # DTE Rate. Actual BPS rate to use. (kg)
		f.write("Y\r\n") # Screen Display - Y=On  N=Off             (Default to Y)
		f.write("Y\r\n") # Printer Toggle - Y=On  N=Off             (Default to Y)
		f.write("Y\r\n") # Page Bell      - Y=On  N=Off             (Default to Y)
		f.write("Y\r\n") # Caller Alarm   - Y=On  N=Off             (Default to Y)
		f.write(self.data.currentUser.username + "\r\n") # User Full Name
		f.write("Lewisville, Tx.\r\n") # Calling From
		f.write("214 221-7814\r\n") # Home Phone
		f.write("214 221-7814\r\n") # Work/Data Phone
		f.write("PASSWORD\r\n") # Password
		f.write("110\r\n") # Security Level
		f.write("1456\r\n") # Total Times On
		f.write("03/14/88\r\n") # Last Date Called
		f.write("7560\r\n") # Seconds Remaining THIS call (for those that particular)
		f.write("126\r\n") # Minutes Remaining THIS call
		f.write("GR\r\n") # Graphics Mode - GR=Graph, NG=Non-Graph, 7E=7,E Caller
		f.write("23\r\n") # Page Length
		f.write("Y\r\n") # User Mode - Y = Expert, N = Novice
		f.write("1,2,3,4,5,6,7\r\n") # Conferences/Forums Registered In  (ABCDEFG)
		f.write("7\r\n") # Conference Exited To DOOR From    (G)
		f.write("01/01/99\r\n") # User Expiration Date              (mm/dd/yy)
		f.write("1\r\n") # User File's Record Number
		f.write("Y\r\n") # Default Protocol - X, C, Y, G, I, N, Etc.
		f.write("0\r\n") # Total Uploads
		f.write("0\r\n") # Total Downloads
		f.write("0\r\n") # Daily Download "K" Total
		f.write("999999\r\n") # Daily Download Max. "K" Limit
		f.write("10/22/88\r\n") # Caller's Birthdate                              (kg)
		f.write("Y:\\r\n") # Path to the MAIN directory (where User File is) (kg)
		f.write("Y:\\r\n") # Path to the GEN directory                       (kg)
		f.write("system\r\n") # Sysop's Name (name BBS refers to Sysop as)      (kg)
		f.write(self.data.currentUser.username + "\r\n") # Alias name                                      (rc)
		f.write("00:05\r\n") # Event time                        (hh:mm)       (rc)
		f.write("Y\r\n") # If its an error correcting connection (Y/N)     (rc)
		f.write("N\r\n") # ANSI supported & caller using NG mode (Y/N)     (rc)
		f.write("Y\r\n") # Use Record Locking                    (Y/N)     (rc)
		f.write("14\r\n") # BBS Default Color (Standard IBM color code, ie, 1-15) (rc)
		f.write("10\r\n") # Time Credits In Minutes (positive/negative)     (rc)
		f.write("07/07/90\r\n") # Last New Files Scan Date          (mm/dd/yy)    (rc)
		f.write("14:32\r\n") # Time of This Call                 (hh:mm)       (rc)
		f.write("07:30\r\n") # Time of Last Call                 (hh:mm)       (rc)
		f.write("6\r\n") # Maximum daily files available                   (rc)
		f.write("3\r\n") # Files d/led so far today                        (rc)
		f.write("23456\r\n") # Total "K" Bytes Uploaded                        (rc)
		f.write("76329\r\n") # Total "K" Bytes Downloaded                      (rc)
		f.write("A File Sucker\r\n") # User Comment                                    (rc)
		f.write("10\r\n") # Total Doors Opened                              (rc)
		f.write("10283\r\n") # Total Messages Left                             (rc)

			
			
			
			
			
			
				   
		cfgdir = tempfile.mkdtemp()
		os.system("cat /pyffle/doors/emusetup.bat > " + cfgdir + "/emusetup.bat")
		f = open(cfgdir + "/emusetup.bat","a")
		f.write("SET PYFNODE=" + str(self.node) + "\r\n")
		f.write("ECHO Node %PYFNODE > COM1")
		f.write("LREDIR E: LINUX\\FS\\pyffle\doors\r\n")
		f.write("LREDIR Y: LINUX\\FS\\" + tmpdir[1:] + "\r\n")
		f.write("E:\r\n")
		f.write("CD \\" + doorName + "\r\n")
		f.write("CALL " + doorName + ".BAT\r\n")
		f.write("EXITEMU\r\n")		
		
		f.close()
		## Finally run the door using dosemu
		os.system("sudo dosemu -quiet -s " + cfgdir + "/emusetup.bat -f /etc/dosemu/dosemu.conf") 

	## Reads doorlist and builds the list of doors that can be run
	def buildDoorList(self):
		self.doors = []
		f = open("/pyffle/doors/doorlist")
		lines = f.readlines()
		f.close()
		for line in lines:
			if not (line == "" or line == None):
			## Line consists of: Door name, command to execute
				elements = line.split("||||")
				name = str(elements[0])
				cmd = str(elements[1])
				self.doors.append([name,cmd])
	
		
	def go(self, command, args):
		## Sysop command to decrease node numbers caused by dropped 
		## connection etc.
		if command == "!decnode":
			self.releaseNode()
			return

		## Normal invocation, let's run the door menu
		self.data.stateChange("doorstart")
		self.buildDoorList()
		self.runMenu()
		self.data.stateChange("doorend")
		