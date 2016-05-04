#!/bin/bash


find ../../ -name 'abc_log.txt1'|while read line; do
	./different_calls.py $line >> a.txt 
	sort a.txt>a_sort.txt
	uniq a_sort.txt > a_uniq.txt
done
