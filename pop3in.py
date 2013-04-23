#!/usr/bin/python
# pop3in

import poplib
import os
import email
SSL = True
server = "pop.gmail.com"
user = "admin@pyffle.com"
password = "0300view!"

def grabAddress(s):
	rv = ""
	elements = s.split(" ")
	for element in elements:
		print "Looking at: " + str(element)
		if element.count("@") > 0:
			print "------Found the address"
			rv = element
			rv = rv.strip()
			break
	return rv 
	
def sendMsg(msg):
	rfcMsg = email.message_from_string(msg)	
	print "START ------\n" + msg + "END ------\n"
	rv = ""
	tohdr = rfcMsg['To']
	if not tohdr == None:
		tohdr = tohdr.replace("<","")
		tohdr = tohdr.replace(">","")
		print "fromhdr=" + str(rfcMsg['From']) + " subjhdr=" + str(rfcMsg['Subject'])
		print "************tohdr" + tohdr

	rv = grabAddress(tohdr)

	print "Parsed TO address: " + str(rv)
	address = str(rv)
	if not rv == "":
		print "to=" + address
		cmdline = "rmail " + address
		msg = "From " + grabAddress(rfcMsg['From']) + "\n" + msg + "\n"
		print msg
		mailin = os.popen(cmdline,"w")
		mailin.write(msg)
		mailin.close()

	
if SSL:
	M = poplib.POP3_SSL(server)
else:
	M = poplib.POP3(server)
M.user(user)
M.pass_(password)

numMessages = len(M.list()[1])
print "Found new msgs" +  str(numMessages)
for i in range(numMessages):
	response,j,octets = M.retr(i+1)
	themsg = ""
	for line in j:
		themsg = themsg + line + "\n"
	sendMsg(themsg)
	print "Deleting message "
	M.dele(i+1)

print "Quitting gracefully"
M.quit()

       
