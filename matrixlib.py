##########################
# Umieszczam dodatkowe komentarze dla elementów języka, które z tego co pamiętam różnią się od języka C,
# ale tylko w pierwszym ich wystąpieniu
# nie tłumaczę również elementów kodu które nie mają wiele wspólnego z głównym funkcjonowaniem klasy.




######################################
# Dodatkowe klasy błędów, które opisują dany błąd i zawierają dodatkowe dane 
# uważam, że biblioteka powinna wywoływać błędy zamiast sobie z nimi radzić, 
# tym powinien zająć się program jej używający.

class Matrix: pass

class MatrixException(Exception):

	def __init__(self, message, matrix=None, other=None):
		super().__init__(message)
		self.message = message
		self.matrix = matrix
		self.other = other

class InvalidMatrixOperation(MatrixException):

	def __str__(self):
		separator = "" if isinstance(other, Matrix) else "\n"  
		return f"\nInvalid operation between {self.matrix}and {self.other}{separator}{self.message}"

######################################



######################################
class Matrix:

	######################################
	# Założenia:
	#
	# array - oznacza tabele rozmarów N x M która jest wnętrznością macierzy.
	# values - rozpakowana lista wartości tabeli 'array'.
	#
	# obiekt tworzy się w następujący sposób: a = Matrix(	[i,j, ..],
	#							[k,l, ..],
	#							[  ...  ] )
	#
	# Klasy w pythonie nie muszą mieć wcześniej zadeklarowanych zmiennych/funkcji.
	# Istnieją więc rózne szkoły formatowania kodu klas, tutaj przyjmuje schemat: 
	# 	1. "funkcje magiczne", cechują się otoczeniem nazwy: __nazwa__(..)
	#	2. normalne funkcje, których w tym programie nie ma
	#	3. properties, własności obiektu (więcej w ich dziale)
	#	4. funkcje statyczne (tak jak w c++, zależne od klasy a nie obiektu)

	# Jeżeli chodzi o zrozumienie tego kodu to sugeruję kolejność:
	#	1. konstruktor __init__
	#	2. funkcje statyczne
	#	3. properties
	#	4. reszta funkcji magicznych
	#
	######################################


	# Operacje matematycze odbywać się będą głównie na zmiennych typu float, których prezycja sięga 16 miejsc po przecinku, 
	# żeby pozbyć się błędu liczbowego ustawiam nową podstawową precyzję 12 miejsc która usuwa błąd wynikający z ciągu operacji.
	# przykładowy problem, zamiast wartosci 0 dla dzielenia macierzy przez nią samą powstaje wartość 1.6e-17, 
	# Funkcja zaokrąglająca znajdująca się w sekcji funkcji statycznych, używana jest tylko do wyświetlania macierzy, pełne wartości nadal są przechowywane w array.  
	# (tylko dla wyświetlania macierzy, wartość 'pod spodem' nadal jest bardziej precyzyjna)
	PRECISION = 12


	# konstruktor klasy
	# W pythonie * spełnia inne funkcje niż w C.
	# W tym przypadku '*array' mówi o nieokreślonej ilości nienazwanych parametrów, według założenia wyżej każdy rząd wartości jest jednym parametrem. 
	# przykładowo dla stworzonego obiektu Matrix( [1,2], [3,4] ) przy notacji __init__(self, *array), array odczytuje się jako:
	# array => ([1,2], [3,4], )   (typ: tuple)
	# *array => [1,2], [3,4]	(typ: brak, zwraca całą zawartość jako kolejne argumenty)
	# dowolną liste można też tak wypakować aby stworzyć nowy obiekt przyjmujący *array (będzie później)
	def __init__(self, *array):
		if not isinstance(array, tuple): # isinstance() porównuje typy danych, pomocne do stwierdzenia warunków które powinny powodować błędy typu.
			raise MatrixException(f"Wrong initialization parameters. {array}")

		n_cols = len(array[0])
		for row in array:
			if len(row) != n_cols:
				raise MatrixException("Matrix has missing values.")

		self.array = list(array)
		self.size = [len(array), n_cols]


	# nadpisanie wyświetlania obiektu (np. dla funkcji print), używa wcześniej wspomnianego zaokrąglania dla czytelności
	def __str__(self):
		str_array = [ [Matrix.round_number(value) for value in row] for row in self.array ]
		# "List comprehension", syntax w pythonie pozwalający tworzenie nowej listy na bazie innej listy
		# pozwala na zagnieżdżanie, ale dla czytelności czasami z niego rezygnuje

		matrix_str = "\n".join( [str(row) for row in str_array] )
		return f"{self.size[0]}x{self.size[1]}:\n" + matrix_str + "\n"


	# nadpisywanie dodawania obiektów
	def __add__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return Matrix( *Matrix._to_array( [value + other for value in self.values], self.size ) )

		if not isinstance(other, Matrix):
			raise InvalidMatrixOperation(f"Trying to add type {type(other)} to a matrix.", self, other)

		if self.size != other.size:
			raise InvalidMatrixOperation("Adding two matrixes whose dimensions don't match.", self, other)

		new_array = []
		for row1,row2 in zip(self.array, other.array): # zip() zestawia ze sobą kolejne elementy dwóch list
			new_array.append( [val1+val2 for val1,val2 in zip(row1,row2)] )

		return Matrix(*new_array)

	# nadpisywanie odejmowania obiektów (wywołuje dodawanie przez -1*wartość)
	def __sub__(self, other):
		if isinstance(other, int) or isinstance(other, float) or isinstance(other, Matrix):
			return self.__add__(-1*other)
		raise InvalidMatrixOperation(f"Trying to substract type {type(other)} to a matrix.", self, other)

	# nadpisuje mnożenie macierzy
	def __mul__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return Matrix( *Matrix._to_array( [other*v for v in self.values], self.size ) )

		if not isinstance(other, Matrix):
			raise InvalidMatrixOperation(f"Trying to multiply a matrix by type {type(other)}.", self, other)

		if self.size[1] != other.size[0]:
			raise InvalidMatrixOperation(f"Multiplying matrices where number of columns of the first matrix doesn't match the number of rows of the second matrix.", self, other)

		# tworzę tabele kolumn (przykład 	[a,b,c]  ->  	[a,d] ) 	dla prawej macierzy (other)
		#					[d,e,f] 	[b,e] )
		#							[c,f] )
		array_of_columns = []
		for col_idx in range(0, other.size[1]):
			array_of_columns.append( 
				[ other.array[row_idx][col_idx] for row_idx in range(0, other.size[0]) ] 
			)

		# new_values będzie listą mieszczącą kolejne sumy z mnożenia wartości rzędu lewej macierzy i kolumny prawej macierzy.
		new_values = []
		for row in self.array:
			for col in array_of_columns:
				new_values.append( sum( [a*b for a,b in zip(row, col)] ) ) 
		# wyniki obliczane są z lewej do prawej (rząd w dół i powtórz) 
		# więc otrzymaną liste wartości wystarczy skonwertować do postaci 'array' która uwzględnia nową wielkość macierzy

		new_size = [self.size[0], other.size[1]]

		return Matrix( *Matrix._to_array(new_values, new_size) )


	# mnożenie gdy macierz znajduje się po prawej stronie znaku, nie trzeba uwzględniać typu Matrix bo działanie lewostronne klasy już to robi
	def __rmul__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return self.__mul__(other)

	# dzielenie, dla macierzy zwracam operacje mnożenia z parametrem odwrotności macierzy po prawej stronie znaku /
	def __truediv__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return Matrix( *Matrix._to_array( [v/other for v in self.values], self.size ) )

		if isinstance(other, Matrix):
			return self.__mul__(other.inverse)


	# daje możliwość indexowania wewnętrznego 'array' bezpośrednio przez obiekt klasy
	def __getitem__(self, idx):
		return self.array[idx]

	# sprawdzenie poprawności danych nie jest możliwe, gdyż w ten sposób indexuje jedynie rząd - który jest listą,
	# musiałbym stworzyć klase Row, która funkcjonowałaby jako lista, z nadpisaniem indexowania i sprawdzaniem danych. 
	def __setitem__(self, other):
		self.array[idx] = other


	######################################
	# Własności
	# Własność jest to dana w postaci funkcji, jest liczona przy wywołaniu, nie jest trzymana jako część obiektu.
	# podstawowo dekoratorem @property tworzy się 'getter' takiej własności, dodatkowo można stworzyć 'setter' również w postaci funkcji.
	
	# w wielu przypadkach w pythonie jedynym wpływem na zdecydowanie się użycia property zamiast zwyczajnej funkcji jest styl i czytelność kodu
	# dla obiektu Matrix A, w wersji property: A.values, a w postaci funkcji A.values(). - wyłącznie kwestia stylu gdy 'setter' nie jest wykorzystywany
	@property
	def values(self):
		values = []
		for row in self.array:
			values += row
		return values

	@property
	def inverse(self):
		if self.size[0] != self.size[1]:
			raise MatrixException(f"Trying to get the inverse of a non-square matrix", self)

		if self.size[0] == 2:
			a,b, c,d = self.values
			det = a*d-b*c
			if not det:
				raise MatrixException(f"Matrix determinant returned 0 when calculating the inverse.", self)
			return 1/det * Matrix( [d, -b],
								   [-c, a] )

		######################################
		# metoda skracania rzędów dla macierzy n x n, przemiana A|I => I|A^-1

		# uzyskuje macierz tożsamościową o odpowiedniej wielkości i łącze ją poziomo z oryginalną macierzą
		identity_matrix = Matrix.identity(self.size[0])
		new_array = [ self.array[n] + identity_matrix[n] for n in range(self.size[0]) ]
		
		for n in range(0, self.size[0]):

			# aktualny punkt na przekątnej przed zamianą na jedynke
			current_diagonal = new_array[n][n]

			# jeżeli wartość przekątnej wynosi 0 to zamieniam rzędy póki nie będzie miała innej wartości lub macierz się skończy
			if current_diagonal == 0:
				i = 1
				while current_diagonal == 0 and n + i < self.size[0]:
					new_array[n], new_array[n+i] = new_array[n+i], new_array[n] # w pythonie do zamiany nie jest potrzebna dana pośrednia
					i += 1
					current_diagonal = new_array[n][n]

			# jeżeli wartość przekątna nadal wynosi 0 to pozostałe rzędy były zerowe i nic nie może zmienić ich wartości
			# powstała mniejsza macierz nadal ma częściową odwrotność, w którą wkrada się błąd niedokończonych obliczeń,
			# zamiast w tym momencie wywołać błąd postanowiłem zwrócić częściową odwrotność macierzy
			if current_diagonal == 0:
				# zwraca tylko prawą część macierzy
				return Matrix( *[ new_array[row][self.size[0]:] for row in range(0, self.size[0]) ] ) 

			# wartości bierzącego rzędu zamieniam na macierz aby użyć znaków +-*/ co nie jest możliwe na listach
			# kolejny powód by stworzyć klasę rzędu
			row = Matrix(new_array[n])

			# bierzący rząd dziele przez odpowiadającą wartość na przekątnej aby otrzymać 1
			new_array[n] = (row/current_diagonal)[0] # indexowanie [0] zwraca cały rząd (lista) gdyż jest to obiekt Matrix o wielkości [1,n]


			# od każdego pozostałego rzędu odejmuje bierzący rząd pomnożony przez wartość którą chce wyzerować
			# wartości nie znajdujące się na przekątnej zerowane są kolejno kolumnami
			current = Matrix(new_array[n]) # ten sam powód na zmianę typu co 'row'
			for m in range(0, self.size[0]):
				if m == n: # pomijam aktualny rząd (nie zeruje przekątnej)
					continue

				# wartość która ma być wyzerowana, jeżeli już jest zerem to pomijam następną operację
				z = new_array[m][n]
				if z == 0:
					continue

				new_array[m] = ( Matrix(new_array[m]) - current*z )[0] # znowu indexowanie Matrix[0] żeby otrzymać wewnętrzny 'array'

		# zwraca tylko prawą część macierzy
		return Matrix( *[ new_array[row][self.size[0]:] for row in range(0,self.size[0]) ] ) 



	### Na początku używałem innej metody znajdywania odwrotności macierzy która wymagała znalezienia determinatora, ale metoda okazała się zbyt wolna dla większych macierzy.
	### Nie starałem się optymalizować tej własności ale zostawiłem ją w klasie na przyszłość, działa odpowiednio dla macierzy mniejszych niż 10x10.
	@property
	def determinant(self):
		if self.size == [2, 2]:
			a,b, c,d = self.values
			return a*d-b*c

		n_rows, n_cols = self.size
		if n_rows != n_cols:
			raise MatrixException(f"Trying to get the determinant of a non-square matrix.")


		det = 0
		is_addition = 1
		for ignored_col in range(0, n_cols):

			smaller_matrix = []
			for row in range(0, n_rows):
				if (row != 0):
					smaller_matrix.append(	self.array[row][:ignored_col] +
											self.array[row][ignored_col+1:] )

			partial = Matrix(*smaller_matrix).determinant * self.array[0][ignored_col]

			if is_addition:
				is_addition = 0
				det = det + partial
			else:
				is_addition = 1
				det = det - partial

		return det



	######################################
	# Funkcje statyczne

	# zaokrąglanie wyświetlanych liczb
	@staticmethod
	def round_number(num):
		new = round(num, ndigits=Matrix.PRECISION)
		if new == int(new):
			return int(new)
		return new

	# przekształca ciąg wartości do tabeli array o podanych wymiarach 
	@staticmethod
	def _to_array(values, size):
		array = []
		row_n, column_n = size

		for n in range(0, row_n):
			m = n*column_n
			array.append(values[m:m+column_n])
		return array

	# zwraca macierz tożsamościową o danej wielkości
	@staticmethod
	def identity(size):
		return Matrix( *[ [1 if n==m else 0 for n in range(size)] for m in range(size) ] )
