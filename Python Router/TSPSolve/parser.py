from Tour import Tour
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
    parser = Parser("p43.atsp")
    tour = Tour(parser)
    tour.printTour()
    #sn = tour.nodes[1].getNext().name
    #print 1, sn
    #tour.swap(1, sn)
    print
    print tour.score
    lscore = tour.score
    for i in range(100000):
        if tour.score < lscore:
            lscore = tour.score
            print tour.score
        tour.randSwap()
    print tour.score
    #print tour.score
    tour.printTour()
