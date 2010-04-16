import random
import sys

class TourNode(object):
    def __init__(self, name, prev=None, next=None):
        self.name = name
        self.prev = None
        self.next = None
    def traverse(self, prev):
        if prev == self.prev:
            return self.next
        return self.prev
    def getPrev(self):
        if self.prev:
            return self.prev
        return None
    def getNext(self):
        if self.next:
            return self.next
        return None

class Tour(object):
    def __init__(self, distances, names=None, start_route=None, use_best=False):
        self.names = names or range(len(distances))
        self.nodes = dict(zip(self.names, map(TourNode, self.names)))
        self.distances = distances
        self.score = sys.maxint
        self.heat = 1.0
        if start_route is not None:
            self.tourFromIndices(start_route)
        else:
            if use_best and self.distances.best_known is not None:
                self.tourFromIndices(self.distances.best_known)
            else:
                random.shuffle(self.names)
                self.tourFromIndices(self.names)

    def tourFromIndices(self, ind):
        pairs = [(ind[i], ind[i+1]) for i in range(len(ind)-1)]
        self.setNext(self.nodes[pairs[-1][1]],self.nodes[pairs[0][0]])
        for i in range(len(pairs)):
            f,s = pairs[i]
            self.setNext(self.nodes[f], self.nodes[s])
        self.score = self.getScore()
        
    def tourToIndices(self):
        np = self.nodes.values()[0]
        first_node_name = np.name
        prev = np.prev
        
        tourIndices = [first_node_name]
        
        while np.next.name != first_node_name:
            prev, np = np, np.traverse(prev)
            
            tourIndices.append(np.name)

        return tourIndices

    ### Node Swapping ###
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
            # translate to x-node1-node2-y
            node1, node2 = node2, node1
            n1p, n2n = n2p, n1n
            n2p = node2
            n1n = node1
        elif n1n == node2 and n2p == node1:
            # order: x-node1-node2-y
            n2p = node2
            n1n = node1
        old  = self.getCost(n1p.name, node1.name)
        old += self.getCost(node1.name, n1n.name)
        old += self.getCost(n2p.name, node2.name)
        old += self.getCost(node2.name, n2n.name)

        new  = self.getCost(n1p.name, node2.name)
        new += self.getCost(node2.name, n1n.name)
        new += self.getCost(n2p.name, node1.name)
        new += self.getCost(node1.name, n2n.name)
        return self.score - old + new

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

    def randGreedySwap(self):
        k1, k2 = random.sample(self.names, 2)
        self.greedySwap(k1, k2)

    def greedySwap(self, k1, k2):
        tscore = self.potentialSwap(k1,k2)
        if tscore < self.score:
            self.swap(k1, k2)
            return True
        return False

    ### 2-Opt ###
    def twoOptScore(self, v1, v2, v3, v4):
        old = self.getCost(v1, v2) + self.getCost(v3, v4)
        new = self.getCost(v3, v1) + self.getCost(v4, v2)
        ptr = self.get(v4)
        # Reverse one of the sub-tours
        while ptr.prev.name != v1:
            if ptr.name != v1:
                old += self.getCost(ptr.name, ptr.next.name)
            if ptr.name != v4:
                new += self.getCost(ptr.name, ptr.prev.name)
            ptr = ptr.next
        return (self.score - old) + new

    def twoOptMove(self, v1, v2, v3, v4):
        if v1 in (v3, v4) or v2 in (v3, v4):
            return
        ptr = self.get(v4)
        # Reverse one of the sub-tours
        while ptr.prev.name != v1:
            tmp = ptr.next
            ptr.next = ptr.prev
            ptr.prev = tmp
            ptr = tmp
        # Stitch everything back together
        self.setNext(self.get(v3), self.get(v1))
        self.setNext(self.get(v4), self.get(v2))

    def randTwoOptMove(self):
        k1, k2 = random.sample(self.names, 2)
        case = random.randint(0,1)
        #print self.getPrev(k1), k1, self.getNext(k1), self.getPrev(k2), k2, self.getNext(k2)
        if case == 0:
            return self.greedyTwoOptMove(k1, self.getNext(k1), k2, self.getNext(k2))
        elif case == 1:
            return self.greedyTwoOptMove(self.getPrev(k1), k1, self.getPrev(k2), k2)

    def greedyTwoOptMove(self, v1, v2, v3, v4):
        tscore = self.twoOptScore(v1,v2,v3,v4)
        if tscore < self.score:
            self.twoOptMove(v1,v2,v3,v4)
            self.score = tscore
            return True
        return False
        
    def annealTwoOpt(self):
        n1,n3,_ = self.randomPair()
        
        n2 = self.getNext(n1)
        n4 = self.getNext(n3)
        
        tscore = self.twoOptScore(n1,n2,n3,n4)
        
        # print "my score: %s two opt score: %s" % (self.score, tscore)
        
        if tscore < self.score or random.random() < self.heat:
            self.twoOptMove(n1,n2,n3,n4)
            self.score = tscore #twoOptMove doesn't update score
            return True

        return False

    ### Util ###
    def getPrev(self, v):
        return self.nodes.get(v).getPrev().name

    def getNext(self, v):
        return self.nodes.get(v).getNext().name

    def setPrev(self, node, prev):
        self.setNext(prev, node)

    def setNext(self, node, next):
        node.next = next
        next.prev = node
        dnx = self.getCost(node.name, next.name)

    def get(self, v1):
        return self.nodes.get(v1)

    def getCost(self, v1, v2):
        return self.distances.getCost(v1, v2)

    def printTour(self, start=0):
        np = self.nodes.get(start)
        prev = np.prev
        c = len(self.nodes)
        print np.name,
        while np.next.name != start and c:
            prev, np = np, np.traverse(prev)
            c -= 1
            print np.name,
        print

    def getScore(self):
        np = self.nodes.values()[0]
        first_node_name = np.name
        prev = np.prev
        score = 0
        while np.next.name != first_node_name:
            score += self.getCost(np.name, np.next.name)
            prev, np = np, np.traverse(prev)
        return score + self.getCost(np.name, np.next.name)
