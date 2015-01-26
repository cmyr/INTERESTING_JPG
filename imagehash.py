
# from https://github.com/JohannesBuchner/imagehash.
# copied because i needed to remove some references to a scipy package


"""
Image hashing library
======================

Example:

>>> import Image
>>> import imagehash
>>> hash = imagehash.average_hash(Image.open('test.png'))
>>> print(hash)
d879f8f89b1bbf
>>> otherhash = imagehash.average_hash(Image.open('other.bmp'))
>>> print(otherhash)
ffff3720200ffff
>>> print(hash == otherhash)
False
>>> print(hash - otherhash)
36
>>> for r in range(1, 30, 5):
...     rothash = imagehash.average_hash(Image.open('test.png').rotate(r))
...     print('Rotation by %d: %d Hamming difference' % (r, hash - rothash))
... 
Rotation by 1: 2 Hamming difference
Rotation by 6: 11 Hamming difference
Rotation by 11: 13 Hamming difference
Rotation by 16: 17 Hamming difference
Rotation by 21: 19 Hamming difference
Rotation by 26: 21 Hamming difference
>>>

"""

from PIL import Image
import numpy
import requests
import shutil
import os


def binary_array_to_hex(arr):
	h = 0
	s = []
	for i,v in enumerate(arr.flatten()):
		if v: h += 2**(i % 8)
		if (i % 8) == 7:
			s.append(hex(h)[2:].rjust(2, '0'))
			h = 0
	return "".join(s)

def binary_array_to_int(arr):
	return sum([2**(i % 8) for i,v in enumerate(arr.flatten()) if v])

"""
Hash encapsulation. Can be used for dictionary keys and comparisons.
"""
class ImageHash(object):
	def __init__(self, binary_array):
		self.hash = binary_array

	def __str__(self):
		return binary_array_to_hex(self.hash)

	def __repr__(self):
		return repr(self.hash)

	def __sub__(self, other):
		if other is None:
			raise TypeError('Other hash must not be None.')
		if self.hash.shape != other.hash.shape:
			raise TypeError('ImageHashes must be of the same shape.', self.hash.shape, other.hash.shape)
		return (self.hash != other.hash).sum()

	def __eq__(self, other):
		if other is None:
			return False
		return numpy.array_equal(self.hash, other.hash)

	def __ne__(self, other):
		if other is None:
			return False
		return not numpy.array_equal(self.hash, other.hash)

	def __hash__(self):
		return binary_array_to_int(self.hash)

def hex_to_hash(hexstr):
	l = []
	if len(hexstr) != 16:
		raise ValueError('The hex string has the wrong length')
	for i in range(8):
		#for h in hexstr[::2]:
		h = hexstr[i*2:i*2+2]
		v = int("0x" + h, 16)
		for i in range(8):
			l.append(v & 2**i > 0)
	return ImageHash(numpy.array(l))


"""
Average Hash computation

Implementation follows http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html

@image must be a PIL instance.
"""
def average_hash(image, hash_size=8):
	image = image.convert("L").resize((hash_size, hash_size), Image.ANTIALIAS)
	pixels = numpy.array(image.getdata()).reshape((hash_size, hash_size))
	avg = pixels.mean()
	diff = pixels > avg
	# make a hash
	return ImageHash(diff)


"""
Difference Hash computation.

following http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html

@image must be a PIL instance.
"""
def dhash(image, hash_size=8):
	image = image.convert("L").resize((hash_size + 1, hash_size), Image.ANTIALIAS)
	pixels = numpy.array(image.getdata(), dtype=numpy.float).reshape((hash_size + 1, hash_size))
	# compute differences
	diff = pixels[1:,:] > pixels[:-1,:]
	return ImageHash(diff)


TEMP_IMAGE_FILE_NAME = "tmpimage2"

def image_hash(img_url):
    response = requests.get(img_url, stream=True)
    response.raw.decode_content = True
    with open(TEMP_IMAGE_FILE_NAME, 'wb') as tmp:
        shutil.copyfileobj(response.raw, tmp)

    img = Image.open(TEMP_IMAGE_FILE_NAME)
    image_hash = dhash(img)
    os.remove(TEMP_IMAGE_FILE_NAME)
    return image_hash


def main():
    import imagefetching
    img_urls = imagefetching.reuters_slideshow_imgs()
    last_hash = None
    for caption, link in img_urls:
    	img_hash = image_hash(link)
    	if last_hash == None:
    		last_hash = img_hash
        print(img_hash)
    	print("diff ", img_hash - last_hash)
        last_hash = img_hash

if __name__ == "__main__":
	main()