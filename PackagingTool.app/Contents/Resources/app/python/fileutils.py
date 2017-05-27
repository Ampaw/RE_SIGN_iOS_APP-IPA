import os
import sys
import shutil

def copyFiles(src, dest):
	if not os.path.isabs(src):
		src = os.path.abspath(src)
	if not os.path.isabs(dest):
		dest = os.path.abspath(dest)
	if not os.path.exists(src):
		print "copyFiles Error! the src dir is not exists, src:" + src
		return 1
	if not os.path.exists(dest):
		os.makedirs(dest)
	for file in os.listdir(src):
		subSrc = os.path.join(src, file)
		subDest = os.path.join(dest, file)
		if os.path.isfile(subSrc):
			copyFile(subSrc, subDest)
		elif os.path.isdir(subSrc):
			copyFiles(subSrc, subDest)
		else:
			print "copyFiles Error! the file type is not file or dir:" + file
			return 1


# src and dest must be absolute path
def copyFile(src, dest):
	if not os.path.exists(src):
		print "copyFile Error! the src path is not exists: " + src
		return 1

	destDir = os.path.dirname(dest)
	if not os.path.exists(destDir):
		os.makedirs(destDir)
	# print "copy file from:" + src + ', to:' + dest
	shutil.copy(src, dest)
	return 0
	# with open(src, 'rb') as fsrc:
	# 	with open(dest, 'wb') as fdst:
	# 		copyfileobj(fsrc, fdst)

def copyfileobj(fsrc, fdst, length=16*1024):
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)

def onerror(oserror, err):
	# print "clearDir error: " + str(oserror) + ", " + str(err)
	pass

def clearDir(dir, root=True):
	for name in os.listdir(dir):
		fullname = os.path.join(dir, name)
		if os.path.isdir(fullname):
			clearDir(fullname, False)
		else:
			try:
				os.remove(fullname)
			except os.error, err:
				onerror(os.error, err)
	if not root:
		try:
			os.rmdir(dir)
		except os.error, err:
			onerror(os.error, err)