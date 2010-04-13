import random
import sys

class TourNode(object):
    def __init__(self, name, prev=None, next=None):
        self.name = name
        self.prev = None
        self.next = None
        self.nDist = 0
    def getPrev(self):
        if self.prev:
            return self.prev
        return None
    def getNext(self):
        if self.next:
            return self.next
        return None

class Tour(object):
    def __init__(self, distances):
        self.names = range(len(distances))
        self.nodes = dict(zip(self.names, map(TourNode, self.names)))
        self.distances = distances
        self.score = sys.maxint
        self.heat = 1.0
        random.shuffle(self.names)
        self.tourFromIndices(self.names)
        
    def __init__(self, distances, indices, scramble_indices=False):
        self.names = indices
        self.nodes = dict(zip(indices, map(TourNode, indices)))
        self.distances = distances
        self.score = sys.maxint
        self.heat = 1.0
        
        if scramble_indices:
            random.shuffle(indices)
        
        self.tourFromIndices(indices)
    
    def tourNamesArray(self):
        namesArray = []
        
        #Consistently start with the same node
        firstNode = self.nodes.items()[0][1]
        nextNode = firstNode
        
        while True :
            
            print nextNode
            
            namesArray.append(nextNode.name)
            nextNode = nextNode.getNext()
            
            if nextNode == firstNode:
                break
        
        return namesArray

    def tourFromIndices(self, ind):
        pairs = [(ind[i], ind[i+1]) for i in range(len(ind)-1)]
        dist = map(lambda x: self.distances.getCost(*x), pairs)
        borderDist = self.distances.getCost(ind[-1], ind[0])
        self.setNext(self.nodes[pairs[-1][1]],self.nodes[pairs[0][0]])
        self.setPrev(self.nodes[pairs[0][0]], self.nodes[pairs[-1][1]])
        for i in range(len(pairs)):
            f,s = pairs[i]
            self.setNext(self.nodes[f], self.nodes[s])
            self.setPrev(self.nodes[s], self.nodes[f])
        self.score = sum(dist) + borderDist

    def potentialSwap(self, n1, n2):
        node1 = self.nodes.get(n1)
        node2 = self.nodes.get(n2)
        n1p = node1.getPrev()
        n1n = node1.getNext()
        n2p = node2.getPrev()
        n2n = node2.getNext()
        # handle swaps between adjacent nodes
        if n1p == node2 and n2n == node1:
            # order: x-node2-node1-y
            n2p = node2.getPrev()
            n2n = node2
            n1p = node1
            n1n = node1.getNext()
            odist  = self.distances.getCost(n2p.name, node2.name)
            odist += self.distances.getCost(node2.name, node1.name)
            odist += self.distances.getCost(node1.name, n1n.name)

            ndist  = self.distances.getCost(n2p.name, node1.name)
            ndist += self.distances.getCost(node1.name, node2.name)
            ndist += self.distances.getCost(node2.name, n1n.name)
        elif n1n == node2 and n2p == node1:
            # order: x-node1-node2-y
            n2p = node2
            n2n = node2.getNext()
            n1p = node1.getPrev()
            n1n = node1
            odist  = self.distances.getCost(n1p.name, node1.name)
            odist += self.distances.getCost(node1.name, node2.name)
            odist += self.distances.getCost(node2.name, n2n.name)

            ndist  = self.distances.getCost(n1p.name, node2.name)
            ndist += self.distances.getCost(node2.name, node1.name)
            ndist += self.distances.getCost(node1.name, n2n.name)
        else:
            odist  = self.distances.getCost(n1p.name, node1.name)
            odist += self.distances.getCost(node1.name, n1n.name)
            odist += self.distances.getCost(n2p.name, node2.name)
            odist += self.distances.getCost(node2.name, n2n.name)

            ndist  = self.distances.getCost(n1p.name, node2.name)
            ndist += self.distances.getCost(node2.name, n1n.name)
            ndist += self.distances.getCost(n2p.name, node1.name)
            ndist += self.distances.getCost(node1.name, n2n.name)
        return self.score - odist + ndist
    
    def annealSwap(self):
        n1,n2,tscore = self.randomPair()
        
        if tscore < self.score:
            self.swap(n1,n2)
            return True
        else:
            # print "a: %s b: %s " % (random.random(),self.heat)
            if random.random() < self.heat:
                self.swap(n1,n2)                
                return True

            return False

    def randomPair(self):
        k1, k2 = random.sample(self.names, 2)
        tscore = self.potentialSwap(k1,k2)
        
        return (k1,k2,tscore)

    def randSwap(self):
        k1, k2 = random.sample(self.names, 2)
        tscore = self.potentialSwap(k1,k2)
        if tscore < self.score:
            self.swap(k1, k2)

    def swap(self, n1, n2):
        self.score = self.potentialSwap(n1, n2)
        node1 = self.nodes.get(n1)
        node2 = self.nodes.get(n2)
        n1p = node1.getPrev()
        n1n = node1.getNext()
        n2p = node2.getPrev()
        n2n = node2.getNext()
        # handle swaps between adjacent nodes
        if n1p == node2 and n2n == node1:
            n2p = node2.getPrev()
            n2n = node2
            n1p = node1
            n1n = node1.getNext()
        elif n1n == node2 and n2p == node1:
            n2p = node2
            n2n = node2.getNext()
            n1p = node1.getPrev()
            n1n = node1
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

    def setNext(self, node, next):
        node.next = next
        next.prev = node
        dnx = self.distances.getCost(node.name, next.name)
        dxn = self.distances.getCost(next.name, node.name)
        node.nDist = dnx

    def printTour(self, start=0):
        np = self.nodes.get(start)
        print np.name,
        while np.next.name != start:
            np = np.next
            print np.name,
        print
