#!/usr/bin/env python

import sys

f = open(sys.argv[1]).read()

f = f.splitlines()

spend = {}

startdate = ""
enddate = ""

for i in f:
	i = i.split(',')
	date = i[0]
	if startdate == "":
		startdate = date
	enddate = date
	tmp = i[1].split(';')
	tmp[0] = tmp[0].rsplit('-',1)
	who =  tmp[0][0].upper()
	try:
		time = tmp[0][1]
	except IndexError, e:
		time = ""
	description = tmp[1]
	amount = float(i[3])
	balance = i[4]

	if who not in spend:
		spend[who] = {}
		spend[who]['total'] = 0
		spend[who]['count'] = 0
		spend[who]['transactions'] = []
	spend[who]['total'] += amount
	spend[who]['count'] += 1
	spend[who]['transactions'].append({'amount':amount, 'date':date, 'description':description})

import operator

spend = sorted(spend.items(), key=lambda x: x[1]['total'])

for i in spend:
	who = i[0]
	total = i[1]['total']
	count = i[1]['count']
	transactions = i[1]['transactions']
	if count > 1:
		print "%s\t%s (%s transactions)" % (total, who, count)
		for j in transactions:
			print "\t%s\t%s\t%s" % (j['amount'],j['date'],j['description'])
	else:
		print "%s\t%s\t%s" % (transactions[0]['amount'], transactions[0]['date'], who)

print "from %s to %s" % (startdate, enddate)
