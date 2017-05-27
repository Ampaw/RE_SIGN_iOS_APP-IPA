#coding:utf-8
import os
import sys
from PIL import Image
import commands

# 图片名称 24组图片
names = [
'AppIcon83.5x83.5@2x~ipad.png',
'AppIcon76x76~ipad.png',
'AppIcon76x76@2x~ipad.png',
'AppIcon72x72~ipad.png',
'AppIcon72x72@2x~ipad.png',
'AppIcon60x60@3x.png',
'AppIcon60x60@2x.png',
'AppIcon57x57.png',
'AppIcon50x50~ipad.png',
'AppIcon50x50@2x~ipad.png',
'AppIcon40x40~ipad.png',
'AppIcon40x40@3x.png',
'AppIcon40x40@2x~ipad.png',
'AppIcon40x40@2x.png',
'AppIcon29x29~ipad.png',
'AppIcon29x29@3x.png',
'AppIcon29x29@2x~ipad.png',
'AppIcon29x29@2x.png',
'AppIcon29x29.png',
'AppIcon20x20~ipad.png',
'AppIcon20x20@3x.png',
'AppIcon20x20@2x~ipad.png',
'AppIcon20x20@2x.png']

# 每张图片对应的大小，宽高一样
values = ['167','76','152','72','144','180','120','57','50','100','40','120','80','80','29','87','58','58','29','20','60','40','40']

	
_iconnames = []
_iconsizes = []
_images = {}
		
def init(iconnames,iconsizes):
	_iconnames = iconnames
	_iconsizes = iconsizes
	for index,name in enumerate(_iconnames):
		_images[name] = _iconsizes[index]

def get_image_size(icon):
	im = Image.open(icon)
	return im.size[0]

def get_available_images(path):
	images = []
	for file_name in os.listdir(path):
		if file_name.endswith(".png"):
			size = get_image_size(file_name)
			if  size >= 180:
				images.append(file_name)
	return images

def resize_image(imagename,size,new_path):
	im = Image.open(imagename)
	if isinstance(size,str):
		size = int(size)
	new_size = (size,size)
	out = im.resize(new_size)
	out.save(new_path)

	
def run(path):
	dirpath =os.path.split(path)[0]
	iconpath =os.path.join(dirpath,'icon')
	if os.path.exists(iconpath):
		for icons in os.listdir(iconpath):
			cmd ='rm -rf '+os.path.join(iconpath,icons)
			(status,output)=commands.getstatusoutput(cmd)
			print output
			if status:
				return status
	else:
		os.mkdir(iconpath)

	for new_path,size in _images.items():
		new_path = os.path.join(iconpath,new_path)
		resize_image(path,size,new_path)


if __name__ == "__main__":
	imagepath = sys.argv[1]
	init(names,values)
	run(imagepath)


