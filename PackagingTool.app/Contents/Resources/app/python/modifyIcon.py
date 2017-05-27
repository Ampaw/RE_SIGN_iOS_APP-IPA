import os
try:  
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance  
except ImportError:  
    import Image, ImageDraw, ImageFont, ImageEnhance

from xml.etree import ElementTree as ET

def paste(src, dest):
	if not  os.path.exists(src) or not os.path.exists(dest):
		print "no icons to modify, src: %s, dest: %s" %(src, dest)
		return 1
	srcImage = Image.open(src)
	destImage = Image.open(dest)
	# srcW, srcH = srcImage.size
	destW, destH = destImage.size
	srcImage.thumbnail((destW, destH), Image.ANTIALIAS)
	# srcImage.load()
	r,g,b,a = srcImage.split()
	# destImage.paste(srcImage, (destW - srcW, destH - srcH), mask = a)
	destImage.paste(srcImage, (0, 0), mask = a)
	destImage.save(dest)

	return 0

def thumbnail(src, dest, w, h):
	if not  os.path.exists(src):
		print "no icons to modify, src: %s" %(src)
		return 1
	srcImage = Image.open(src)
	srcW, srcH = srcImage.size
	srcImage.thumbnail((w, h), Image.ANTIALIAS)
	srcImage.save(dest)

	return 0

def modify(iconFile, destDir):
	if not os.path.exists(iconFile):
		return 0

	manifestFile = os.path.join(destDir, "AndroidManifest.xml")
	if not os.path.exists(manifestFile):
		print "Error! no manifestFile."
		return 1

	tree = ET.parse(manifestFile)
	androidNS = "http://schemas.android.com/apk/res/android"
	ET.register_namespace("android", androidNS)
	root = tree.getroot()

	applicationNode = root.find("application")
	if applicationNode is not None and len(applicationNode) > 0:
		findLaunchIcon = False
		iconKey = "{" + androidNS + "}icon"
		nameKey = "{" + androidNS + "}name"
		luanchActivity = None
		launchIconName = None
		for activityNode in applicationNode.findall("activity"):
			for intentNode in activityNode.findall("intent-filter"):
				findAction = False
				findCategory = False
				for actionNode in intentNode.findall("action"):
					if actionNode.get(nameKey) == "android.intent.action.MAIN":
						findAction = True
						break
				for categoryNode in intentNode.findall("category"):
					if categoryNode.get(nameKey) == "android.intent.category.LAUNCHER":
						findCategory = True
				if findAction and findCategory:
					luanchActivity = actionNode
					break
			if luanchActivity is not None:
				launchIconName = luanchActivity.get(iconKey)
				break
		if not launchIconName:
			launchIconName = applicationNode.get(iconKey)
		if not launchIconName:
			launchIconName = "@drawable/ic_launcher"
		if not launchIconName.startswith("@drawable/"):
			print "Error! wrong launch icon name"
			return 1
		launchIconName = launchIconName[10:] + ".png"
		destPath = os.path.join(destDir, "res")
		if not os.path.exists(destPath):
			return 0
		for drawablePath in os.listdir(destPath):
			if drawablePath.startswith("drawable"):
				destIconPath = os.path.join(destPath, drawablePath + "/" + launchIconName)
				if os.path.exists(destIconPath):
					paste(iconFile, destIconPath)
	else:
		print "Error! no application node"
		return 1

	return 0