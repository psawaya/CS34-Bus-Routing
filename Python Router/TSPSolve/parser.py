from Tour import Tour

import random
import time

class Parser:
	def __init__(self,filename):
		lines = []

		with open (filename,'r') as f:
			lines = [ l.strip() for l in f.readlines()]

		relevantLines = filter(lambda x: x[0].isdigit(),lines)

		self.matrix = []

		for line in relevantLines:
			appendArray = [float(number) for number in line.split()]

			self.matrix.append(appendArray)
			
	def getCost(self, node1Idx, node2Idx):
		return self.matrix[node1Idx][node2Idx]

	def __len__(self):
		return len(self.matrix)

if __name__ == "__main__":
    random.seed(1337)
    
    parser = Parser("kro124p.atsp")
    tour = Tour(parser)
    tour.printTour()

    print
    print tour.score
    lscore = tour.score

    deltaE = -0.01
    
    iterationsOfNoChange = 0
    
    reheat = False

    while True:
        prevScore = tour.score
        
        if tour.annealSwap():            
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
    
    print tour.score
    tour.printTour()
