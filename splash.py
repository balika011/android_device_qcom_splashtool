import sys, os, StringIO
from struct import pack, unpack
from PIL import Image
from RLE24 import encodeRLE24, decodeRLE24

SECTOR_SIZE_IN_BYTES = 512
QCSPLASH_MAGIC = 'SPLASH!!'

def genHeader(size, real_bytes, compressed = False):
	header = [0 for i in range(SECTOR_SIZE_IN_BYTES)]

	width, height = size
	real_size = (real_bytes + SECTOR_SIZE_IN_BYTES - 1) / SECTOR_SIZE_IN_BYTES

	# magic
	header[:8] = [ord(chr) for chr in QCSPLASH_MAGIC]

	# width
	header[8] = (width	& 0xFF)
	header[9] = ((width >> 8) & 0xFF)
	header[10]= ((width >> 16) & 0xFF)
	header[11]= ((width >> 24) & 0xFF)

	# height
	header[12]= (height	& 0xFF)
	header[13]= ((height >> 8) & 0xFF)
	header[14]= ((height >> 16) & 0xFF)
	header[15]= ((height >> 24) & 0xFF)

	# type
	header[16]= (compressed	& 0xFF)
	header[17]= 0
	header[18]= 0
	header[19]= 0

	# block number
	header[20] = (real_size	& 0xFF)
	header[21] = ((real_size >> 8) & 0xFF)
	header[22] = ((real_size >> 16) & 0xFF)
	header[23] = ((real_size >> 24) & 0xFF)

	return ''.join([pack("B", i) for i in header])
	
def readHeader(buffer):
	pos = 0
	magic = ''
	for i in range(8):
		magic += chr(unpack("B", buffer[pos : pos + 1])[0])
		pos += 1
		
	if not magic == QCSPLASH_MAGIC:
		print 'Wrong splash magic!'
		sys.exit()
	
	width = unpack("B", buffer[pos : pos + 1])[0]
	pos += 1
	width |= unpack("B", buffer[pos : pos + 1])[0] << 8
	pos += 1
	width |= unpack("B", buffer[pos : pos + 1])[0] << 16
	pos += 1
	width |= unpack("B", buffer[pos : pos + 1])[0] << 24
	pos += 1
	
	height = unpack("B", buffer[pos : pos + 1])[0]
	pos += 1
	height |= unpack("B", buffer[pos : pos + 1])[0] << 8
	pos += 1
	height |= unpack("B", buffer[pos : pos + 1])[0] << 16
	pos += 1
	height |= unpack("B", buffer[pos : pos + 1])[0] << 24
	pos += 1
	
	compressed = unpack("B", buffer[pos : pos + 1])[0]
	pos += 1
	pos += 1
	pos += 1
	pos += 1
	
	real_size = unpack("B", buffer[pos : pos + 1])[0]
	pos += 1
	real_size |= unpack("B", buffer[pos : pos + 1])[0] << 8
	pos += 1
	real_size |= unpack("B", buffer[pos : pos + 1])[0] << 16
	pos += 1
	real_size |= unpack("B", buffer[pos : pos + 1])[0] << 24
	pos += 1

	return width, height, compressed, real_size
	
def genData(img, compressed = False):
	bgcolor = (0x00, 0x00, 0x00)
	
	if img.mode == "RGB" or img.mode == "P" or img.mode == "L":
		background = Image.new("RGB", img.size, bgcolor)
		img.load()
		background.paste(img)
	elif img.mode == "RGBA":
		background = Image.new("RGB", img.size, bgcolor)
		img.load()
		background.paste(img, mask = img.split()[3]) # alpha channel
	else:
		print ("sorry, can't support this format")
		sys.exit()
	
	if compressed:
		return encodeRLE24(background)
	else:
		r, g, b = background.split()
		return Image.merge("RGB", (b, g, r)).tostring()
	
def readData(buffer, size, compressed = False):
	img = 0
	if compressed:
		img = decodeRLE24(buffer, size)
	else:
		bgcolor = (0x00, 0x00, 0x00)
		width, height = size
		img = Image.new("RGB", size, bgcolor)
		pixels = img.load()
		hw = 0
		while hw < height * width:
			pixels[hw % width, hw / width] = (ord(buffer[hw * 3 + 2]), ord(buffer[hw * 3 + 1]), ord(buffer[hw * 3]))
			hw += 1

	buf = StringIO.StringIO()
	img.save(buf, format = 'PNG')
	return buf.getvalue()
	
#def picsa(background):
#	rle = encodeRLE24(background)
#	img = decodeRLE24(rle, background.size)
#	img.save("decoded.png")

#	img = Image.new("RGB", bg.size, bgcolor)
#	imgpixels = img.load()
	
#	hw = 0
#	while hw < height * width:
#		imgpixels[hw % width, hw / width] = pixels[hw]
#		hw += 1

#	return img
#	return img