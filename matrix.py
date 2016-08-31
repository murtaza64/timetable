from time import sleep
from struct import *
from scrollalphabet import *
import sys, os

errors=''
EMPTYTRIPLE=(0,0,0)
WHITE=(255,255,255)
def monochrome(inMatrix):
	matrix=[]
	for row in inMatrix:
		matrix.append([])
		for cell in row:
			if cell==1:
				matrix[-1].append(WHITE)
			else:
				matrix[-1].append(EMPTYTRIPLE)
	return matrix
def makeBMP(matrix, name):
	global errors
	w, h = 0, 0
	for row in matrix:
		h+=1
	for cell in matrix[0]:
		w+=1
	depth = 24
	padding = int(4 - (w*(depth/8) %4)) if (w*(depth/8) % 4 != 0) else 0
	bytes_per_row = int (w*(depth/8) + padding) 
	bytes_in_image = h*bytes_per_row

	size = 54 + bytes_in_image
	BITMAPFILEHEADER = pack('<hihhi',0x4D42, size, 0, 0, 54)

	BITMAPINFOHEADER = pack('<iiihhiiiiii', 40, w, -h, 1, depth, 0, bytes_in_image, 2835, 2835, 0, 0)

	imagebytes = []

	for row in matrix:
		for cell in row:
			red=cell[0].to_bytes(1, byteorder='little')
			green=cell[2].to_bytes(1, byteorder='little')
			blue=cell[1].to_bytes(1, byteorder='little')

			imagebytes.append(blue)
			imagebytes.append(green)
			imagebytes.append(red)
			
		for i in range(0, padding):
			imagebytes.append((0).to_bytes(1, byteorder='little'))
	try:
		image=open('bmp/'+name, 'wb')
		image.write(BITMAPFILEHEADER)
		image.write(BITMAPINFOHEADER)
		for byte in imagebytes:
			image.write(byte)
		image.close()
	except PermissionError:
		print('permission denied in ' + 'bmp/' + name)
		errors += 'permission denied in ' + 'bmp/' + name + '\n'
	except FileNotFoundError:
		os.makedirs('bmp/')
	

class pixelmatrix:
	def __init__(self, dims=(8,8), BMP=0, _print=1):
		self.matrix=[]
		self.frame=0
		y=dims[0]
		x=dims[1]
		self.ylen=y
		self.xlen=x
		self.BMP=BMP
		self._print=_print
		for i in range (y):
			row=[EMPTYTRIPLE for k in range (x)]
			self.matrix.append(row)
	def __getitem__(self, key):
		return self.matrix[key]
	def step(self):
		if self._print:
			for row in self.matrix:
				print('[', end='')
				for cell in row:
					if cell == EMPTYTRIPLE:
						print(' ', end ='')
					else:
						print('X', end ='')
				print(']\n', end='')
			print('\n')
		filename='{0:0>3}.bmp'.format(self.frame)
		self.frame+=1
		sleep(0.1)
		if self.BMP:
			makeBMP(self.matrix, filename)

	def update(self, inMatrix, coords=(0,0)):
		y,x=coords
		ylen=len(inMatrix)
		xlen=len(inMatrix[0])
		for i, row in enumerate(inMatrix):
			for j, cell in enumerate(row):
				self.matrix[y+i][x+j] = cell

	def newRow(self):
		return [EMPTYTRIPLE for k in range (self.xlen)]
	def newCol(self):
		return [EMPTYTRIPLE for k in range (self.ylen)]
	def pushRow(self, row, side='bottom'):
		xin = len(row)
		if side == 'bottom':
			del self.matrix[0]
			self.matrix.append(self.newRow())
			for i in range (xin):
				self.matrix[-1][i]=row[i]
		if side == 'top':
			del self.matrix[-1]
			self.matrix.insert(0, self.newRow())
			for i in range (xin):
				self.matrix[0][i]=row[i]
	def pushCol(self, col, side='right'):
		yin = len(col)
		if side == 'right':
			for row in self.matrix:
				row.pop(0)
			for i in range (yin):
				self.matrix[i].append(col[i])
			for j in range (i+1, self.ylen):
				self.matrix[j].append(EMPTYTRIPLE)
		if side == 'left':
			for row in self.matrix:
				row.pop()
			for i in range (yin):
				self.matrix[i].insert(0, col[i])
			for j in range (i+1, self.ylen):
				self.matrix[j].insert(0, EMPTYTRIPLE)
	def scroll(self, inMatrix):
		width=len(inMatrix[0])
		for i in range (width):
			col=[]
			for row in inMatrix:
				col.append(row[i])
			self.pushCol(col)
			self.step()
			
	def scrollText(self, str):
		for char in str:
			chargrid=monochrome(scrollAlphabet[char])
			self.scroll(chargrid)
			self.pushCol(self.newCol())
			self.step()
		for i in range (self.xlen):
			self.pushCol(self.newCol())
			self.step()

if __name__ == "__main__":
	testStr='OO'

	#scrollMatrix(testStr)

	#updateMatrix(testMatrix, (4,4))
	#showMatrix()

	screen = pixelmatrix(dims=(8,16))
	screen.step()
	screen.scrollText(sys.argv[1])
	screen.update(monochrome(testMatrix), (4,4))
	screen.step()
	print(errors)