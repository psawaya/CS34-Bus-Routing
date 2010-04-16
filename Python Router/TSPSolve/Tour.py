import random
import sys

class Cycle(list):
    def __getitem__(self, i):
        return list.__getitem__(self, i % len(self))
    def __setitem__(self, i, v):
        list.__setitem__(self, i % len(self), v)
    def __getslice__(self, i, j):
        i = i % len(self)
        j = j % len(self)
        if i < j:
            return list.__getslice__(self, i, j)
        else:
            #if i == len(self) and j == 0:
            #    return [self[-1]]
            return list.__getslice__(self, i, len(self)) + list.__getslice__(self, 0, j)
    def __setslice__(self, i, j, v):
        i = i % len(self)
        j = j % len(self)
        if i < j:
            list.__setslice__(self, i, j, v)
        else:
            list.__setslice__(self, i, len(self), v[:len(self)-i])
            list.__setslice__(self, 0, j, v[len(self)-i:])


class TourNode(object):
    def __init__(self, name, heads=1):
        self.name = name
        self.heads = heads

class Tour(object):
    def __init__(self, distances, names=None, use_best=False):
        self.names = names or range(len(distances))
        self.nodes = map(TourNode, self.names)
        self.distances = distances
        self.score = sys.maxint
        self.heat = 1.0
        if use_best and self.distances.best_known is not None:
            self.tour = self.distances.best_known[:]
        else:
            self.tour = Cycle(self.names[:])
            random.shuffle(self.tour)
        self.score = self.calcScore()

    ### Node Swapping ###
    def scoreSwap(self, n1, n2):
        if abs(n2 - n1) <= 1 or abs(n2 - n1) == len(self.tour) - 1:
            old  = self.calcPartialScore(self.tour[n1-1:n2+2])
            new  = self.calcPartialScore([self.tour[n1-1], self.tour[n2], self.tour[n1], self.tour[n2+1]])
        else:
            old  = self.calcPartialScore(self.tour[n1-1:n1+2])
            old += self.calcPartialScore(self.tour[n2-1:n2+2])
            new  = self.calcPartialScore([self.tour[n1-1], self.tour[n2], self.tour[n1+1]])
            new += self.calcPartialScore([self.tour[n2-1], self.tour[n1], self.tour[n2+1]])

        return self.score - old + new

    def swap(self, i, j):
        self.score = self.scoreSwap(i, j)
        self.tour[i], self.tour[j] = self.tour[j], self.tour[i]

    def greedySwap(self, k1, k2):
        tscore = self.scoreSwap(k1,k2)
        if tscore < self.score:
            self.swap(k1, k2)
            return True
        return False

    def randGreedySwap(self):
        k1, k2 = random.sample(self.names, 2)
        self.greedySwap(k1, k2)

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
        tscore = self.scoreSwap(k1,k2)
        
        return (k1,k2,tscore)

    ### 2-Opt ###
    def scoreTwoOpt(self, e1, e2):
        v1, v2 = self.tour[e1], self.tour[e1+1]
        v3, v4 = self.tour[e2], self.tour[e2+1]
        old = self.getCost(v1, v2) + self.getCost(v3, v4)
        new = self.getCost(v3, v1) + self.getCost(v4, v2)

        seg = self.tour[e2+1:e1+1] # from v4 to v1
        old += self.calcPartialScore(seg)
        new += self.calcPartialScore(seg[::-1])
        return self.score - old + new

    def twoOptMove(self, e1, e2):
        if abs(e2 - e1) <= 1:
            return
        self.score = self.scoreTwoOpt(e1, e2)
        v1, v2 = self.tour[e1], self.tour[e1+1]
        v3, v4 = self.tour[e2], self.tour[e2+1]
        self.tour[e2+1:e1+1] = self.tour[e2+1:e1+1][::-1]

    def randTwoOptMove(self):
        e1, e2 = random.sample(range(len(self.tour)), 2)
        return self.greedyTwoOptMove(e1, e2)

    def greedyTwoOptMove(self, e1, e2):
        tscore = self.scoreTwoOpt(e1,e2)
        if tscore < self.score:
            self.twoOptMove(e1,e2)
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

    def getCost(self, v1, v2):
        return self.distances.getCost(v1, v2)

    def printTour(self, start=0):
        print " ".join(map(str, self.tour))

    def calcPartialScore(self, tour):
        score = 0
        for i in range(len(tour)-1):
            score += self.getCost(tour[i], tour[i+1])
        return score

    def calcScore(self):
        score = self.calcPartialScore(self.tour)
        score += self.getCost(self.tour[-1], self.tour[0])
        return score
