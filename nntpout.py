#!/usr/bin/python
# nntptest

from nntplib import NNTP
import datetime
import os
import sys

	
args = sys.argv
if not len(args) == 2:
	print "usage nntpout.py <hostname>"
else:
	print "Connecting to " + args[1]
	s = NNTP(args[1],user="pyffledev",password="glfvauqus")	
	print "Posting"
	rv = s.post(sys.stdin)
	print "Posted"	
	print "Server said: " + rv
