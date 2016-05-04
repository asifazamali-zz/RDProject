#!/usr/bin/python

import sys
from sets import Set
import re
from collections import OrderedDict
f =open(str(sys.argv[1]),'r')
g = open("out.txt",'w')
l=Set([])
sublabel={}
S=Set([])                                                   # Number of threads
space_bw_two_tid=15
#local_wvariables={}
local_variables={}                                          # containing local variables---> number
local_objects = {}                                          # local_objects for sync between lock and local variable objects
local_object_keys =[]                                      # local_objects_keys for fast accessing keys
global_variables={}                                         # containing global variable---> number
lock_variables={}                                           # lock variable --> number  
global_keys=[]                                              # global_keys for fast accessing keys
local_keys=[]                                               
lock_keys=[]                                 
#global_rvariables={}
l_rwctr=0
g_rwctr=0
lock_ctr=0
file_index=0
file_descriptors=[]

                                                            #Subject Labels
CALL_POST={}
POST_CALL={}
CALL=[]
POST=[]
#WAIT_NOTIFY={}
NOTIFY_NOTIFIED={}
WAIT=[]
NOTIFY_TID=[]
NOTIFIED_ID=[]
l=Set([])
f.seek(0,0)   #setting file pointer to beginning


ptid=0
ctid=0
# for POST(ctid==ptid)
# prev_ptid=0
# prev_ctid=0
event=''
ret_string=''
prevstring = ''
adjustflag=False
child_id=-1
par_id=-1
operation=''
parent_child_operation={}
c_f=0       #counter for fork
c_n=0       #counter for notify
c_p=0 
for line in f:
  if line:
      matchobj = re.match( r'(.*?)tid:([0-9]([0-9]*)).*', line)
      if matchobj:
        #print str(matchobj.group(2)).split()[0]
        S.add(int(str(matchobj.group(2)).split()[0]))
      y=re.sub('\s+',' ',line)
      temp=re.split(" +",y)
      #print y
      if(temp[1]=='POST'):
        POST.append(temp)
      if(temp[1]=='CALL'):
        CALL.append(temp)
      if(temp[1]=='WAIT'):
        WAIT.append(int(temp[2].split(':')[1]))
      if(temp[1]=='NOTIFY'):
        NOTIFY_TID.append(int(temp[2].split(':')[1]))
        NOTIFIED_ID.append(int(temp[3].split(':')[1]))
      if(temp[1]=='READ' or temp[1]=='WRITE'):
          if(len(temp)>5):
            key = (temp[3]+"_"+temp[5])
            ############ Lock(obj) and R/W(obj,Field) as two separate objects
            ############ Problem happens when lock and R/W's are interchanged
            # if(temp[3].split(':')[1] in lock_keys):      
            #   local_keys.append(key)
            #   local_variables[key] = lock_variables[temp[3].split(':')[1]]
            if key not in local_keys:
              l_rwctr+=1;
              local_keys.append(key)
              local_variables[key]=l_rwctr
              object_key = temp[3].split(':')[1]
              if object_key not in local_object_keys:
                local_objects[object_key] = l_rwctr
                local_object_keys.append(object_key)
      if(temp[1]=='READ-STATIC' or temp[1]=='WRITE-STATIC'):
          if(len(temp)>4):
            key = (temp[3]+"_"+temp[4])
            if key not in global_keys:
              g_rwctr+=1;
              global_keys.append(key)
              global_variables[key]=g_rwctr   
      if(temp[1]=='LOCK'):
        key = temp[3].split(':')[1]
        # if key in local_object_keys:
        #   lock_keys.append(key)
        #   lock_variables[key]=local_objects[key]

        if (key not in lock_keys):
          lock_keys.append(key)
          lock_ctr+=1
          lock_variables[key]= lock_ctr         
      if(temp[1]=="HB"):
        break
      if(temp[1].isupper() and temp[1]!='ACCESS' and temp[1]!='ADD_IDLE_HANDLER' and temp[1]!='ENABLE-LIFECYCLE' and temp[1]!='ENABLE-WINDOW-FOCUS' and temp[1]!='INSTANCE-INTENT' and temp[1]!='QUEUE_IDLE' and temp[1]!='REMOVE_IDLE_HANDLER'and temp[1]!='TRIGGER-BROADCAST' and temp[1]!='TRIGGER-EVENT'and temp[1]!='TRIGGER-LIFECYCLE' and temp[1]!='TRIGGER-SERVICE'and temp[1]!='TRIGGER-WINDOW-FOCUS' and temp[1]!='ATTACH-Q' and temp[1]!='ENABLE-EVENT'and temp[1]!='LOOP' and temp[1]!='NATIVE-EXIT'and temp[1]!='RET'):
        l.add(temp[1])  
      # if(temp[1]!="POST" and temp[1]!="START"):
      #   S.add(temp[2].split(':')[1])


S=sorted(S)
#g.write(str(l))
post_list={}
for p in POST:
  #print c
  post_list[p[3]]=p[2]
print post_list
call_list={}
for p in CALL:
  #print c
  call_list[p[3]]=p[2]
print call_list
for c in CALL:
  try:
  #if p[3] in call_list:
    #print p
    #print call_list.index(p)
    CALL_POST[c[2]+c[3]]=int(post_list[c[3]].split(':')[1])
  #else:
  except(KeyError):    
    CALL_POST[c[2]+c[3]]=-1
for c in POST:
  try:
  #if p[3] in call_list:
    #print p
    #print call_list.index(p)
    POST_CALL[c[2]+c[3]]=int(call_list[c[3]].split(':')[1])
  #else:
  except(KeyError):    
    POST_CALL[c[2]+c[3]]=-1

print CALL_POST
print POST_CALL

#print NOTIFY_TID,WAIT,NOTIFIED_ID
for w in WAIT:
  try:
    if w in NOTIFY_NOTIFIED.keys():

      k=NOTIFIED_ID.index(w)
      NOTIFY_NOTIFIED[w].append(NOTIFY_TID[k])
      #print w
      #print k
      #print NOTIFIED_ID
      del NOTIFIED_ID[k]
      del NOTIFY_TID[k]
      #print NOTIFIED_ID
      #print NOTIFY_TID
      #print NOTIFY_NOTIFIED
    else:
      k=NOTIFIED_ID.index(w)
      NOTIFY_NOTIFIED[w]= [NOTIFY_TID[k]]
      #print w
      #print k
      #print NOTIFIED_ID
      del NOTIFIED_ID[k]
      del NOTIFY_TID[k]
      
      #print NOTIFIED_ID
      #print NOTIFY_TID
      #print NOTIFY_NOTIFIED
  except(ValueError):
    if w in NOTIFY_NOTIFIED.keys():
      NOTIFY_NOTIFIED[w].append(-1)
    else:
      NOTIFY_NOTIFIED[w]=[-1]

#print WAIT
#print '\n'
# for k in zip(NOTIFIED_ID,NOTIFY_TID):
#   print k

#print '\n'

# for k,v in NOTIFY_NOTIFIED.items():
#   print k,v
g.write('Global Variables: ')

for k in global_variables.keys():
  g.write(str(global_variables[k])+" ")  
g.write('\n')
g.write('Lock Varaibles: ')
for k in lock_variables.keys():
  g.write(str(lock_variables[k])+" ")
g.write('\n')  
for i in S:
  ptid=i
  ctid=ptid+1
  label=[[i],S,[i]]
  sublabel[str(i)]=label 
  string = 'tid:'+str(i)
  space = (ctid-ptid)*space_bw_two_tid
  final_string = string+ (' '*(space-len(string)))
  g.write(final_string)                           #tid:1+11 spaces
g.write('\n')





def id_to_index(tid):
  return (S.index(tid)+1)

def callFork(ptid,ctid):
  global file_index,file_descriptors,print_enable
  #print 'FORK'
  string = str(ctid)+"_"+str(ptid)+".txt"
  open_files.append(string)
  f=open(string)
  file_descriptors.append(f)
  file_descriptors_tid[f]=int(ctid)
  thread_file_descriptors[int(ctid)]=f
  file_descriptors_length[f]=0
  print_enable.append(True)
  #print file_descriptors
  files_open[f]=string
  #line = f.readline()
  #print file_index
  #file_index = (file_index+1)%len(file_descriptors)
  string = 'FORK'
  if ctid==ptid:
      final_string=string
  # Assuming fork i j where i<j always
  else:
    #print ctid
    if(ctid.find('_')>=0):
      chtid= int(ctid.split('_')[0])
      ctid=chtid
    else:
      chtid = int(ctid)
      ctid=chtid
    print chtid,ptid
    space = (id_to_index(chtid)-id_to_index(ptid))*space_bw_two_tid
    final_string = string+ ('-'*(space-len(string)-1))+'>'
  # print final_string.rjust((id_to_index(ptid)-1)*space_bw_two_tid)
    string = final_string.rjust((id_to_index(ptid)-1)*space_bw_two_tid)
  return final_string
  #print open_files
  #print file_descriptors

def callNOTIFY(ptid,ctid):
  #print 'inside notify'
  global string
  child_file_descriptor = thread_file_descriptors[int(ctid)]
  
  
  if(ctid>ptid):
    child_nxt_line = child_file_descriptor.readline()
    child_file_descriptor.seek(-len(child_nxt_line),1)
    if(child_nxt_line.find('WAIT')>=0):
    #string = str(ctid)+"_"+str(ptid)+".txt"
      print ctid,ptid
      space = (id_to_index(ctid)-id_to_index(ptid))*space_bw_two_tid
      string = 'NOTIFY' 
      final_string = string + ('-'*(space-len(string)-1))+'>'
      return final_string.rjust((id_to_index(int(ptid))-1)*space_bw_two_tid) 
    else:
      print'wait not found'
      space = ' '*(id_to_index(ptid)-id_to_index(ctid))*space_bw_two_tid
      final_string= space
      parent_file_descriptor = thread_file_descriptors[int(ptid)]
      parent_file_descriptor.seek(-len(line),1)
      return final_string
  
  else:
    child_previous_line_length = file_descriptors_length[child_file_descriptor]
    print child_previous_line_length
    child_file_descriptor.seek(-child_previous_line_length,1)
    child_prevous_line = child_file_descriptor.readline()
    print 'Inside notify child_prevous_line',child_prevous_line,child_file_descriptor
    if(child_prevous_line.find('WAIT')>=0):
    # #####swap (ctid>ptid) WAIT<--------NOTIFY    Notify tid:i notifiedtid:j----> swap these to make solve Fork---->tid1tid2
    # temp=ptid
    # ctid=ptid
    # ptid=ctid
    #string = str(ptid)+"_"+str(ctid)+".txt"
      space = (id_to_index(ptid)-id_to_index(ctid))*space_bw_two_tid
      string = 'NOTIFY'
      #print 'notify',space
      string = '<'+('-'*(space-(len(string)-2)))+string
      final_string = string
      return final_string
    else:
      print'wait not found'
      space = ' '*(id_to_index(ptid)-id_to_index(ctid))*space_bw_two_tid
      final_string= space
      parent_file_descriptor = thread_file_descriptors[int(ptid)]
      parent_file_descriptor.seek(-len(line),1)
      return final_string

  #.rjust((int(ptid))*space_bw_two_tid)
    #print open_files,file_descriptors,string  
  #c_fd = file_descriptors[open_files.index(string)]
  #line = c_fd.readline()


def callPOST(ptid,msg,ctid,string,flag):
  global file_index,file_descriptors,space_bw_two_tid,file_descriptors_length
  space = (id_to_index(ctid)-id_to_index(ptid))*space_bw_two_tid

  if(ctid>ptid):
    if(flag):
      string +='('+msg+')'
      final_string = string+ ('-'*(space-len(string)-1))+'>'

    else:
      final_string = string+ (' '*(space-len(string)-1))
    return final_string.rjust((id_to_index(int(ptid))-1)*space_bw_two_tid)  
  elif(ctid==ptid):
    final_string = string
    prev_file_index = file_index
    nxt_file_desc = file_descriptors[(file_index+1)%len(file_descriptors)]
    nxt_line = nxt_file_desc.readline()
    while(not nxt_line):
      nxt_file_desc = file_descriptors[(file_index+1)%len(file_descriptors)]
      nxt_line = nxt_file_desc.readline()
      file_index = (file_index+1)%len(file_descriptors)
    print 'nxtline',nxt_line,nxt_file_desc,file_descriptors_length[nxt_file_desc]
    nxt_file_desc.seek(-len(nxt_line),1)
    file_index = prev_file_index
    y=re.sub('\s+',' ',nxt_line)
    temp=re.split(" +",y)
    nxt_ptid = int(temp[2].split(':')[1])
    print 'nxt_ptid,ptid',nxt_ptid,ptid
    space = (id_to_index(nxt_ptid)-id_to_index(ptid))*space_bw_two_tid
    print 'space',space
    string +='('+msg+')'
    final_string = string+(' '*(space-len(string))) 
    return final_string
  else:                   #ctid<ptid
    space = (id_to_index(ptid)-id_to_index(ctid))*space_bw_two_tid
    string = 'POST('+msg+')'
    #print 'notify',space
    final_string = '<'+('-'*(space-(len(string)-1)))+string
    return final_string.rjust((id_to_index(int(ptid))-1)*space_bw_two_tid)


def callOtherEvents(temp):
  global ctid,ptid,event
  string = event
  if((string=='READ' or string=='WRITE') and len(temp)>5):
    key = (temp[3]+"_"+temp[5])
    string +='('+str(local_variables[key])+')'
  if((string=='READ-STATIC' or string=='WRITE-STATIC') and len(temp)>4):
    key = (temp[3]+"_"+temp[4])
    string +='('+str(global_variables[key])+')'
  if(string == 'LOCK' or string == 'UNLOCK'):
    key = temp[3].split(':')[1]
    string += '('+str(lock_variables[key])+')'   
    
  
      
  #print event
  # if(ctid.find('_')>0):
  #   ctid= ctid.split('_')[0]
  space = (id_to_index(int(ctid))-id_to_index(ptid))*space_bw_two_tid
  final_string = string+ (' '*(space-len(string)))
  #print "callOtherEvents",final_string
  return str(final_string) 

# def callWAIT():
#   return 'WAIT  '


def identifyCalls(line):
  y=re.sub('\s+',' ',line)
  temp=re.split(" +",y)
  global ptid,ctid,event,file_index,file_descriptors,space_bw_two_tid,file_descriptors_length,operation
  
  
  if line:
    if(temp[1]=='FORK'):
      operation='FORK'
      ptid=int(temp[2].split(':')[1])
      ctid=temp[3].split(':')[1]
      string = callFork(ptid,ctid)
      parent_child_operation[(ptid,int(ctid))]=operation
      #print string
      return string
    elif(temp[1]=='NOTIFY'):
      #ptid to print ' ' until ctid WAIT
      operation='NOTIFY'
      ptid=int(temp[2].split(':')[1])
      ctid=int(temp[3].split(':')[1])
      parent_child_operation[(int(ptid),int(ctid))]=operation
      return callNOTIFY(ptid,ctid)  
    
    elif(temp[1]=="WAIT"):
      #print WAIT_NOTIFY
      #print 'wait',int(temp[2].split(':')[1])

      ptid=int(temp[2].split(':')[1])
      notified_thread= (NOTIFY_NOTIFIED[int(temp[2].split(':')[1])][0])
      if notified_thread<0:
        return ret_string+((' ')*(abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid))
      #print notified_thread,thread_file_descriptors,int(temp[2].split(':')[1]),NOTIFY_NOTIFIED
      #print thread_file_descriptors
      #print line
      #print 'file_descriptors',file_descriptors,notified_thread,thread_file_descriptors.keys()
      if(notified_thread in thread_file_descriptors.keys()):
        notified_thread_file_descriptor= thread_file_descriptors[notified_thread]
        #print notified_thread,notified_thread_file_descriptor,file_descriptors
        if(notified_thread>ptid):
          nxtline= notified_thread_file_descriptor.readline()
          notified_thread_file_descriptor.seek(-len(nxtline),1)
        else:
          notified_thread_file_descriptor.seek(-file_descriptors_length[notified_thread_file_descriptor],1)  
          nxtline = notified_thread_file_descriptor.readline()
             
        if(nxtline.find('NOTIFY')>=0):
          print "notify found",WAIT,NOTIFY_NOTIFIED
          # del NOTIFIED_ID[NOTIFIED_ID.index(WAIT[0])]
          # del NOTIFY_TID[NOTIFY_TID.index(notified_thread)]
          del NOTIFY_NOTIFIED[int(temp[2].split(':')[1])][0]
          del WAIT[WAIT.index(int(temp[2].split(':')[1]))]
          
          print "notify found",S[(S.index(ptid)+1)%len(S)],WAIT,NOTIFY_NOTIFIED,
          string ='WAIT'
          prev_file_index = file_index
          nxt_file_desc = file_descriptors[(file_index+1)%len(file_descriptors)]
          nxt_line = nxt_file_desc.readline()
          print 'nxt_line',nxt_line
          while(not nxt_line):
            nxt_file_desc = file_descriptors[(file_index+1)%len(file_descriptors)]
            nxt_line = nxt_file_desc.readline()
            file_index = (file_index+1)%len(file_descriptors)
            print 'nxt_line',nxt_line
          print file_descriptors_length  
          print 'nxtline',nxt_line,nxt_file_desc,file_descriptors_length[nxt_file_desc]
          nxt_file_desc.seek(-len(nxt_line),1)
          file_index = prev_file_index
          y=re.sub('\s+',' ',nxt_line)
          temp=re.split(" +",y)
          nxt_ptid = int(temp[2].split(':')[1])
          print 'nxt_ptid,ptid',nxt_ptid,ptid
          space = (id_to_index(nxt_ptid)-id_to_index(ptid))*space_bw_two_tid
          print 'space',space
          final_string = string+(' '*(space-len(string)+1))
          return final_string
        else:
          print "notify not found\n"
          #file_index=(file_index+1)%len(file_descriptors)
          #print line
          file_descriptors[file_index].seek(-len(line),1)
          return ret_string+((' ')*((abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid)))
          #+(id_to_index(file_descriptors_tid[notified_thread_file_descriptor])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid+identifyCalls(line))
             
      else:
          file_descriptors[file_index].seek(-len(line),1)
          print 'notify file not found',(file_index+1)%len(file_descriptors),file_descriptors_tid
          return ret_string+((' ')*((abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid)))
             
    elif(temp[1]=='POST'):
      print temp
      operation='POST'
      ptid=int(temp[2].split(':')[1])
      msg=str(temp[3].split(':')[1])
      ctid= POST_CALL[temp[2]+temp[3]]
      parent_child_operation[(ptid,int(ctid))]=operation
      print 'POST: ptid,ctid',ptid,ctid
      if(ctid<0):
        return ret_string+((' ')*((abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid)))
          
      #ptid to print ' ' in output until ctid reached CALL
      if(ctid==ptid):
        print 'ctid==ptid'
        return callPOST(ptid,msg,ctid,'POST',True)           #posting on the same thread
      elif(ctid in thread_file_descriptors.keys()):
        c_fd = thread_file_descriptors[ctid]
        if(ctid>ptid):                                 #POST---------------->CALL
          #f = str(ctid)+"_"+str(ptid)+".txt"
          #print "open_files",open_files
          print 'POST:ctid>ptid'
          #c_fd = file_descriptors[open_files.index(f)]
          
          #c_fd.seek(-len(line),1)
          #enable = print_enable[open_files.index(f)]
          nxtline = c_fd.readline()
          #print nxtline
          c_fd.seek(-len(nxtline),1)
        else:
          print 'POST:ctid<ptid '
          c_fd.seek(-file_descriptors_length[c_fd],1)
          nxtline = c_fd.readline()
          #c_fd.seek(-len(nxtline),1)    
        if(nxtline.find("CALL")>=0 and nxtline.find("msg:"+msg)>=0):  
          print 'CALL found'
          return callPOST(ptid,msg,ctid,'POST',True)
        else:
          print 'call not found'
          p_fd = thread_file_descriptors[ptid]
          p_fd.seek(-len(line),1)
          return ret_string+((' ')*((abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid)))
              
            #return callPOST(ptid,msg,ctid,'POST',True)
      else:
        print 'call file not opened'
        return ret_string+((' ')*((abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid)))
      
               
    elif(temp[1]=="CALL"):

      #print WAIT_NOTIFY
      #print 'wait',int(temp[2].split(':')[1])
      ptid=int(temp[2].split(':')[1])
      msg=str(temp[3].split(':')[1])
      notified_thread= (CALL_POST[temp[2]+temp[3]])
      print 'notified_thread',notified_thread,ptid
      if(notified_thread<0):                     #if notified thread is not there
        return ret_string+((' ')*(abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid))
      #print notified_thread,thread_file_descriptors,int(temp[2].split(':')[1]),NOTIFY_NOTIFIED
      #print thread_file_descriptors
      #print line
      #print 'file_descriptors',file_descriptors,notified_thread,thread_file_descriptors.keys()
                          #CALL<----------------POST
      if notified_thread==ptid:
         #calling the same thread
        string = 'CALL('+msg+')'
        final_string = string
        prev_file_index = file_index
        nxt_file_desc = file_descriptors[(file_index+1)%len(file_descriptors)]
        nxt_line = nxt_file_desc.readline()
        while(not nxt_line):
          nxt_file_desc = file_descriptors[(file_index+1)%len(file_descriptors)]
          nxt_line = nxt_file_desc.readline()
          file_index = (file_index+1)%len(file_descriptors)
        print 'nxtline',nxt_line,nxt_file_desc,file_descriptors_length[nxt_file_desc]
        nxt_file_desc.seek(-len(nxt_line),1)
        file_index = prev_file_index
        y=re.sub('\s+',' ',nxt_line)
        temp=re.split(" +",y)
        nxt_ptid = int(temp[2].split(':')[1])
        print 'nxt_ptid,ptid',nxt_ptid,ptid
        space = (id_to_index(nxt_ptid)-id_to_index(ptid))*space_bw_two_tid
        print 'space',space
        final_string = string+(' '*(space-len(string))) 
        return final_string
      elif(notified_thread in thread_file_descriptors.keys()):
        notified_thread_file_descriptor= thread_file_descriptors[notified_thread]
        if(notified_thread>ptid):
          print notified_thread,notified_thread_file_descriptor,file_descriptors
          nxtline= notified_thread_file_descriptor.readline()
          notified_thread_file_descriptor.seek(-len(nxtline),1)
        else:
          notified_thread_file_descriptor.seek(-file_descriptors_length[notified_thread_file_descriptor],1)  
          nxtline = notified_thread_file_descriptor.readline()
          print nxtline
        # for k,v in WAIT_NOTIFY.items():
        #   print k,v
        #print 'nxtline',notified_thread,nxtline,file_descriptors
        #print line
        if(nxtline.find('POST')>=0 and nxtline.find("msg:"+msg)>=0):
          #notified_thread_file_descriptor.seek(-len(nxtline),1)
          print temp[2]+temp[3],CALL_POST[temp[2]+temp[3]]
          print "post found",WAIT,NOTIFY_NOTIFIED
          # del NOTIFIED_ID[NOTIFIED_ID.index(WAIT[0])]
          # del NOTIFY_TID[NOTIFY_TID.index(notified_thread)]
          #del NOTIFY_NOTIFIED[int(temp[2].split(':')[1])][0]
          #del WAIT[WAIT.index(int(temp[2].split(':')[1]))]
          
          print "notify found",WAIT,NOTIFY_NOTIFIED
          
          return 'CALL('+msg+')   '
        else:
          print "POST not found\n"
          #file_index=(file_index+1)%len(file_descriptors)
          #notified_thread_file_descriptor.seek(-len(nxtline),1)
          #print line
          file_descriptors[file_index].seek(-len(line),1)
          return ret_string+((' ')*((abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid)))
      #+(id_to_index(file_descriptors_tid[notified_thread_file_descriptor])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid+identifyCalls(line))
        # else:
        #   print'POST not found\n'
        #   file_descriptors[file_index].seek(-len(line),1)
        #   return ret_string+((' ')*((abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid)))
            
      else:
        print 'notified_id file not opened\n'
        #file_descriptors[file_index].seek(-len(line),1)
        print file_descriptors,file_index,(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]]))
        print abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))
        ret=ret_string+((' ')*(abs(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1])))*space_bw_two_tid))
    #  print 'returned value',ret+'v'
        return ret
           # len('WAIT')+(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])-id_to_index(int(temp[2].split(':')[1]))*space_bw_two_tid)
        # print 'ret value',(id_to_index(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]]),
   #call other events
    else:
      if(temp[1] in l):
      #print temp
        ptid=int(temp[2].split(':')[1]) 
        ctid =str(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])
        print 'ctid',ctid
        #ctid=files_open[(file_descriptors[(S.index(ptid)+1)%len(file_descriptors)])].split('.')[0]
        #enable=print_enable[open_files.index(f)]
        #print 'inside other event',ptid,ctid
        if(ctid.find('_')>=0):
          ctid=ctid.split('_')[0] 
        event = temp[1]                   
        #string = files_open[(file_descriptors[(S.index(ptid)+1)%len(file_descriptors)])].split('.')[0]
        string = callOtherEvents(temp)    
        #print ptid,ctid,event,string                       
        return string            
      else:
        ptid=int(temp[2].split(':')[1]) 
        ctid =str(file_descriptors_tid[file_descriptors[(file_index+1)%len(file_descriptors)]])
        string =''
        space = (id_to_index(int(ctid))-id_to_index(ptid))*space_bw_two_tid
        final_string = string+ (' '*(space-len(string)))
        #print 'inside else'
        return final_string



# def adjustString(string):
#   global prevstring,adjustflag,ptid,ctid,event,adjustflag,child_id,par_id,operation,beg_find_operation,ptid,parent_child_operation
#   d=collections.OrderDict(sorted(parent_child_operation.keys()))
#   for k,v in d:
#     temp=k.split(':')
#     par_id =temp[0]
#     child_id=temp[1]
      #counter for post
def adjustString(adjstr):
  global space_bw_two_tid,parent_child_operation,c_f,c_n,c_p,string,ptid,ctid,operation
  print 'adjustString',parent_child_operation,adjstr.count('FORK'),adjstr.count('NOTIFY'),adjstr.count('POST')
  if len(parent_child_operation)>=1 :
    if (adjstr.count('FORK')>1 or adjstr.count('NOTIFY')>1 or adjstr.count('POST')>1) :
      d=sorted(parent_child_operation.iteritems(),key=lambda(k,v):k[0])
      
      print d

      for k in d:
        ptid = k[0][0]
        ctid = k[0][1]
        if(ptid!=ctid):
        #print k
          if(parent_child_operation[k[0]]=='FORK'):                       # Fork--------------->THREADINIT  changed to FORK(1)---------->THREADINIT(1)                                                     
            c_f+=1
            comm_index = (id_to_index(ptid)-1)*space_bw_two_tid
            rep_th_index = (id_to_index(ctid)-1)*space_bw_two_tid
            # rep_st_index = (comm_index)*space_bw_two_tid
            last_index = rep_th_index+len('THREADINIT')
            print 'inside final adjustString',comm_index,last_index,adjstr[:last_index]
            adjstr = adjstr[0:comm_index]+adjstr[comm_index:comm_index+4]+"("+str(c_f)+")"+adjstr[comm_index+7:last_index]+'('+str(c_f)+')'+adjstr[last_index+3:]
            print 'inside final adjustString: changed string',adjstr
            if(adjstr.find('THREADINIT',last_index+1)>=0):
              l=adjstr.find('THREADINIT',last_index+1)
              print l,last_index
              adjstr =adjstr[:last_index+3]+((('-')*(l-last_index-4))+'>')+adjstr[last_index+3:].lstrip()
            if(adjstr.find('WAIT',last_index+1)>=0):
              l=adjstr.find('WAIT',last_index+1)
              adjstr =adjstr[:last_index+3]+(('-')*(l-last_index-4)+'>')+adjstr[last_index+3:].lstrip()
            if(adjstr.find('CALL',last_index+1)>=0):
              l=adjstr.find('CALL',last_index+1)
              adjstr =adjstr[:last_index+3]+(('-')*(l-last_index-4)+'>')+adjstr[last_index+3:].lstrip()
            print 'inside final adjustadjstr',adjstr    

          if(parent_child_operation[k[0]]=='NOTIFY'):
            c_n+=1
            comm_index = prevstring.find('NOTIFY',(id_to_index(c_n)-1)*len('NOTIFY'))
            rep_st_index = (comm_index)*space_bw_two_tid
            last_index = rep_st_index+(ctid-ptid)*space_bw_two_tid+len('WAIT')
            adjstr = adjstr[rep_st_index:rep_st_index+4]+"("+str(c_n)+")"+adjstr[rep_st_index+7:last_index]+'('+str(c_n)+')'
            print 'adjustString',comm_index,rep_st_index,last_index,adjstr
            if(adjstr.find('THREADINIT',last_index+1)>=0):
              l=adjstr.find('THREADINIT',last_index+1)
              adjstr =adjstr[:last_index+3]+(('-')*(last_index-l-1)+'>')+adjstr[last_index:].lstrip()
            if(adjstr.find('WAIT',last_index+1)>=0):
              l=adjstr.find('WAIT',last_index+1)
              adjstr =adjstr[:last_index+3]+(('-')*(last_index-l-1)+'>')+adjstr[last_index:].lstrip()
            if(adjstr.find('CALL',last_index+1)>=0):
              l=adjstr.find('CALL',last_index+1)
              adjstr =adjstr[:last_index+3]+(('-')*(last_index-l-1)+'>')+adjstr[last_index:].lstrip()
            print 'inside final adjustString',adjstr    

          if(parent_child_operation[k[0]]=='POST'):
            c_p+=1
            comm_index = prevstring.find('POST',(id_to_index(c_p)-1)*len('POST'))
            rep_st_index = (comm_index)*space_bw_two_tid
            last_index = rep_st_index+(ctid-ptid)*space_bw_two_tid+len('CALL')
            adjstr = adjstr[rep_st_index:rep_st_index+4]+"("+str(c_p)+")"+adjstr[rep_st_index+7:last_index]+'('+str(c_p)+')'
            print 'adjustadjstr',comm_index,rep_st_index,last_index,adjstr
            if(adjstr.find('THREADINIT',last_index+1)>=0):
              l=adjstr.find('THREADINIT',last_index+1)
              adjstr =adjstr[:last_index+3]+(('-')*(last_index-l-1)+'>')+adjstr[last_index:].lstrip()
            if(adjstr.find('WAIT',last_index+1)>=0):
              l=adjstr.find('WAIT',last_index+1)
              adjstr =adjstr[:last_index+3]+(('-')*(last_index-l-1)+'>')+adjstr[last_index:].lstrip()
            if(adjstr.find('CALL',last_index+1)>=0):
              l=adjstr.find('CALL',last_index+1)
              adjstr =adjstr[:last_index+3]+(('-')*(last_index-l-1)+'>')+adjstr[last_index:].lstrip()
            print 'inside final adjustString',adjstr    
      
    else:
      #print operation
      if(ctid<ptid and operation =='NOTIFY' and (adjstr.find('NOTIFY')>=0)):
        print 'Inside adjustString else part',string
        remaining_string = prevstring[:-(len(string))]
        remaining_string = remaining_string.rstrip()
        print 'remaning string after strip',remaining_string
        remaining_string += string
        print 'final reamaining string',remaining_string
        adjstr = remaining_string
    #  adjstr = remaining_string
  parent_child_operation={}
  string1 =adjstr
  return string1 
  c_n=0
  c_p=0
  c_f=0
  

#beg_find_operation =0
def printstring(string):
  #global printstring
  #print 'string'+string
  global prevstring,adjustflag,ptid,ctid,event,adjustflag,child_id,par_id,operation,beg_find_operation,ptid,parent_child_operation
  # print "prevstring",prevstring
   #print string

  #print string,string.find('FORK')
  
  if(adjustflag):
    print 'childid,ptid,par_id',child_id,ptid,par_id
    if(int(child_id)==int(ptid)):          #no adjustment require if ptid==chid(next one is chtid which is called for fork)
      prevstring= prevstring+string
      adjustflag=False
      print 'adjustflag false',string
    elif(int(child_id)>int(ptid) and file_index!=0):
      #print 'inside else child_id>ptid',ptid,par_id
      print 'abc',prevstring,operation
      comm_index = (id_to_index(int(par_id))-1)*space_bw_two_tid
      print 'comm_index',comm_index
      whitespace_strip_string = string.rstrip()  #e.g. 'WAIT    (NUMBEROFSPACE(i,i+1)--->WAIT'
      #print 'whitespace_strip_string',whitespace_strip_string,whitespace_strip_string.find('READ-STATIC'),whitespace_strip_string.find('WRITE-STATIC')
      if(not ((whitespace_strip_string.find('READ-STATIC')>=0) or (whitespace_strip_string.find('WRITE-STATIC')>=0))):
        #print whitespace_strip_string.find('READ-STATIC')
        dash_remove=whitespace_strip_string.replace('-','')
      else:
        dash_remove = whitespace_strip_string
      dash_arrow_remove = dash_remove.replace('>','')  
      print 'dash_arrow_remove',dash_arrow_remove
      #print child_id,par_id,ptid,len(prevstring)
      rep_st_index = comm_index+(id_to_index(int(ptid))-id_to_index(int(par_id)))*space_bw_two_tid
      #replacing started
      prevstring = prevstring[0:(rep_st_index)]+dash_arrow_remove+prevstring[rep_st_index+len(dash_arrow_remove):len(prevstring)]
      #adjustflag=False
      print 'adjustflag false',string
      print "comm_index",comm_index,'rep_st_index',rep_st_index
      #i = 0
      
      # while(i<len(string)):
      #   print prevstring[rep_st_index],string[i],rep_st_index
      #   prevstring[rep_st_index]=string[i]
      #   i+=1
      #   rep_st_index+=1

      #   print prevstring
      #print prevstring
    else:
      prevstring+=string    
      #print prevstring
  #get child id of com_event
  else:
    prevstring+=string
    
  if(((string.find('FORK')>=0) or (string.find('NOTIFY')>=0) or (string.find('POST')>=0)) and not adjustflag and ctid!=ptid):
    #if(file_index==(len(file_descriptors)-1)):  #if its the last operation then make immediate connection with its counterpart
      print 'ctid,ptid,par_id',ctid,ptid,par_id
      if((int(ctid)<int(ptid)) and (int(ctid)<=int(par_id))):  #whitespace_strip_string=prevstring.rstrip()
        CALL_RESPONSE ={'THREADINIT':'FORK','WAIT':'NOTIFY','CALL':'POST'} 
        print 'initial prevstring',prevstring
        prevstring = prevstring[:-len(string)]
        prevstring=prevstring.rstrip()+' '+string
        string = string.replace('-','')
        string = string.replace('<','')
        
        print 'prevstring after reducing',string,prevstring
        l=prevstring.find(string,(((id_to_index(ptid))-1)*space_bw_two_tid))
        list_calls = prevstring[(id_to_index(ctid)-1)*space_bw_two_tid:l+(len(string)+1)].split()
        child_call = list_calls[0]
        #list_calls.append(string)
        
        print 'list_calls',list_calls,child_call,prevstring
        total_bw_call_response = ((id_to_index(ptid)-id_to_index(ctid))*space_bw_two_tid)
        #-len(CALL_RESPONSE[child_call])
        temp_string = prevstring[0:(id_to_index(ctid)-1)*space_bw_two_tid+len(CALL_RESPONSE[child_call[0:4]])-1]+'<'
        print 'temp_string',temp_string
        number_of_dashes=0
        del list_calls[0]
        for l in list_calls:
            if(l.find('<')>=0):
              l=l.replace('<','')
              l=l.replace('-','')
            print 'list_items',l,prevstring
            ind = prevstring.find(l,len(temp_string)+1)
            print 'index',ind,(ind-len(temp_string)-1)
            number_of_dashes+=(ind-len(temp_string)-1)
            #number_of_dashes+= len(l)
            temp_string = temp_string[0:len(temp_string)]+('-')*((ind-len(temp_string)-1))+l
            #number_of_dashes += (ind-len(temp_string)-1)
            #rint number_of_dashes
            print temp_string
        #tmp_string = prevstring[0:(id_to_index(ctid)*space_bw_two_tid+CALL_RESPONSE[]]
        l = len(prevstring)-total_bw_call_response-len(string)-1
        #l=number_of_dashes-total_bw_call_response
        if(l>0 and len(list_calls)>1):
          print number_of_dashes,total_bw_call_response
          
          prevstring=temp_string
          prevstring = prevstring[:-len(string)]
          print 'ab',prevstring,l,id_to_index(ptid),id_to_index(ctid)
          
          prevstring = prevstring[:-l]
          print 'anc',prevstring,l
          
          prevstring = prevstring+string
          print 'acad',prevstring,l
        
      
      else: 

        adjustflag=True
        par_id =ptid
        child_id=ctid
        #parent_child_operation[str(ptid)+":"+str(ctid)]=operation
        #operation = string
        #beg_find_operation=len(string)
        #print '    '+child_id
        print 'inside adjustflag',line,child_id,ptid

    #print 'ctid',ctid,child_id,line

  #print prevstring+'\n'
  print 'prevstring',prevstring+'v'
  if(file_index==(len(file_descriptors)-1)):
      prevstring= adjustString(prevstring)
      prevstring_after_strip= prevstring.lstrip()
      print 'prevstring after lstrip',prevstring_after_strip+'v'
      if(prevstring_after_strip):
        # prevstring = prevstring.rstrip()
        # print 'prevstring after rstrip',prevstring
        # if(prevstring):
        print 'prevstring',prevstring+'v'
        prevstring=prevstring+'\n'
        g.write(prevstring)
      prevstring=''
      adjustflag=False

def checkIndex(string):
  if(string.find('READ')>=0):
    return string.find('READ')
  elif(string.find('WRITE')>=0):
    return string.find('WRITE')
  elif(string.find('READ-STATIC')>=0):
    return string.find('READ-STATIC')
  else:
    return string.find('WRITE-STATIC')
  
#print global_rvariables 
#print 	global_wvariables
#print local_rvariables
#print global_wvariables

open_files=['1.txt']
files_open={}             #filedescriptor -> filename
file_descriptors_tid={}
print_enable=[]
thread_file_descriptors={}
file_descriptors_length={}
previous_line ={}
#com_events=['FORK','NOTIFY','POST']
f = open(open_files[0])
files_open[f]='1.txt'
file_descriptors.append(f)
line = f.readline()
print_enable.append(True)
thread_file_descriptors[1]=f
file_descriptors_tid[f]=1
file_descriptors_length[f]=len(line)
print_flag = True
#length_of_filedescriptors=len(file_descriptors)
while(len(file_descriptors)):
  if line:
    print line
    #if print_flag:
    returned_value = identifyCalls(line)
    #print "prevstring",printstring
    #print line
    print returned_value,ctid,ptid
    #print 'returned value',returned_value
    #concatenate until all the fd's are read (Problem: Fork---------->ThreadInitThreadExit)
    printstring(returned_value)               
    #print printstring,file_descriptors,open_files
    #lf = line.find('READ')>=0 or line.find('WRITE')>=0 +line.find('READ-STATIC')>=0 +line.find('WRITE-STATIC')>=0 
   # index_of_read_write =checkIndex(line)
    #if(index_of_read_write>=0):
    #  previous_line[file_index] = line[index_of_read_write:]
    
    file_index= (file_index+1)%len(file_descriptors)
    # if(file_index==0):
    #   length_of_file_descriptors=len(file_descriptors)
    #file_descriptors.append(f) 
    print 'reading',file_descriptors[file_index],file_descriptors
    line = file_descriptors[file_index].readline()
    index_of_read_write = checkIndex(line)
   # if((len(previous_line)>=len(file_descriptors)) and (line[index_of_read_write:] == previous_line[file_index])):
   #  print 'line,  same',line[index_of_read_write:]
   #   print 'previous line',previous_line[file_index]
  #    print_flag = False
   #   continue
    file_descriptors_length[file_descriptors[file_index]]=len(line)
    print_flag= True
    #print 'thread_file_descriptors',thread_file_descriptors
    
    #print file_descriptors_length
   #print line 
   # print line
  else:
    if(file_descriptors):
      if(file_index==(len(file_descriptors)-1)):
        prevstring= prevstring+'\n'
        print 'closed string',prevstring
        g.write(prevstring)
        prevstring=''
      #file_index= (file_index+1)%len(file_descriptors)
      #print file_index,file_descriptors
      #print 'closing',file_descriptors[file_index]
      file_descriptors[file_index].close()
      del open_files[file_index]
      del files_open[file_descriptors[file_index]] 
      #S.remove(file_descriptors_tid[file_descriptors[file_index]])
      del file_descriptors_tid[file_descriptors[file_index]]
      del file_descriptors_length[file_descriptors[file_index]]
      del file_descriptors[file_index]
      #del thread_file_descriptors[file_index]
      #del thread_file_descriptors[open_files[file_descriptors[file_index]].split('_')[0]]
      del print_enable[file_index]

      print 'closing:',file_index,len(file_descriptors)
      
      #g.write(prevstring+'\n')
      #eprevstring=''
      if(len(file_descriptors)):
        file_index=(file_index)%len(file_descriptors)
      #file_index= (file_index+1)%length_of_filedescriptors
        print 'closing',file_descriptors,file_index
        line =file_descriptors[file_index].readline()
  
       
 





f.close()
g.close()