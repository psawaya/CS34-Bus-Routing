#!/usr/bin/env python2.6

from parser import Parser
from Tour import Tour

import random

import json #not using python's built-in json to preserve compatibility with python 2.5

import re

import sys

class MultiTour:
    def __init__(self, mapinfo):
        self.routes = []
        self.tours = []

        self.mapinfo = mapinfo
        self.addresses = []
        self.coordinates = []
        for i in self.mapinfo.addresses:
            a,c = i.split("|")
            self.addresses.append(a)
            self.coordinates.append(map(float, c.strip("() ").split(",")))

        self.routes_json = None

        self.tourBase = [self.addresses[0],self.coordinates[0]]

        self.buildTours()

    def calculateScore(self):
        return sum([tour.score for tour in self.tours])

    # Writes tour data to JSON file, suitable for Google Maps integration
    def dumpToFile(self,filename):
        tourRoutes = []
        for tour in self.tours:
            tourCoordinates = []

            for node in tour.tour:#tour.tourToIndices():
                tourCoordinates.append([node, list(self.coordinates[node])])

            tourRoutes.append(tourCoordinates)

        f = open(filename,'w')

        f.write(json.write({'base' : {'name': self.tourBase[0], 'coords' : self.tourBase[1]},
                'routes' : tourRoutes, 'routeLength' : self.calculateScore()}))

        f.close()

    def dumpToDOTFile(self,filename):
        f = open(filename,'w')

        f.write("graph G {\n")

        for node in range(len(self.addresses)):
            coordinates = self.coordinates[node]
            f.write("n%s [ pos = \"%s,%s!\"];\n" %
                    (self.addresses[node],abs(coordinates[0] % 1)*200,abs(coordinates[1] % 1)*200))

        for tour in self.tours:
            for node in self.getRoutePairs(tour):
                f.write("n%s -- n%s;\n" % node)

        f.write("\n}")
        f.close()

    def dumpDiffsToDOTFile(self,filename,diffs):
        f = open(filename,'w')

        f.write("graph G {\n")

        for node in range(len(self.addresses)):
            coordinates = self.coordinates[node]
            f.write("n%s [label=\"\",size=\"1\"];\n" % (self.addresses[node]))
            #,abs(int(coordinates[1]*10) - float(coordinates[1]*10))*300,abs(int(coordinates[0]*10) - float(coordinates[0]*10))*300)
            # f.write("n%s [ pos = \"%s,%s!\"];\n" % (self.addresses[node],abs(float(coordinates[0])-int(coordinates[0]))*200,abs(float(coordinates[1])-int(coordinates[1]))*200))


        for tourIdx in range(len(self.tours)):
            routePairs = self.getRoutePairs(self.tours[tourIdx])
            edgeList = []

            for pair in routePairs:
                edgeList.append((pair[0],pair[1]))
                edgeList.append((pair[1],pair[0]))

            print edgeList

            for nodeIdx in range(len(routePairs)):
                if diffs[tourIdx][nodeIdx] not in edgeList:
                    f.write("n%s -- n%s [color=\"#ff0000\"];\n" % routePairs[nodeIdx])
                    f.write("n%s -- n%s [color=\"#00ff00\"];\n" % diffs[tourIdx][nodeIdx])
                else:
                    f.write("n%s -- n%s [label=\"%s m\"];\n" % (routePairs[nodeIdx][0],routePairs[nodeIdx][1],self.mapinfo.getCost(*routePairs[nodeIdx])))
        f.write("\n}")
        f.close()

    def swapBetweenRoutes(self,probabilityOfWorsening=0):
        pass
        # routeIdxFrom = random.sample(range(len(self.tours)),1)[0]
        # routeIdxTo = random.sample(range(len(self.tours)),1)[0]
        # 
        # #Just try again if they're the same
        # if routeIdxFrom == routeIdxTo: return self.swapBetweenRoutes(probabilityOfWorsening)
        # 
        # randomNodeIdx = random.randint(0,len(self.tours[routeIdxFrom])-1)
        # randomNode = self.tours[routeIdxFrom][randomNodeIdx]
        # 
        # closestInNewRoute = self.tours[routeIdxTo].returnClosestToNode(randomNode)
        # closest = self.mapinfo.getRowFrom(randomNode)
        # closest.sort()
        # 
        # if closestInNewRoute[1] in closest[0:3] or random.random() < probabilityOfWorsening:
        #     #Do swap
        # 
        #     print "would do swap"
        #     del self.tours[routeIdxFrom].tour[randomNodeIdx]
        #     insertIdx = closestInNewRoute[0]
            #TODO:  Generate all permutations of area around insertIdx
        #     

        # print "mapinfo: %s" % closest
        # print "compare: %s " %          self.tours[routeIdxTo].returnClosestToNode(randomNode)
        # self.tours[routeIdxTo].GENI(randomNode)



    def getRoutePairs(self,tour):
        return [(tour.tour[x],tour.tour[x+1]) for x in range(len(tour.tour)-1)]

    def readRoutes(self,filename):
        f = open(filename)

        routesTxt = f.read()

        f.close()

        self.routes_json = json.read(routesTxt)

    def buildTours(self):
        #alltour = set()
        #map(alltour.update, self.routes)
        allt = range(len(self.addresses))
        best = self.mapinfo.best_known or allt[:]
        print allt, best

        self.tours = [Tour(self.mapinfo, names=allt, default_tour=best)]
        self.allstops = self.tours[0]

        #for route in self.routes:
        #    newTour = Tour(self.mapinfo, names=route, default_tour=route)
        #    self.tours.append(newTour)

        #print self.tours

    #HACKFEST 2k10
    def correlateWithAddresses(self,addressesFilename=None):
        if self.mapinfo.addresses is None or addressesFilename is not None:
            self.addresses = dict()  #Unfortunately, we're doing this by index,
                                     # so build a dict of addresses->indices
            f = open (addressesFilename)
            fileLines = f.readlines()
            f.close()

            for lineIdx in range(len(fileLines)):
                line = fileLines[lineIdx]
                justAddressIdx = line.find("(")
                self.addresses[line[0:justAddressIdx].strip()] = lineIdx

                self.coordinates.append(line[justAddressIdx:].strip()) #save coordinates for file dump

        for routeIdx in range(len(self.routes_json['stops'])):
            self.routes.append([])
            for address in self.routes_json['stops'][routeIdx]:
                try:
                    self.routes[routeIdx].append (self.addresses[self.standardizeAddress(address).strip()])
                except KeyError:
                    #try no replacement.
                    self.routes[routeIdx].append (self.addresses[self.standardizeAddress(address,False).strip()])

        self.tourBase = [self.routes_json['home'],self.addresses[self.standardizeAddress(self.routes_json['home'])]]

        # print self.coordinates

    def partition(self):
        tagd = []
        for i in range(len(self.allstops.tour)-1):
            v1, v2 = self.allstops.tour[i:i+2]
            tagd.append((v1, self.allstops.getCost(v1, v2)))
        tagd.sort(reverse=True)
        exp = tagd[:len(self.routes)]

    @staticmethod
    def standardizeAddress(txt,replace=True):
        #print "txt = %s" % txt
        if (type(txt) == 'list'):
            txt=txt[0]
        newTxt = txt.lower().strip()

        if replace:
            newTxt = newTxt.replace("lane","ln")

        if newTxt.find(" pelham, ma 01002") == -1:
            newTxt += " amherst, ma 01002"

        if newTxt.find(" and ") != -1: # "road" is "rd", but only in the names of intersections. ugh.
            newTxt = newTxt.replace("road","rd").replace("drive","dr")

        return newTxt

def printUsage():
    print """Usage: python %s [--k=k-opt degree] [--heat=initial heat]
                             [--count=number of iterations]
                             [--routes=file] [--addresses=file] inputfile""" % sys.argv[0]

if __name__ == "__main__":
    import getopt
    if len(sys.argv) == 1:
        printUsage()
        sys.exit(1)

    optlist, args = getopt.getopt(sys.argv[1:], '', ['routes=', 'addresses=',
                                                    'k=', 'heat=', 'count='])
    print optlist, args
    if len(args) > 1:
        printUsage()
        sys.exit(1)

    parser = Parser()
    mapinfo = parser.parse(args[0])

    multiTour = MultiTour(mapinfo)

    opts = dict(optlist)
    if opts.has_key('--addresses'):
        multiTour.correlateWithAddresses(opts['addresses'])
    if opts.has_key('--routes'):
        multiTour.readRoutes(opts['routes'])
    if opts.has_key('--k'):
        k = int(opts['--k'])
    else:
        k = 3
    if opts.has_key('--heat'):
        heat0 = float(opts['--heat'])
    else:
        heat0 = 1.0
    if opts.has_key('--count'):
        count = int(opts['--count'])
    else:
       count = 200000
    multiTour.dumpToFile("before.json")
    multiTour.dumpToDOTFile("before.dot")

    beforeRoutes = [multiTour.getRoutePairs(tour) for tour in multiTour.tours]

    print "initial overall score: %i" % multiTour.calculateScore()
    # multiTour.swapBetweenRoutes()

    try:
       #for tour in multiTour.tours:
       for tour in multiTour.tours:
           heat = heat0
           dec = heat/10000
           # while (heat > 0):
           for x in range(count):
               tour.heat = heat
               tour.annealKOpt(k)
               if heat > 0:
                   heat -= dec
    except KeyboardInterrupt:
        pass

    print "final overall score: %i" % multiTour.calculateScore()
    print multiTour.tours
    multiTour.dumpToFile("after.json")
    multiTour.dumpToDOTFile("after.dot")

    multiTour.dumpDiffsToDOTFile("diffs.dot",beforeRoutes)
