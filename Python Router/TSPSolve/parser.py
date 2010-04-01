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

parser = Parser("p43.atsp")
tour = Tour(parser)