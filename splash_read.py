import sys, os
from PIL import Image
from splash import readHeader, readData, SECTOR_SIZE_IN_BYTES

if __name__ == "__main__":
	if len(sys.argv) < 3 or len(sys.argv) > 4:
		print(" usage: python logo_read.py <input file> <splash image> [fastboot image]")
		sys.exit()

	infile = sys.argv[1]
	splashfile = sys.argv[2]
	fastbootfile = ''
	if len(sys.argv) == 4:
		fastbootfile = sys.argv[3]

	if not os.access(infile, os.R_OK):
		print('Failed to open ' + infile + '.')
		sys.exit()

	file = open(infile, "rb")

	img = open(splashfile, "wb")
	width, height, compressed, real_size = readHeader(file.read(SECTOR_SIZE_IN_BYTES))
	img.write(readData(file.read(real_size * SECTOR_SIZE_IN_BYTES), (width, height), compressed))
	img.close()
	
	header2 = file.read(SECTOR_SIZE_IN_BYTES)
	if not fastbootfile == '' and not header2 == '':
		img = open(fastbootfile, "wb")
		width, height, compressed, real_size = readHeader(header2)
		img.write(readData(file.read(real_size * SECTOR_SIZE_IN_BYTES), (width, height), compressed))
		img.close()

	file.close()
