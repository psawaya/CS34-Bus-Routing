from parser import Parser
from Tour import Tour

import json #not using python's built-in json to preserve compatibility with python 2.5

class MultiTour:
    def __init__(self):
        self.routes = []
        self.tours = []
        
    def readRoutes(self,filename):
        f = open(filename)
        
        routesTxt = f.read()
        
        f.close()
        
        self.routes_json = json.read(routesTxt)
    
    def buildTours(self,parser):
        for route in self.routes:
            newTour = Tour(parser, route)
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
        
        for routeIdx in range(len(self.routes_json)):
            self.routes.append([])
            for address in self.routes_json[routeIdx]:
                self.routes[routeIdx].append (self.addresses[self.standardizeAddress(address).strip()])
        
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
    parser = Parser("routesData/crockerMatrix.txt")
    
    multiTour.buildTours(parser)
