import png
import random
import sys
import StringIO
import base64
MAXVALUE = sys.maxint
def getRandomNums(n):
	rv = []
	for i in range(0,n):
		## RGB
		rv.append(random.randint(0,255))
		rv.append(random.randint(0,255))
		rv.append(random.randint(0,255))	
	return rv

def getRandomPixels(h,w):
	rv = []
	
	for i in range(0,h): # loop through rows
		rv.append(getRandomNums(w))
	
	return rv


random.seed()
#f = StringIO.StringIO()
f = open("rndbaboon.png","w")
pixels = getRandomPixels(40,40)
encoder = png.Writer(width=40,height=40)
encoder.write(f,pixels)
## print f.getvalue()
f.close()

print "<html><body>"
print "<img src='rndbaboon.png'>"
print "<p><pre>"
b=StringIO.StringIO()
for j in range(0,40):
	for i in range(0,120):  ## 3 bytes/row
		b.write(pixels[j][i])
b64 = base64.b64encode(b.getvalue())
b.close()
col = 0
for c in b64:
	sys.stdout.write( c )
	if col == 72:
		print " "
		col = 0
	else:
		col = col + 1
		
print "</pre></body></html>"


		 
