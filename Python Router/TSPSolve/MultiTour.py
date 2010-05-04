from parser import Parser
from Tour import Tour

import random

import json #not using python's built-in json to preserve compatibility with python 2.5

import re

class MultiTour:
    def __init__(self):
        self.routes = []
        self.tours = []
        
        self.addresses = []
        self.coordinates = []
        
        self.routes_json = None
        
        self.tourBase = ["",None]
        
        self.mapinfo = None

    def calculateScore(self):
        return sum([tour.score for tour in self.tours])
    
    # Writes tour data to JSON file, suitable for Google Maps integration
    def dumpToFile(self,filename):        
        coordinatesRegex = re.compile("\(([0-9\-\.]{1,})\,([0-9\-\.]{1,})\)")
        
        tourRoutes = []
        for tour in self.tours:
            tourCoordinates = []

            for node in tour.tour:#tour.tourToIndices():
                coordinates = coordinatesRegex.match(self.coordinates[node]).groups()
                tourCoordinates.append([node, [float(coordinates[0]),float(coordinates[1])]])
            
            tourRoutes.append(tourCoordinates)
            
        f = open(filename,'w')
        
        f.write(json.write({'base' : {'name': self.tourBase[0], 'coords' : self.parseCoordinates(self.coordinates[self.tourBase[1]])},
                'routes' : tourRoutes, 'routeLength' : self.calculateScore()}))
        
        f.close()
    
    def dumpToDOTFile(self,filename):
        f = open(filename,'w')
        
        f.write("graph G {\n")
        
        for node in self.addresses.iterkeys():
            coordinates = self.parseCoordinates(self.coordinates[self.addresses[node]])
            f.write("n%s [ pos = \"%s,%s!\"];\n" % (self.addresses[node],abs(float(coordinates[0])-int(coordinates[0]))*200,abs(float(coordinates[1])-int(coordinates[1]))*200))
        
        for tour in self.tours:
            for node in self.getRoutePairs(tour):                
                f.write("n%s -- n%s;\n" % node)
        
        f.write("\n}")
        f.close()
        
    def dumpDiffsToDOTFile(self,filename,diffs):
        f = open(filename,'w')
        
        f.write("graph G {\n")
        
        for node in self.addresses.iterkeys():
            coordinates = self.parseCoordinates(self.coordinates[self.addresses[node]])
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
    
    def buildTours(self,mapinfo):        
        for route in self.routes:
            newTour = Tour(mapinfo, names=route, default_tour=route)
            self.tours.append(newTour)

        print self.tours
        self.mapinfo = mapinfo

    #HACKFEST 2k10
    def correlateWithAddresses(self,addressesFilename):
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
        print self.addresses

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

    #Thanks, http://snippets.dzone.com/posts/show/753
    @staticmethod
    def all_perms(str):
        if len(str) <=1:
            yield str
        else:
            for perm in all_perms(str[1:]):
                for i in range(len(perm)+1):
                    yield perm[:i] + str[0:1] + perm[i:]    

    @staticmethod
    def parseCoordinates(coordinatesStr):
        coordinatesRegex = re.compile("\(([0-9\-\.]{1,})\,([0-9\-\.]{1,})\)")
        
        coordinates = coordinatesRegex.match(coordinatesStr).groups()
        return [float(coordinates[0]),float(coordinates[1])]

    @staticmethod
    def standardizeAddress(txt,replace=True):
        print "txt = %s" % txt
        if (type(txt) == 'list'): txt=txt[0]
        newTxt = txt.lower().strip()
        
        if replace:
            newTxt = newTxt.replace("lane","ln")
        
        if newTxt.find(" pelham, ma 01002") == -1:
            newTxt += " amherst, ma 01002"

        if newTxt.find(" and ") != -1: # "road" is "rd", but only in the names of intersections. ugh.
            newTxt = newTxt.replace("road","rd").replace("drive","dr")

        return newTxt

if __name__ == "__main__":
    multiTour = MultiTour()

    multiTour.readRoutes('routesData/hsStops.json')#('routesData/crockerStops.json')

    multiTour.correlateWithAddresses("../../routes/by_school/high-juniorhigh.txt")

    parser = Parser()
    mapinfo = parser.parse("routesData/hsMatrix.txt")

    multiTour.buildTours(mapinfo)

    multiTour.dumpToFile("before.json")
    multiTour.dumpToDOTFile("before.dot")
    
    beforeRoutes = [multiTour.getRoutePairs(tour) for tour in multiTour.tours]

    print "initial overall score: %i" % multiTour.calculateScore()
    # multiTour.swapBetweenRoutes()
    
    
    for tour in multiTour.tours:
        heat = 0
        # while (heat > 0):
        for x in range(10000):
            tour.heat = 0
            tour.annealTwoOpt()
    
            # heat -= 0.01
            # print heat
    
    print "final overall score: %i" % multiTour.calculateScore()
    
    multiTour.dumpToFile("after.json")
    multiTour.dumpToDOTFile("after.dot")
    
    multiTour.dumpDiffsToDOTFile("diffs.dot",beforeRoutes)
