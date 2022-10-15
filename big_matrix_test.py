from matrixlib import Matrix
import random



# random.seed(12345)

size = 100
a = []
for _ in range(0, size):
	a.append( [random.randrange(0,100,1) for _ in range(0, size)] )



A = Matrix( *a )

Matrix.PRECISION = 6
print(A*A.inverse)
# prawie natychmiastowe dla wielkości 100x100, dla wielkości 200x200 operacja zajmuje do 10 sekund.
