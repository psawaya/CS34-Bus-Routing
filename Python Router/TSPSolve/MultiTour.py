from parser import Parser
from Tour import Tour

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

    def calculateScore(self):
        return sum([tour.score for tour in self.tours])
    
    # Writes tour data to JSON file, suitable for Google Maps integration
    def dumpToFile(self,filename):        
        coordinatesRegex = re.compile("\(([0-9\-\.]{1,})\,([0-9\-\.]{1,})\)")
        
        tourRoutes = []
        for tour in self.tours:
            tourCoordinates = []

            for node in tour.tourToIndices():
                coordinates = coordinatesRegex.match(self.coordinates[node]).groups()
                tourCoordinates.append([node, [float(coordinates[0]),float(coordinates[1])]])
            
            tourRoutes.append(tourCoordinates)
            
        f = open(filename,'w')
        
        f.write(json.write({'base' : {'name': self.tourBase[0], 'coords' : self.parseCoordinates(self.coordinates[self.tourBase[1]])},
                'routes' : tourRoutes}))
        
        f.close()

    def readRoutes(self,filename):
        f = open(filename)
        
        routesTxt = f.read()
        
        f.close()
        
        self.routes_json = json.read(routesTxt)
    
    def buildTours(self,mapinfo):
        for route in self.routes:
            print "%s %s" % (route,len(self.routes))

            newTour = Tour(mapinfo, names=route, start_route=route)
            self.tours.append(newTour)

        print self.tours

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

        for routeIdx in range(len(self.routes_json['stops'])):
            self.routes.append([])
            for address in self.routes_json['stops'][routeIdx]:
                self.routes[routeIdx].append (self.addresses[self.standardizeAddress(address).strip()])
                
        self.tourBase = [self.routes_json['home'],self.addresses[self.standardizeAddress(self.routes_json['home'])]]

        # print self.coordinates
    @staticmethod
    def parseCoordinates(coordinatesStr):
        coordinatesRegex = re.compile("\(([0-9\-\.]{1,})\,([0-9\-\.]{1,})\)")
        
        coordinates = coordinatesRegex.match(coordinatesStr).groups()
        return [float(coordinates[0]),float(coordinates[1])]

    @staticmethod
    def standardizeAddress(txt):
        newTxt = txt.lower().replace("lane","ln").strip() + " amherst, ma 01002"

        if newTxt.find(" and ") != -1: # "road" is "rd", but only in the names of intersections. ugh.
            newTxt = newTxt.replace("road","rd").replace("drive","dr")

        return newTxt

if __name__ == "__main__":
    multiTour = MultiTour()

    multiTour.readRoutes('routesData/crockerStops.json')

    multiTour.correlateWithAddresses("../../routes/by_school/crocker.txt")

    parser = Parser()
    mapinfo = parser.parse("routesData/crockerMatrix.txt")

    multiTour.buildTours(mapinfo)

    multiTour.dumpToFile("before.json")

    print "initial overall score: %i" % multiTour.calculateScore()

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
