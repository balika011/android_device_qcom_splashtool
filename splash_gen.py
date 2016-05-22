import sys, os
from PIL import Image
from splash import genHeader, genData, SECTOR_SIZE_IN_BYTES

SUPPORT_RLE24_COMPRESSIONT = True
USE_XIAOMI_FASTBOOT_LOGO_ALGO = True
XIAOMI_FASTBOOT_LOGO_OFFSET = 0x12E00

if __name__ == "__main__":
	if len(sys.argv) < 3 or len(sys.argv) > 4:
		print(" usage: python logo_gen.py <splash image> [fastboot image] <output file>")
		sys.exit()

	splashfile = sys.argv[1]
	fastbootfile = ''
	outfile = sys.argv[2]
	if len(sys.argv) == 4:
		fastbootfile = sys.argv[2]
		outfile = sys.argv[3]

	if not os.access(splashfile, os.R_OK):
		print 'Failed to open',  splashfile, '.'
		sys.exit()
		
	if len(sys.argv) == 4 and not os.access(fastbootfile, os.R_OK):
		print 'Failed to open', fastbootfile, '.'
		sys.exit()

	file = open(outfile, "wb")

	img = Image.open(splashfile)
	data = genData(img, SUPPORT_RLE24_COMPRESSIONT)
	file.write(genHeader(img.size, len(data), SUPPORT_RLE24_COMPRESSIONT))
	file.write(data)
	
	if len(sys.argv) == 4:
		if USE_XIAOMI_FASTBOOT_LOGO_ALGO:
			if file.tell() < XIAOMI_FASTBOOT_LOGO_OFFSET:
				file.write('\0' * (XIAOMI_FASTBOOT_LOGO_OFFSET - file.tell()))
			else:
				print 'XiaoRekt: Size of splash', file.tell(), 'is bigger then', XIAOMI_FASTBOOT_LOGO_OFFSET, '.'
				print 'XiaoRekt: Unable to generate fastboot image.'
				file.close()
				sys.exit()
		else:
			file.write('\0' * (len(data) - ((real_bytes + SECTOR_SIZE_IN_BYTES - 1) / SECTOR_SIZE_IN_BYTES)))

		img = Image.open(fastbootfile)
		data = genData(img, SUPPORT_RLE24_COMPRESSIONT)
		file.write(genHeader(img.size, len(data), SUPPORT_RLE24_COMPRESSIONT))
		file.write(data)

	file.close()
