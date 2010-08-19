import os.path, imghdr, PIL.Image
from array import array

class Image(object):
	""" This class represents an image object and provides the basic
	methods to manipulate it. Images can use RGB color mode or Gray scale. """
	
	def GradientImage(color1, color2, direction="left-right"):
		""" This method creates a new gradient image. If is colored gradient image
		 the parameters color1 and color2 must be triples using the RGB color mode.
		 If not color1 and color2 must be bytes with the corresponding 0-255 gray values.
		 The optional direction parameters sets the directions in which de gradient will be set.
		 The valid options are left-right, right-left, top-bottom, bottom-top"""
		raise NotImplementedError
	
	def __init__(self, filename, width=None, height=None, format="bmp", color=False):
		""" The image can be initialized from a file by giving it's path. If the image's type is raw,
		 the image's size must be given by setting the parameters width and height. By default all the
		 raw type images are in gray-scale, if the images uses the RGB color mode the color parameter
		 must be set to True. If you want to create a new image the image's filename and size must be
		set. Optional parameters are format and color which by default are set to bmp and False """
		if not os.path.isfile(fname):
			if not width or not height:
				raise AssertionError("The image's size must be set")
			self.__width = width
			self.__height = height
			self.__format = format
			self.__image_file = open(filename, "rwb")
			self.__color = color
		else:
			self.__filename = filename
			self.__format = imghdr.what(filename)
			if not self.__format:
				self.__format = "raw"
				if not width or not height:
					raise AssertionError("The image %s is a raw image, it's width and height must be defined." % filename)
				self.__width = width
				self.__height = height
				if color:
					raise NotImplementedError("Raw colored images not supported yet")
				self.__color = color
				file = open(filename)
				self.__bytes = array("B", file.read())
			else:
				image = PIL.Image.open(filename)
				if image.mode == "1":
					self.__color = False
				elif image.mode == "RGB":
					self.__color = True
				else:
					raise AssertionError("Color mode %s not supported" % image.mode)
				self.__width, self.__height = image.size
				self.__bytes = list(image.getdata())
		
	def __get_filename(self):
		return self.__filename
	
	def __get_width(self):
		return self.__width
	
	def __get_height(self):
		return self.__height
		
	def __get_format(self):
		return self.__format	
		
	def __get_bytes(self):
		return self.__bytes
		
	filename = property(__get_filename)
	width = property(__get_width)
	height = property(__get_height)
	format = property(__get_format)
	bytes = property(__get_bytes)
	
	def is_colored(self):
		return self.__color
	
	def get_pixel(self, x, y):
		""" Returns the pixel value pointed by the x & y coordinates. If it's a colored image
		the method will return a triple containing the RGB channels, otherwise it will return a byte """
		return self.__bytes[(self.__width * y) + x]	
		
	def set_pixel(self, x, y, value):
		self.__bytes[(self.__width * y) + x] = value
		
	def crop(self, upper_left, lower_right):
		""" Returns an new image from this image delimited by the given square """
		raise NotImplementedError
		
	def save(self):
		raise NotImplementedError
		
def DrawImage(image):
	raise NotImplementedError
		
if __name__ == "__main__":
	image = Image('./Imagenes/BINARIO.BMP')