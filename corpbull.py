
##
## Gets Corporate Bullshit from the Sourceforge Corporate Bullshit generator
##
## Written by Sampsa Laine (corpbull@sampsa.com), August 2012
##
## Legalese: I don't really give a monkey's what you do with this code. 
##			 That means consider it public domain.
## 			 I'm also not responsible for any damage it might cause.
##			 Should probably not be incorporated in nuclear reactors or aircraft
##

import sys
import httplib
import random

class CorpBull():
	items = []
	
	def __init__(self):
		random.seed()
		self.loadBullshit()

	def dumpShit(self):
		for item in self.items:
			item = item.strip()
			print "|" + item + "|"
			
	def getRandomBullshit(self):
		x = random.randint(0,len(self.items))
		return self.items[x].strip()
		
	def loadBullshit(self):
		conn = httplib.HTTPConnection("cbsg.sourceforge.net")
		conn.request("GET","/cgi-bin/live")
		res = conn.getresponse()
		
		html = res.read()
		
		thelist = html.split("<ul>")[1]
		thelist = thelist.split("</ul>")[0]
		self.items = thelist.split("<li>")
	
		

#bullshit = CorpBull()
#print bullshit.getRandomBullshit()
