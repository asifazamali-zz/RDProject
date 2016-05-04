#! /usr/bin/python

import sys
from sets import Set
import re
f =open(str(sys.argv[1]),'r')
l=Set([])
for line in f:
   y=re.sub('\s+',' ',line)
   temp=re.split(" +",y)
   #print y
   if(temp[1]=="HB"):
	break
   if(temp[1].isupper() and temp[1]!='ACCESS' and temp[1]!='ADD_IDLE_HANDLER' and temp[1]!='ENABLE-LIFECYCLE' and temp[1]!='ENABLE-WINDOW-FOCUS' and temp[1]!='INSTANCE-INTENT' and temp[1]!='QUEUE_IDLE' and temp[1]!='REMOVE_IDLE_HANDLER'and temp[1]!='TRIGGER-BROADCAST' and temp[1]!='TRIGGER-EVENT'and temp[1]!='TRIGGER-LIFECYCLE' and temp[1]!='TRIGGER-SERVICE'and temp[1]!='TRIGGER-WINDOW-FOCUS' and temp[1]!='ATTACH-Q' and temp[1]!='ENABLE-EVENT'and temp[1]!='LOOP' and temp[1]!='NATIVE-EXIT'and temp[1]!='RET' and temp[1]!='THREADEXIT'):
      l.add(temp[1])

print l   
   #if(temp[1]=="READ"):
   #print temp[1]  
   #l.add(temp[1])
 #   if(len(line.split())>=2):
	# print line.split()[1]
 #   	l.add(line.split()[1])


#for s in l:
#	if str(s).isupper():
#		print s
