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
        
    def getRowFrom(self,n):
        return self.matrix[n]

    def pathToAddresses(self, path):
        if self.addresses:
            for i in path:
                print addresses[i]

    def graphvizify(self, tour, output):
        import pygraphviz as pgv
        G = pgv.AGraph()
        G.graph_attr.update(minlen=".1")
        coords = open("crocker.txt").readlines()
        coords = [i.strip().strip("()") for i in coords]
        coords = [i.split(",") for i in coords]
        coords = [(float(i[0]), float(i[1])) for i in coords]
        coords = [(i[0]-42.3, abs(i[1]+72.4)) for i in coords]
        coords = [(i[0]*100, i[1]*100) for i in coords]
        G.graph_attr.update(ratio="fill")

        G.node_attr.update(shape="circle")
        G.node_attr.update(fixedsize="True")
        G.node_attr.update(label="hax")
        G.node_attr.update(width="0.2")
        G.node_attr.update(height="0.2")
        G.node_attr.update(color="blue")

        #G.add_nodes_from(range(len(self.matrix)), label="")
        for x in range(len(self.matrix)):
            G.add_node(str(x), label="", pos=str(coords[x][0])+","+str(coords[x][1])+"!")

        #edgeWeights = []
        #for i in range(len(tour)-1):
        #    edgeWeights.append(self.getCost(tour[i],tour[i+1]))
        #edgeMax = max(edgeWeights)

        for i in range(len(tour)-1):
            G.add_edge(str(tour[i]),str(tour[i+1]))
        G.add_edge(str(tour[-1]),str(tour[0]))
        
        G.layout("neato")
        G.write("fuckthis.dot")
        G.draw(output)


    def __len__(self):
        return len(self.matrix)

if __name__ == "__main__":
    #random.seed(1337)

    mapinfo = Parser().parse(sys.argv[1])
    tour = Tour(mapinfo, use_best=True)

    print "Starting tour:"
    tour.printTour()
    #mapinfo.graphvizify(tour.tour, "start.png")

    print
    print tour.score
    lscore = tour.score

    deltaE = -0.01

    iterationsOfNoChange = 0

    reheat = False

    try:
        while True:
            prevScore = tour.score

            if tour.annealKOpt(): #tour.annealSwap():
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
    print " score =", tour.score
    print " tour =", tour.printTour()
    mapinfo.graphvizify(tour.tour, "end.png")
