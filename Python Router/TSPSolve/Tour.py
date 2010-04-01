import random
import sys

class TourNode(object):
    def __init__(self, name, prev=None, next=None):
        self.name = name
        self.prev = None
        self.pDist = 0
        self.next = None
        self.nDist = 0
    def getPrev(self):
        if self.prev:
            return (self.prev, self.pDist)
        return (None, 0)
    def getNext(self):
        if self.next:
            return (self.next, self.nDist)
        return (None, 0)

class Tour(object):
    def __init__(self, distances):
        self.names = range(len(distances))
        self.nodes = dict(zip(self.names, map(TourNode, self.names)))
        self.score = sys.maxint
        self.distances = distances
        random.shuffle(self.names)
        self.tourFromIndices(self.names)

    def tourFromIndices(self, ind):
        pairs = [(ind[i], ind[i+1]) for i in range(len(ind)-1)]
        dist = map(lambda x: self.distances.getCost(*x), pairs)
        borderDist = self.distances.getCost(ind[0], ind[-1])
        self.setPrev(self.nodes[pairs[0][0]], self.nodes[pairs[-1][1]])
        self.setPrev(self.nodes[pairs[-1][1]],self.nodes[pairs[0][0]]) 
        for i in range(len(pairs)):
            f,s = pairs[i]
            self.setNext(self.nodes[f], self.nodes[s])
            self.setPrev(self.nodes[s], self.nodes[f])

    def potentialSwap(self, n1, n2):
        node1 = self.nodes.get(n1)
        node2 = self.nodes.get(n1)
        (n1p, n1pd) = node1.getPrev()
        (n1n, n1nd) = node1.getNext()
        (n2p, n2pd) = node2.getPrev()
        (n2n, n2nd) = node2.getNext()
        dn1n2p = self.distances.getCost(n1, n2p.name)
        dn1n2n = self.distances.getCost(n1, n2n.name)
        dn2n1p = self.distances.getCost(n2, n1p.name)
        dn2n1n = self.distances.getCost(n2, n1n.name)
        tscore = self.score
        tscore -= (n1pd + n1nd + n2pd + n2nd)
        tscore += (dn1n2p + dn1n2n + dn2n1p + dn2n1n)
        return tscore

    def randSwap(self):
        k1, k2 = random.sample(self.names, 2)
        tscore = self.potentialSwap(k1,k2)
        if tscore >= self.score:
            self.swap(k1, k2)

    def swap(self, n1, n2):
        self.score = self.potentialSwap(n1, n2)
        node1 = self.nodes.get(n1)
        node2 = self.nodes.get(n2)
        (n1p, q) = node1.getPrev()
        (n1n, q) = node1.getNext()
        (n2p, q) = node2.getPrev()
        (n2n, q) = node2.getNext()
        print n1p.name, n1, n2, n2n.name
        if n1p in (node1, node2):
            print "doing n1p"
            (n1p,_) = n1p.getPrev()
        if n2p in (node1, node2):
            print "doing n2p"
            (n2p,_) = n2p.getPrev()
        if n1n in (node1, node2):
            print "doing n1n"
            (n1n,_) = n1n.getNext()
        if n2n in (node1, node2):
            print "doing n2n"
            (n2n,_) = n2n.getNext()
        print n1p.name, n1, n2, n2n.name
        self.setPrev(node1, n2p)
        self.setNext(node1, n2n)
        self.setPrev(node2, n1p)
        self.setNext(node2, n1n)

    def setPrev(self, node, prev):
        node.prev = prev
        prev.next = node
        dnp = self.distances.getCost(node.name, prev.name)
        dpn = self.distances.getCost(prev.name, node.name)
        prev.nDist = dpn
        node.pDist = dnp

    def setNext(self, node, next):
        node.next = next
        next.prev = node
        dnx = self.distances.getCost(node.name, next.name)
        dxn = self.distances.getCost(next.name, node.name)
        next.pDist = dxn
        node.nDist = dnx

    def printTour(self):
        np = self.nodes.get(0)
        print np.name,
        while np.next.name != 0:
            np = np.next
            print np.name,
        print
