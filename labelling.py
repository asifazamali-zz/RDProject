#!/usr/bin/python
import sys
import re
import math
import copy


tid_event ={}
sub_label = {}
obj_set = []
obj_label = {}
global_obj_set ={}
global_obj_label ={}
lock_obj_set =[]
lock_obj_label ={}
mesg_set =[]
mesg_label ={}
write_error_count =0
write_global_count =0
space_bw_two_tid=15
var_lock_map = dict()
fork_flag = True

def tid_from_index(ind):
	float_value = ind/space_bw_two_tid
	floor_value = ind//space_bw_two_tid
	ceil_value = math.ceil(ind/space_bw_two_tid)
	if((float_value-floor_value)<(ceil_value-float_value)):
		return floor_value
	else:
		return ceil_value
def getTidFromSpace(line):
	events_list  = re.split('-|>| |<|\n',line)
	start_index =0
	for event in events_list:
		if(event):
			index_in_line = line.find(event,start_index)
			start_index = index_in_line+1
			tid = tid_from_index(index_in_line)
			tid_event[int(tid)]=event


def lub(class_a,class_b):                        #   lub(a,b)   i.e    (a) lub_opration (b) --> (a)  // where a and b are the label
	# print 'class_a',class_a,'class_b',class_b
	owner_a =class_a[0]                           
	reader_set_a=set(class_a[1])                        
	writer_set_a=set(class_a[2])  
	reader_set_b=set(class_b[1])
	writer_set_b=set(class_b[2])
	reader_set_a.intersection_update(reader_set_b)   #  taking the intersection of reader_set_a and reader_set_b and save it in reader_set_a
	writer_set_a=writer_set_a.union(writer_set_b)    #  taking the union of writer_set_a and writer_set_b and save it in writer_set_a    
	return [owner_a,reader_set_a,writer_set_a]  

def initialize_subject(key):
	if(fork_flag):
		sub_label[key] = [key,S,{key}]				 # initial label of subject S{ownner:tid,all tids,tid}	
def identify_event(key,line):
	global write_error_count,write_global_count
	if line == 'THREADINIT':
		if key not in sub_label.keys():
			initialize_subject(key)
	#elif line == 'THREADEXIT':
	elif line == 'THREADEXIT':
		return 0
	elif line.find('READ-STATIC')>=0:
		obj_id= int(line[len('READ-STATIC')+1:-1])
		if obj_id not in global_obj_set:
			global_obj_set.append(obj_id)
			global_obj_label[obj_id] = [-1,S,{-1}]	             #initial label of global object G[-1,S,-1]
		current_thread_label = sub_label[key]
		want_to_read = current_thread_label[0]
		current_variable_label = global_obj_label[obj_id]
		reader_set = current_variable_label[1]
		if(want_to_read in reader_set):
			sub_label[key] = lub(sub_label[key],global_obj_label[obj_id])
			print 'sub_label after read', sub_label[key]
		else:
			print '############ MISUSE #####################'
			print 'on line_no ',line_no
			print 'operation: READ-STATIC'
			print 'tid:'+str(key)+' having label '+str(sub_label[key])
			print 'object_id '+str(obj_id)+' having label '+str(global_obj_label[obj_id])
			

	elif line.find('WRITE-STATIC')>=0:	
		obj_id = int(line[len('WRITE-STATIC('):-1])
		if obj_id not in global_obj_set:
			global_obj_set.append(obj_id)
			global_obj_label[obj_id] = [-1,S,{-1}]					#initial label of global object G[-1,S,-1]
		current_thread_label = sub_label[key]
		want_to_read = current_thread_label[0]
		thread_reader_set = current_thread_label[1]
		thread_writer_set = current_thread_label[2]
		current_variable_label = global_obj_label[obj_id]
		reader_set = current_variable_label[1]
		writer_set = current_variable_label[2]
		if(set(reader_set)<= set(thread_reader_set)):
			global_obj_label[obj_id] = global_obj_label[obj_id]
			print 'global_obj_label after write',global_obj_label
		else:
			write_global_count = write_global_count+1
			print '##############  MISUSE #################'
			print 'on line no. ',str(line_no)
			print 'operation: WRITE-STATIC'
			print 'tid:'+str(key)+' having label '+str(sub_label[key])
			print 'object_id '+str(obj_id)+' having label '+str(global_obj_label[obj_id])

			
	elif line.find('READ')>=0:
		obj_str = line[5:-1]
				                  # Ignoring read and write from database
		if obj_str:
			obj_id = int(obj_str)
			if(obj_id not in obj_set):
				obj_set.append(obj_id)
				obj_label[obj_id] = [key,S,{key}]									#inital label of O[id,S,id]
			current_thread_label = sub_label[key]
			want_to_read = current_thread_label[0]	
			current_variable_label = obj_label[obj_id]
			reader_set = current_variable_label[1]
			print 'reader_set,want_to_read',reader_set,want_to_read
			if(want_to_read in reader_set):
				sub_label[key] = lub( sub_label[key], obj_label[obj_id])
				print 'sub_label after read',sub_label[key]
			else:
				print '####################### MISUSE #########################'
				print 'lin no. ' + str(line_no)
				print 'operation: ' + 'READ'
				print 'tid:'+str(key)+' having label '+ str(sub_label[key])
				print 'obj_id :'+str(obj_id)+' having label '+str(obj_label[obj_id])

	elif line.find('WRITE')>=0:
		print line
		obj_str = line[6:-1]
		if(obj_str):						#ignoring database write
			obj_id = int(obj_str)
			if obj_id not in obj_set:
				obj_set.append(obj_id)
				obj_label[obj_id] = sub_label[key]

			current_thread_label  = sub_label[key]
			want_to_read = current_thread_label[0]
			thread_reader_set = current_thread_label[1]
			thread_writer_set = current_thread_label[2]
			current_variable_label = obj_label[obj_id]
			reader_set = current_variable_label[1]
			writer_set = current_variable_label[2]	
			if( set(reader_set) <= set(thread_reader_set)):
				obj_label[obj_id] = lub(obj_label[obj_id], sub_label[key])
				print 'obj_label after write',obj_label[obj_id]	
			else:
				write_error_count +=1
				print '########## MISUSE ###########'
				print 'on line_no ' +str(line_no)
				print 'operation: '+'WRITE'
				print 'tid:'+str(key)+' having label '+str(sub_label[key])
				print 'object_id '+str(obj_id)+' having label '+str(obj_label[obj_id])


	



	
	elif line.find('UNLOCK')>=0:
		obj_id = int(line[len('UNLOCK('):-1])
		var_lock_map[obj_id] =0
		holding_thread_label = sub_label[key]
		sub_label[key] = lub(sub_label[key],lock_obj_label[obj_id])
		lock_obj_label[obj_id] = lub(holding_thread_label,lock_obj_label[obj_id])

	elif line.find('LOCK')>=0:
		obj_id =int(line[len('LOCK('):-1])
		if obj_id not in lock_obj_set:
			lock_obj_set.append(obj_id)
			lock_obj_label[obj_id] = [{-1},S,{-1}]										#initial label of lock_object{-1,S,-1}
		var_lock_map[obj_id]=1
		holding_thread_label = sub_label[key]
		sub_label[key] = lub(sub_label[key],lock_obj_label[obj_id])
		lock_obj_label[obj_id] = lub(holding_thread_label,lock_obj_label[obj_id])

	
	

	elif line.find('FORK')>=0:          ######did'nt cover more than one thread in a line
		#print tid_event
		target_thread_id = tid_event.keys()[tid_event.values().index('THREADINIT')]
		#print target_thread_id,tid_event_key
		tid_event_key.remove(target_thread_id)
		del tid_event[target_thread_id]
		#tid_event_key.remove(target_thread_id)
		target_thread_id = R[target_thread_id]
		if target_thread_id not in sub_label.keys():
			initialize_subject(target_thread_id)
		sub_label[target_thread_id]=sub_label[key]	
		fork_flag = False
		print 'sub_label[parent_label]',sub_label[key]
		print 'sub_label[child_label]',sub_label[target_thread_id]


	elif line.find('NOTIFY')>=0:
		#print 'line',line
		try:
			target_thread_id = tid_event.keys()[tid_event.values().index('WAIT')]
			tid_event_key.remove(target_thread_id)
			del	tid_event[target_thread_id]
		except ValueError:
			target_thread_id = tid_event.keys()[tid_event.values().index('WAI')]
			tid_event_key.remove(target_thread_id)
			del	tid_event[target_thread_id]	
		target_thread_id = R[target_thread_id]					# change from index to corresponding tid
		if target_thread_id not in sub_label.keys():
			initialize_subject(target_thread_id)
		#print key,target_thread_id
		sub_label[target_thread_id] = lub(sub_label[key],sub_label[target_thread_id])
		print 'sub_label[target_thread_id]',sub_label[target_thread_id]		

	elif line.find('CALL')>=0:
		print line
		mesg_id = line[5:-1]
		mesg_id = int(mesg_id)
		str_post = 'POST('+str(mesg_id)+')'
		if(str_post in tid_event.values()):
			target_thread_id = tid_event_key[tid_event.values().index(str_post)]
			if(key<R[target_thread_id]):
				del tid_event[target_thread_id]
				tid_event_key.remove(target_thread_id)
				if(mesg_id not in mesg_set):
					mesg_set.append(mesg_id)
					mesg_label[mesg_id] = [key,S,{key}]					#initial label for mesg[id,S,id]
				mesg_label[mesg_id][1].add(target_thread_id)
				print 'mesg_label',mesg_label
		sub_label[key]= lub(sub_label[key],mesg_label[mesg_id])	
		print 'sub_label[parent_label]',sub_label[key]
	elif line.find('POST')>=0:
		print 'inside',line
		mesg_id = line[5:-1]
		mesg_id = int(mesg_id)
		if mesg_id not in mesg_set:
			mesg_set.append(mesg_id)
			mesg_label[mesg_id]= [key,S,{key}]
		str_call = 'CALL('+str(mesg_id)+')'
		if(str_call in tid_event.values()):
			target_thread_id = tid_event_key[tid_event.values().index(str_call)]
			del tid_event[target_thread_id]
			tid_event_key.remove(target_thread_id)
			target_thread_id = R[target_thread_id]
			mesg_label[mesg_id][1].add(target_thread_id) 
		print 'mesg_label',mesg_label
	else:
		return 0




#f =open("out.txt",'r')
line_no =0
tid_event_key = []
f = open("merge.txt",'r')
for i in range(0,2):
	f.readline()
line = f.readline()
num_of_threads = int(line.split(':')[-1].rstrip())
R = range(1,num_of_threads+1)
S = set(R)
for line in f:
	line_no +=1
	print line
	tid_event ={}
	getTidFromSpace(line)
	print 'tid_event',tid_event
	tid_event_key = tid_event.keys()
	for key in tid_event_key:
		identify_event(R[key],tid_event[key])
	fork_flag = True	

print 'write error count is: '+str(write_error_count)+'\n'
print 'write global error count is: '+str(write_global_count)+'\n\n\n'
