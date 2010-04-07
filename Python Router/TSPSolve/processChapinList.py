import sys

# Little script to process the scripts Paul Chapin sent us into matrices our code can use

f = open('crockerDistance.txt')

lines = f.readlines()

f.close()

lineTokens = [ [int(p) for p in line.split(",") ] for line in lines]

#find the max index, then add 1
matrixSize = 0

for token in lineTokens:
    matrixSize = max(matrixSize,token[0],token[1])

matrixSize+=1

# matrixSize = lineTokens[-1][0] + 1

#Use sys.maxint for nodes that don't have distances provided

matrix = [[ sys.maxint for b in range(matrixSize)] for a in range(matrixSize)]

for token in lineTokens:
    print token
    matrix[token[0]][token[1]] = token[2]
    matrix[token[1]][token[0]] = token[2]

outfile = open ('outputMatrix.txt','w')

for row in matrix:
    outfile.write ("\t".join(map(str,row)) + "\n")

outfile.close()

print matrix
