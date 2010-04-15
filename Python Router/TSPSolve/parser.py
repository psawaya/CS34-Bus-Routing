#!/usr/bin/env python2.6

from Tour import Tour

import random
import sys
import time

class ParseError(RuntimeError):
    pass

class Parser:
    def parse(self, filename):
        mapinfo = MapInfo()
        lines = []

        with open(filename,'r') as f:
            lines = [ l.strip() for l in f.readlines()]

        i = 0
        while i < len(lines):
            cur = lines[i]
            s = cur.split()
            if len(s) > 1:
                if   s[0] == "NAME:":
                    mapinfo.setName(s[1].strip())
                elif s[0] == "DIMENSION:":
                    mapinfo.setDimension(int(s[1]))
                elif s[0] == "EDGE_WEIGHT_FORMAT:":
                    mapinfo.setEdgeWeightFormat(s[1].strip())
                elif s[0] == "BEST_KNOWN:":
                    mapinfo.setBestKnown([int(k) for k in s[1:]])
                i += 1
            elif len(s) == 1:
                j = i+1
                if s[0] == "ADDRESS_SECTION":
                    while j < len(lines) and not lines[j].startswith("EDGE_WEIGHT_SECTION"):
                        j += 1
                    mapinfo.setAddresses(lines[i+1:j])
                    i = j
                elif s[0] == "EDGE_WEIGHT_SECTION":
                    while j < len(lines) and lines[j] != "EOF":
                        j += 1
                    matrix = [[float(number) for number in lines[i+1].split()]]
                    for row in lines[i+2:j]:
                        appendArray = [float(number) for number in row.split()]
                        if mapinfo.dimension and len(matrix[-1]) < mapinfo.dimension:
                            matrix[-1].extend(appendArray)
                            if len(matrix[-1]) > mapinfo.dimension:
                                raise ParseError("Matrix size error")
                        else:
                            matrix.append(appendArray)
                    mapinfo.setEdgeWeights(matrix)
                i = j
        return mapinfo

class MapInfo:
    def __init__(self):
        self.name = None
        self.dimension = None
        self.matrix = None
        self.addresses = None
        self.best_known = None

    def setName(self, value):
        self.name = value

    def setDimension(self, value):
        self.dimension = value
        if self.matrix is not None:
            if len(self.matrix) != self.dimension:
                raise ParseError("Dimension parameter does not match actual "\
                                   "size of distance matrix")
    def setEdgeWeightFormat(self, value):
        pass

    def setBestKnown(self, value):
        self.best_known = value

    def setAddresses(self, value):
        self.addresses = value

    def setEdgeWeights(self, value):
        self.matrix = value
        if self.dimension is not None:
            if len(self.matrix) != self.dimension:
                raise ParseError("Dimension parameter does not match actual "\
                                   "size of distance matrix")
    def getCost(self, n1, n2):
        return self.matrix[n1][n2]

    def pathToAddresses(self, path):
        if self.addresses:
            for i in path:
                print addresses[i]

    def __len__(self):
        return len(self.matrix)

if __name__ == "__main__":
    random.seed(1337)

    mapinfo = Parser().parse(sys.argv[1])
    tour = Tour(mapinfo, use_best=True)

    print "Starting tour:"
    tour.printTour()

    print
    print tour.score
    lscore = tour.score

    deltaE = -0.01

    iterationsOfNoChange = 0

    reheat = False

    try:
        while True:
            prevScore = tour.score

            if tour.randTwoOptMove():
                print "score = %i, heat = %f, all time best = %i" % (tour.score,tour.heat,lscore)

                iterationsOfNoChange = 0

                if tour.score < lscore:
                    lscore = tour.score

            if tour.score == prevScore:
                iterationsOfNoChange += 1

            if reheat and iterationsOfNoChange > 1 and tour.heat <= 0:
                tour.heat = random.random()

                print "reheating to %s" % tour.heat
                time.sleep(2)

            if tour.heat > 0:
                tour.heat += deltaE
    except KeyboardInterrupt:
        pass
    print
    print "score =", tour.score
    print " tour =", tour.printTour()
