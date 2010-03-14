#!/usr/bin/python

from location_db import LocationDB

import time

l = LocationDB()

l.createTable()

lines = []

with open("uniq_nl_data.csv") as f:
    for line in f:
        lines.append (line)
        

x=162
while x < len(lines):
    tokens = lines[x].split('#')
    
    print ("%i: %s" % (int(tokens[0]), (tokens[1] + tokens[2]).replace("'","") ) )

    if l.addLocation( (tokens[1] + tokens[2]).replace("'","")  ,int(tokens[0])):
        x = x + 1

        # time.sleep(10)
        # print line

# l.addLocation("Hampshire College Amherst MA 01002")
# l.addLocation("ABQIAAAAxvUcjYHQiRMj8NOewtBaKBStu2RGdso2Ia6oOTd8yAAQNqw8yRSdLY27dctGySnJTIxAaiJyWK9zDQ")