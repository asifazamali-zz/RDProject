#!/usr/bin/python
import sets
import os
import csv
import re
# defining the set that are going to use
write_error_count=0                             # to count the total number of write error
write_global_error_count=0						# to count the total number of writeglobal error
read_error_count=0								# to count the total number of read error	
read_global_error_count=0						# to count the total number of readglobal error
thread_set=set()                                # set to contains the threads
queue_set=set()									# set to contain all the queues
variable_set=set()								# set to contain all the variables
global_variable_set=set()						# set to contain all the global variables
queue_to_mesg_map=dict()						# a mapping from queue_id to message_list
thread_to_queue_map=dict()						# a mapping from thread to queue
lambda_map=dict()                               # lamda function which contain the mapping form (thread,message,queue,variable ,etc) --> to respective label
var_lock_map=dict()								# a mapping from variable to {0,1} i.e unlock or lock
# initial state
# here we are mapping the subject with their corresponding number
   #1) application --> 1
   #2) user --> 2
   #3) others --> 3
thread_label=[1,[1,2,3],[1]]					# initial label of a thread
global_var_label=[2,[1,2,3],[2]]				# initial label of a global variable
thread_set.add("tid:1")                         # adding thread tid:1 in the set of thread
thread_set.add("tid:2")							# adding thread tid:2 in the set of thread
lambda_map["tid:1"]=thread_label 				# assign label to tid:1 
lambda_map["tid:2"]=thread_label                # assign label to tid:2 
line_no=0
def lub(class_a,class_b):                        #   lub(a,b)   i.e    (a) lub_opration (b) --> (a)  // where a and b are the label
	owner_a =class_a[0]                           
	reader_set_a=set(class_a[1])                        
	writer_set_a=set(class_a[2])  
	reader_set_b=set(class_b[1])
	writer_set_b=set(class_b[2])
	reader_set_a.intersection_update(reader_set_b)   #  taking the intersection of reader_set_a and reader_set_b and save it in reader_set_a
	writer_set_a=writer_set_a.union(writer_set_b)    #  taking the union of writer_set_a and writer_set_b and save it in writer_set_a    
	return [owner_a,reader_set_a,writer_set_a]         # return the calculated label ()

f = open('uniq_formal_op_seq.dat', 'rb')
line=f.readlines()
temp_queue=list();
for x in line:
	line_no=line_no+1
	y=re.sub('\s+',' ',x)
	temp=re.split(" +",y)
	if temp[0] ==  "FORK":                          # if command is FORK then
		thread_set.add("tid:"+temp[2])				# add the new thread id in the thread set 
		lambda_map["tid:"+temp[2]]=lambda_map["tid:"+temp[1]]   # assign the label of child thread to the label of parent thread
	

	if temp[0] == "JOIN":							# if command is join then
		lambda_map["tid:"+temp[2]]= lub ( lambda_map["tid:"+temp[2]] ,lambda_map["tid:"+temp[1]]  )  # calculate the lub(parent,child ) --> label of parent

	if temp[0] == "ATTACHQ" :						
		queue_set.add(temp[2])						# add the queue id in the set of queue.set()
		thread_to_queue_map[temp[1]]=temp[2]		# attach the queue id to the corresponding thread id
		queue_to_mesg_map[temp[2]]=list()           
		lambda_map[temp[2]]=lambda_map["tid:2"]		# and each and every time the queue is attached by the thread 2 only

	if temp[0]== "LOOPONQ" :
		lambda_map["tid:"+temp[1]]=lub(lambda_map["tid:"+temp[1]],lambda_map[temp[2]])  # lub(thread_id, queue_id  ) -->label (thread id)

	if temp[0] == "POST" :
		is_thread_valid = "tid:"+temp[1]  
		if is_thread_valid not in thread_set:
			thread_set.add(is_thread_valid)
			lambda_map[is_thread_valid]=thread_label     # if the thread is encounter for the first time then assign it the thread_label
		lambda_map["mesg:"+temp[2]]=lambda_map["tid:"+temp[1]]  # assign the label to the posted mesg     
		temp_mesg_list=queue_to_mesg_map[thread_to_queue_map[temp[3]]] # get the list of mesg which is associated with list of queue id and which is also associated with thread id
		temp_mesg_list.append(temp[2])       # add the message to the corresponding list        
		lambda_map[thread_to_queue_map[temp[3]]]= lub( lambda_map[thread_to_queue_map[temp[3]]] , lambda_map["tid:"+temp[1] ]	)  # lub(queue id ,mesg id) --> label of queue id
		queue_to_mesg_map[thread_to_queue_map[temp[3]]]=temp_mesg_list     # update the message list associated with the queue id 



	if temp[0] == "BEGIN" :
		temp_mesg_list = queue_to_mesg_map[thread_to_queue_map[temp[1]]]     # get the message list associated with thread
		if temp[2] in temp_mesg_list:       
			index=temp_mesg_list.index(temp[2])
			temp_mesg_list.pop(index)
		else:
			print "error"
		lambda_map["tid:"+temp[1]]= lub( lambda_map["tid:"+temp[1]] , lambda_map["mesg:"+temp[2]] )  # using lub update the label of thread id
		lambda_map[thread_to_queue_map[temp[1]]]=lub( lambda_map[thread_to_queue_map[temp[1]]] , lambda_map["tid:"+temp[1]] )	# using the lub update the label of queue id 
		queue_to_mesg_map[thread_to_queue_map[temp[1]]] = temp_mesg_list # assign the updated list to the corresponding queue id



	if temp[0] == "ACQUIRE" :
		if temp[2] not in variable_set:
			variable_set.add(temp[2])

			lambda_map[temp[2]]=[temp[1],{1,2,3},{1}]     
		var_lock_map[temp[2]]=1
		holding__lamda = lambda_map["tid:"+temp[1]]
		lambda_map["tid:"+temp[1]] = lub(lambda_map["tid:"+temp[1]],lambda_map[temp[2]] )  # update label of  thread id 
		lambda_map[temp[2]]= lub (lambda_map[temp[2]] , holding__lamda  )    # update label of  acquired variable 

	if temp[0] == "RELEASE":
		var_lock_map[temp[2]] = 0
		lambda_map[temp[2]]= lub( lambda_map[temp[2]] , lambda_map["tid:"+temp[1]] )

	if temp[0] == "READ" :    
		if temp[2] not in variable_set:     # checks if the element is present or not 
			variable_set.add(temp[2])       # if not present the add to it 
			
			# lambda_map[temp[2]]=global_var_label
			lambda_map[temp[2]]=[1,[1,2],[1]]
		current_thread_label = lambda_map["tid:"+temp[1]]
		want_to_read = current_thread_label[0]
		current_variable_label= lambda_map[temp[2]]
		reader_set=current_variable_label[1]
		if(want_to_read in reader_set):     # check if they have read permission or not to read
			lambda_map["tid:"+temp[1]]= lub ( lambda_map["tid:"+temp[1]] ,lambda_map[temp[2]]  )   # if update the lambda of thread id
		else:
			print "########    MISUSE   ###########"
			print "on line no "+str(line_no)
			print "opration : "+temp[0]
			print "tid: " + temp[1] + "  having label "+ str(lambda_map["tid:"+temp[1]])
			print "object id: "+temp[2]+ "  having field :"+ temp[3]+"  having label "+str(lambda_map[temp[2]]) 


	if temp[0] == "READGLOBAL" :	   
		if temp[2] not in variable_set:     # checks if the element is present or not 
			variable_set.add(temp[2])     # if not present the add to it 
			global_variable_set.add(temp[2])
			# lambda_map[temp[2]]=global_var_label
			lambda_map[temp[2]]=[1,[1,2],[1]]
		current_thread_label = lambda_map["tid:"+temp[1]]
		want_to_read = current_thread_label[0]
		current_variable_label= lambda_map[temp[2]]
		reader_set=current_variable_label[1]
		if(want_to_read in reader_set):    # check if they have read permission or not to read
			lambda_map["tid:"+temp[1]]= lub ( lambda_map["tid:"+temp[1]] ,lambda_map[temp[2]]  ) # update the label of thread id 
		else:
			print "########    MISUSE   ###########"
			print "on line no "+str(line_no)
			print "opration : "+temp[0]
			print "tid: " + temp[1] + "  having label "+ str(lambda_map["tid:"+temp[1]])
			print "object id: "+temp[2]+ "  having field :"+ temp[3]+"  having label "+str(lambda_map[temp[2]]) 


	if temp[0] == "WRITE" :        
		if temp[2] not in variable_set:     # checks if the element is present or not 
			variable_set.add(temp[2])       # if not present the add to it 
			lambda_map[temp[2]]=lambda_map["tid:"+temp[1]]     
		if (temp[2] in variable_set - global_variable_set):
			lambda_map[temp[2]]= lub (lambda_map[temp[2]] , lambda_map["tid:"+temp[1]])   # update the label of object
		else:
			print "should be WRITEGLOBAL operation "


	if temp[0] == "WRITEGLOBAL" :
		if temp[2] not in variable_set:     # checks if the element is present or not 
			variable_set.add(temp[2])       # if not present the add to it 
			global_variable_set.add(temp[2])
			lambda_map[temp[2]]=global_var_label                         
		current_thread_label = lambda_map["tid:"+temp[1]]
		want_to_write = current_thread_label[0]
		thread_reader_set = current_thread_label[1]
		thread_writer_set = current_thread_label[2]
		current_variable_label = lambda_map[temp[2]]
		reader_set = current_variable_label[1]
		writer_set = current_variable_label[2]
		if(set(thread_writer_set) <= set(writer_set) and set(reader_set) <= set(thread_reader_set) ):    
			lambda_map[temp[2]]=lambda_map[temp[2]]
		else:
			write_global_error_count=write_global_error_count+1
			print "########    MISUSE   ###########"
			print "on line no "+str(line_no)
			print "opration : "+temp[0]
			print "tid: " + temp[1] + "  having label "+ str(lambda_map["tid:"+temp[1]])
			print "object id: "+temp[2]+ "  having field : "+temp[3] +"  having label "+str(lambda_map[temp[2]]) 

# print "write error count is :"+ str(write_error_count)
print "write global error count is :"+ str(write_global_error_count)
                        
