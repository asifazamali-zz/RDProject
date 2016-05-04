#!/usr/bin/python
import sys
import re
import math
import copy

space_bw_two_tid=15
tid_event ={}
read_line ={}
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

def replace_duplicate_string(tid_event,replaced_string,line):
	start_index =0
	print 'replaced_string in func',replaced_string
	replaced_string_keys = replaced_string.keys()
	for key in tid_event.keys():
		if( key in replaced_string_keys):
			index_in_line = line.find(tid_event[key],start_index)
			start_index = index_in_line+1
			print 'index in line',index_in_line,line[0:index_in_line],replaced_string[key],line[index_in_line+len(replaced_string[key].replace(' ','-')):],len(replaced_string)
			line= line[0:index_in_line]+replaced_string[key]+line[index_in_line+len(replaced_string[key].replace(' ','-')):]
	return line
f =open("out.txt",'r')
g = open('merge.txt','w')
replaced_string={}
for i in range(0,3):
	line = f.readline()
	g.write(line)

num_of_threads = int(line.split(':')[-1].rstrip())
getTidFromSpace(line)
read_line= copy.deepcopy(tid_event)
for line in f:
	print 'readline',line
	tid_event={}
	replaced_string = {}
	getTidFromSpace(line)
	#########checking duplicate copy of event##############
	if len(tid_event)<=len(read_line):
		for tid in tid_event.keys():
			#print 'tid_event',tid_event[tid],(tid_event[tid].find('READ')>=0),(tid_event[tid].find('WRITE')>=0)
			if(tid in read_line.keys() and tid_event[tid]==read_line[tid] and ((tid_event[tid].find('READ')>=0) or (tid_event[tid].find('WRITE')>=0))):
				print 'match found',len(tid_event[tid]),tid_event[tid],tid
				replaced_string[tid]=(' '*len(tid_event[tid]))
				print 'replaced_string[tid]',replaced_string[tid]+'v'
	else:
		for tid in read_line.keys():
			#print 'tid_event',tid_event[tid],(tid_event[tid].find('READ')>=0),(tid_event[tid].find('WRITE')>=0)
				
			if(tid in tid_event.keys() and tid_event[tid]==read_line[tid] and ((read_line[tid].find('READ')>=0) or (read_line[tid].find('WRITE')>=0))):
				print 'match found',len(tid_event[tid]),tid_event[tid],tid
				replaced_string[tid]=(' '*len(tid_event[tid]))
				print 'replaced_string[tid]',replaced_string[tid]+'v'

	result_line =replace_duplicate_string(tid_event,replaced_string,line)
	print 'result_line',result_line
	if(len(result_line.strip())):
		g.write(result_line)
	#print 'result_line',result_line
	read_line= copy.deepcopy(tid_event)			
f.close()
g.close()
#print tid_event