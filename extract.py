#!/usr/bin/python
import sys
import re
import os
f= open(str(sys.argv[1]),'r')
f.next() #Android
f.next() # new line
f.next() # 1 START
for line in f:
   #print line
   # matchobj = re.match( r'(.*?)tid:([0-9]([0-9]*)).*', line)
   # if matchobj:
   if line:	
	y=re.sub('\s+',' ',line)
	temp=re.split(" +",y)
   #print y
	if(temp[1]=="HB"):
		break

	#print matchobj.group(2)
	#print matchobj.group()
	#print "group2 #"+str(matchobj.group(2))
	#print temp
	try:
		tid=temp[2].split(':')
		if(tid[0]=='tid' or tid[0]=='src' or tid[0]=='par-tid'):
			newfile =open(str(tid[1])+".txt",'a+')
			newfile.write(line)
	except(IndexError):
		print temp
		
	#print temp[2].split(':')[1]
		#print line
#print 'No Match!'
print "renaming"
f= open(str(sys.argv[1]),'r')
   
for line in f:
#   print line
   matchobj = re.match( r'(.*) *tid:(.*?)$', line, re.M|re.I)
   if matchobj:	
   	ind = matchobj.group(1).find("FORK")	
#	print ind
	if ind!=-1:
		file_name = line.split()[3].split(":")[1]+"_"+line.split()[2].split(":")[1]+".txt"
		#print "_"+line.split[3].split(":")[1]+".txt"
#		print line.split()[3].split(":")[1]+".txt" 
		os.rename(line.split()[3].split(":")[1]+".txt",file_name)


	 
