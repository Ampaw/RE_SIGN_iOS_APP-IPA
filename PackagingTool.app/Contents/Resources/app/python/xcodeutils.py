#coding:utf-8
import os
import json
import fileutils
import biplist
import modifyIcon as MI

from pbxproj import *
from pbxproj.pbxextensions import *


forXcodeConfigMap = {}
def loadForXcodeConfigFile(sdk, path):
	if not os.path.exists(path):
		return 1
	with open(path) as fsrc:
		forXcodeConfigMap[sdk] = json.load(fsrc)
	return 0

def getForXcodeConfigFile(sdk):
	if forXcodeConfigMap.has_key(sdk):
		return forXcodeConfigMap[sdk]
	else:
		return None

# get info.plist path , the path is relative the **.xcodeproj file
def getInfoPlistPath(XcodeProject):
	phases = XcodeProject.get_build_phases_by_name('XCBuildConfiguration')
	base = 'buildSettings'
	key = "INFOPLIST_FILE"
	for build_phase in phases:
		if base in build_phase and key in build_phase[base]:
			return build_phase[base][key]
	return None


def getProductName(XcodeProject):
	phases = XcodeProject.get_build_phases_by_name('XCBuildConfiguration')
	base = 'buildSettings'
	key = "PRODUCT_NAME"
	for build_phase in phases:
		if base in build_phase and key in build_phase[base]:
			return build_phase[base][key]
	return None

# get the file path by name , the path is relative the **.xcodeproj file
def getFilePathForProj(fileName, XcodeProject):
	files = XcodeProject.get_files_by_name(fileName)
	for file in files:
		if file["path"]:
			return file["path"]
	return None


def copySdkFilesToProj(sdk, srcDir, destDir, XcodeProject,buildPath,config=None):
	print "[ %s ] copy sdk files to project start" % sdk
	srcDir = os.path.abspath(srcDir)	# this meanings the src sdk location
	destDir = os.path.abspath(destDir)	# this meanings the **.xcodeproj files dir location

	for fileName in os.listdir(srcDir):
		filePath = os.path.join(srcDir, fileName)

		if fileName == "aonesdk.json":

			destAonesdkPath = getFilePathForProj(fileName, XcodeProject)
			srcAonesdkPath = filePath

			if destAonesdkPath:
				destAonesdkPath = os.path.join(destDir, destAonesdkPath)
				modifyAonesdkJson(srcAonesdkPath, destAonesdkPath)
			else:
				print "[ %s ] Error! aonesdk.json not found!" % sdk
				return 1

		elif fileName.endswith(".framework"):

			#  add 3d framework
			file_options = FileOptions(weak=False, embed_framework=False, code_sign_on_copy=False)  #weak=False means the Status is Required
			XcodeProject.add_file(filePath,tree='SOURCE_ROOT', file_options=file_options, force=False)
			#  add 3d framework search path
			XcodeProject.add_framework_search_paths(srcDir)

		elif fileName.endswith(".a"):

			# add 3d library
			file_options = FileOptions(weak=True, embed_framework=False, code_sign_on_copy=False)	#library's Status is always Required
			XcodeProject.add_file(filePath,tree='SOURCE_ROOT', file_options=file_options, force=False)
			# add 3d library search path
			XcodeProject.add_library_search_paths(srcDir)

		elif fileName.endswith(".plist") or fileName.endswith(".bundle"):

			XcodeProject.add_file(filePath)

		elif fileName == "uuSdkConfig.json":

			destUuSdkConfigPath = getFilePathForProj(fileName, XcodeProject)
			destUuSdkConfigPath = os.path.join(destDir, destUuSdkConfigPath)
			srcUuSdkConfigPath = filePath

			if destUuSdkConfigPath:
				# purpose for particular plugin to modify the init params
				modifySrcUuSdkConfigJson(srcUuSdkConfigPath,config)

				modifyUuSdkConfigJson(srcUuSdkConfigPath, destUuSdkConfigPath)
			else:
				print "[ %s ] Error! uuSdkConfig.json not found!" % sdk
				return 1

		elif fileName == "ForXcode.json":

			configData = getForXcodeConfigFile(sdk)
			if configData:
				modifyProjSettings(configData, XcodeProject)


	print "[ %s ] copy sdk files to project finish" % sdk
	return 0


# set the project's Build Settings
def modifyProjSettings(srcData, XcodeProject):

	if srcData.has_key("archs"): 	# no need to add archs
		pass

	if srcData.has_key("linkFlags"):	# add other link flags
		XcodeProject.add_other_ldflags(srcData["linkFlags"])

	if srcData.has_key("frameworks"):	## add system frameworks
		for framework in srcData["frameworks"]:
			framework = 'System/Library/Frameworks/' + framework
			file_options = FileOptions(weak=False, embed_framework=False, code_sign_on_copy=False)
			parent = XcodeProject.get_or_create_group("Frameworks")
			XcodeProject.add_file(framework,tree='SDKROOT',file_options=file_options,force=False)

	if srcData.has_key("libs"): 	## add system library
		for lib in srcData["libs"]:
			lib = 'usr/lib/' + lib
			file_options = FileOptions(weak=True, embed_framework=False, code_sign_on_copy=False)
			parent = XcodeProject.get_or_create_group("Frameworks")
			XcodeProject.add_file(lib,tree='SDKROOT',file_options=file_options,force=False)


#  modify aoensdk.json , intend to replace the `channel`
def modifyAonesdkJson(src, dest):
	if not os.path.exists(src):
		return 0
	if not os.path.exists(dest):
		fileutils.copyFile(src, dest)
		return 0
	with open(src) as fsrc:
		srcData = json.load(fsrc)

	changeFile = False
	if srcData.has_key("channel"):
		changeFile = True
	if changeFile:
		with open(dest) as fdest:
			destData = json.load(fdest)
		destData["channel"] = srcData["channel"]
	destData = json.dumps(destData,ensure_ascii=False)
	with open(dest, "w") as fdest:
		fdest.write(destData)

	return 0


#  modify the uusdkconfig.json for particular Plugin
def modifySrcUuSdkConfigJson(dest,config):
	if not os.path.exists(dest):
		print "[modifySrcUuSdkConfigJson] uusdkconfig.json not exist:%s"%(dest)
		return

	sdkName = "AnalyticsAppsFlyer"
	init_param_key = "AppStore_AppleId"
	init_param_value = config.getAppleId()
	modifyUusdkJsonInitParam(dest,sdkName,init_param_key,init_param_value)

	sdkName = "AnalyticsReYunTrack"
	init_param_key = "reyun_appid"
	init_param_value = config.getReyunAppId()
	modifyUusdkJsonInitParam(dest,sdkName,init_param_key,init_param_value)

	sdkName = "AnalyticsTalkingdata"
	dic = {"td_appid":config.getTDAppId(),"td_channel":config.getTDChannel()}
	for key in dic:
		init_param_key = key
		init_param_value = dic[init_param_key]
		modifyUusdkJsonInitParam(dest,sdkName,init_param_key,init_param_value)

# modify the init param for uuSdkConfig.json
def modifyUusdkJsonInitParam(src,sdkName,key,value):
	"""
	 modify the init params
	 `src` the uusdkconfig.json in the sdk/xxx/uusdkConfig.json
	 `sdkName` the sdk which you want to midify
	 `key` key in the init_params
	 `value` value for the key
	"""
	result = False
	if not os.path.exists(src):
		return result

	with open(src) as fsrc:
		srcData = json.load(fsrc)

	if srcData.has_key("sdks"):
		srcSdks = srcData["sdks"]
		for sdk in srcSdks:
			if sdk["name"] == sdkName and sdk.has_key("init_params") and sdk["init_params"].has_key(key):
				sdk["init_params"][key] = value
				result = True

	srcData["sdks"] = srcSdks
	srcData = json.dumps(srcData,ensure_ascii=False)
	with open(src, "w") as fdest:
		fdest.write(srcData)
				
	return result


# add the src channel sdk's content in the uuSdkConfig.json into the Xcode Project's uuSdkConfig.json
def modifyUuSdkConfigJson(src, dest):
	if not os.path.exists(dest):
		fileutils.copyFile(src, dest)
		return
	with open(src) as fsrc:
		srcData = json.load(fsrc)
	with open(dest) as fdest:
		destData = json.load(fdest)

	# set default sdk
	defalutSdkNames = ["defaultUserSdk", "defaultIapSdk", "defaultAnalyticsSdk", "defaultShareSdk", "defaultAdsSdk", "defaultPushSdk"]
	for sdkName in defalutSdkNames:
		if srcData.has_key(sdkName):
			destData[sdkName] = srcData[sdkName]
	
	# add sdk config to uuSdkConfig.json
	destSdks = []
	if destData.has_key("sdks"):
		destSdks = destData["sdks"]
	destSdkMap = {}
	for sdk in destSdks:
		if sdk.has_key("name"):
			destSdkMap[sdk["name"]] = sdk

	if srcData.has_key("sdks"):
		srcSdks = srcData["sdks"]
		for sdk in srcSdks:
			if sdk.has_key("name"):
				sdkName = sdk["name"]
				if destSdkMap.has_key(sdkName):
					destSdks.remove(destSdkMap[sdkName])
				destSdks.append(sdk)
				destSdkMap[sdkName] = sdk
	destData["sdks"] = destSdks
	destData = json.dumps(destData,ensure_ascii=False)
	with open(dest, "w") as fdest:
		fdest.write(destData)


# Intend set the `displayName` , `buildNumber` , `versionNumber`, `BundleID`
def modifyGeneralSetting(sdk,XcodeProjectDir,XcodeProject,config):
	print "\n---[General Settings]-----\n"
	if not config:
		return 1

	infoPlist = getInfoPlistPath(XcodeProject)
	if not infoPlist:
		print "[ %s ] Error! doesnt find info.plist" % sdk
		return 1

	infoPlist = os.path.join(XcodeProjectDir, infoPlist)
	if not os.path.exists(infoPlist):
		print "Error! info.plist doesn't exist, path = %s\n" % infoPlist
		return 1

	plist = biplist.readPlist(infoPlist)

	#  游戏名称
	displayName = config.getDisplayName()
	if len(displayName) > 0:
		print "set the displayName = %s\n" % displayName
		plist["CFBundleDisplayName"] = displayName

	# 发布版本号
	version = config.getVersionNumber()
	if len(version) > 0:
		print "set the version number = %s\n" % version
		plist["CFBundleShortVersionString"] = version

	# 内部版本号
	build = config.getBuildNumber()
	if len(build) > 0:
		print "set the build number = %s\n" % build
		plist["CFBundleVersion"] = build 

	# 游戏包名
	bundleIdentifier = config.getIdentifier()
	if len(bundleIdentifier) > 0:
		print "set the bundleID = %s\n" % bundleIdentifier
		XcodeProject.set_flags("PRODUCT_BUNDLE_IDENTIFIER",bundleIdentifier)

	biplist.writePlist(plist, infoPlist, False)
	return 0


def modifyPackageSettings(sdk,XcodeProject,config):
	print "\n---[Package Settings]-----\n"
	developmentTeam = config.getDevelopmentTeam()
	#  set developemnt team
	if not developmentTeam:
		print "Error, please Set development team in config.json"
		return 1
	print "set Development Team = %s\n" % developmentTeam
	XcodeProject.set_flags("DEVELOPMENT_TEAM", developmentTeam)

	# set code sign identity , separate 'Release' from 'Debug'
	codeSignDev = config.getSignId_dev()
	codeSignDis = config.getSignId()
	if not codeSignDev and not codeSignDis:
		print "Error, please Set code sign in config.json"
		return 1
	print "set dis code sign = %s\n" % codeSignDis
	print "set dev code sign = %s\n" % codeSignDev
	XcodeProject.set_flag("CODE_SIGN_IDENTITY", codeSignDis, Release=True)
	XcodeProject.set_flag("CODE_SIGN_IDENTITY", codeSignDev, Release=False)

	# set provisioning profile specifier name , separate 'Release' from 'Debug'
	profileSpecifierDev = config.getProfileSpcifier_dev()
	profileSpecifierDis = config.getProfileSpecifier()
	if not profileSpecifierDev and not profileSpecifierDis:
		print "Error, please set profile specifier in config.json"
		return 1
	print "set dis profile specifier = %s\n" % profileSpecifierDis
	print "set dev profile specifier = %s\n" % profileSpecifierDev
	XcodeProject.set_flag("PROVISIONING_PROFILE_SPECIFIER", profileSpecifierDis, Release=True)
	XcodeProject.set_flag("PROVISIONING_PROFILE_SPECIFIER", profileSpecifierDev, Release=False)




# Intend to modify bundle ID and add add the URL Types for particular sdk
def modifyInfoPlist(sdk, srcDir, destDir, XcodeProject):
	configData = getForXcodeConfigFile(sdk)
	if not configData:
		return 1

	if configData.has_key("bundleId") or configData.has_key("infoSetting"):
		infoPlist = getInfoPlistPath(XcodeProject)
		if not infoPlist:
			print "[ %s ] Error! doesnt find info.plist" % sdk
			return 1

		infoPlist = os.path.join(destDir, infoPlist)
		if not os.path.exists(infoPlist):
			print ("[%s] Error! info.plist file not exist , path = %s\n"%(sdk,infoPlist))
			return 1

		plist = biplist.readPlist(infoPlist)

		if configData.has_key("bundleId"):
			newBundleId = configData["bundleId"]
			ret = modifyBundleId(sdk, newBundleId, plist,XcodeProject)
			if ret:
				return 1

		if configData.has_key("infoSetting"):
			infoSettings = configData["infoSetting"]
			ret = addSettingsToInfoPlist(sdk, infoSettings, plist)
			if ret:
				return 1

		biplist.writePlist(plist, infoPlist, False)

	return 0

def modifyBundleId(sdk, newBundleId, plist,XcodeProject):
	print "[ %s ] modify bundle id start" % sdk

	if not plist.has_key("CFBundleIdentifier"):
		print "[ %s ] Error! no CFBundleIdentifier in info.plist" % sdk
		return 1
	oldBundleId = plist["CFBundleIdentifier"]
	if newBundleId.startswith("."):
		newBundleId = oldBundleId + newBundleId
	elif newBundleId.endswith("."):
		if newBundleId.startswith("com") and oldBundleId.startswith("com"):
			newBundleId = newBundleId + oldBundleId[3:-1]
		else:
			newBundleId = newBundleId + oldBundleId
	print "new bundle id: " + newBundleId
	plist["CFBundleIdentifier"] = newBundleId

	print "[ %s ] modify bundle id finish" % sdk
	return 0

def addSettingsToInfoPlist(sdk, infoSettings, plist):
	for key, value in infoSettings.items():
		if key == "CFBundleURLTypes":
			bundleId = plist["CFBundleIdentifier"]
			for cfBundleURL in value:
				if cfBundleURL.has_key("CFBundleURLName"):
					name = cfBundleURL["CFBundleURLName"]
					if name.find("bundleId") != -1:
						cfBundleURL["CFBundleURLName"] = name.replace("bundleId", bundleId)
				if cfBundleURL.has_key("CFBundleURLSchemes"):
					schemes = cfBundleURL["CFBundleURLSchemes"]
					for i in range(len(schemes)):
						if schemes[i].find("bundleId") != -1:
							schemes[i] = schemes[i].replace("bundleId", bundleId)

				if not plist.has_key("CFBundleURLTypes"):
					plist["CFBundleURLTypes"] = []
				plist["CFBundleURLTypes"].append(cfBundleURL)
		else:
			plist[key] = value
	return 0



# modify Icon and Logo.png 
def modifyIconAndLogo(sdk,project,xcodeProjDir,config):

	srcLogoPath = os.path.join(xcodeProjDir,"../../../",config.getIconPath(),"logo/logo.png")
	srcIconDir = os.path.join(xcodeProjDir,"../../../",config.getIconPath(),"icon")
	destIconDir = getFilePathForProj("Images.xcassets",project)
	AppIconName = project.get_flag_value("ASSETCATALOG_COMPILER_APPICON_NAME")[0] + ".appiconset"
	destIconDir = os.path.join(xcodeProjDir,destIconDir,AppIconName)

	project.add_file(srcLogoPath,force=True)
	# if os.path.exists(srcLogoPath):
	# 	project.add_file(srcLogoPath,force=True)
	# else:
	# 	print ("src Logo Path not exist, path = %s\n" % srcLogoPath)

	if os.path.exists(srcIconDir) and os.path.exists(destIconDir):
		fileutils.copyFiles(srcIconDir,destIconDir)
	else:
		print ("src Icon Dir not exist , path = %s\n" % srcIconDir)
		print ("dest Icon Dir not exist , path = %s\n" % destIconDir)


# modify Icon if necessary, the name must be the icon.png
def modifyIcon(sdk, srcDir, destDir, XcodeProject):
	iconFile = os.path.join(srcDir, "icon/icon.png")
	if not os.path.exists(iconFile):
		return 0
	print "[ %s ] modify icon start" % sdk
	# ret = MI.modify(iconFile, destDir)
	imageXcassets = getFilePathForProj("Images.xcassets", XcodeProject)
	if imageXcassets is None:
		imageXcassets = "demo/Images.xcassets"
	if not imageXcassets:
		print "[ %s ] Error! Images.xcassets not found!" % sdk
		return 1
	imageXcassets = os.path.join(destDir, imageXcassets)
	print imageXcassets
	imageContents = os.path.join(imageXcassets, "AppIcon.appiconset/Contents.json")
	if not os.path.exists(imageContents):
		print "[ %s ] Error! the file Images.xcassets/AppIcon.appiconset/Contents.json not found!" % sdk
		return 1
	with open(imageContents) as fsrc:
		contentsData = json.load(fsrc)
		if contentsData.has_key("images"):
			for imageData in contentsData["images"]:
				if imageData.has_key("filename"):
					imagePath = imageData["filename"]
					imagePath = os.path.join(imageXcassets, "AppIcon.appiconset/" + imagePath)
					if not os.path.exists(imagePath):
						print "[ %s ] Warning! the image is not exists: %s" % (sdk, imagePath)
					else:
						ret = MI.paste(iconFile, imagePath)
						if ret:
							return ret

	print "[ %s ] modify icon finish" % sdk
	return 0


# modify the splash if necessary
def modifySplash(sdk, srcDir, destDir, XcodeProject, orientation):
	print "[ %s ] modify splash start" % sdk
	if orientation == "landscape":
		srcSpalshPath = os.path.join(srcDir, "splash/landscape")
	else:
		srcSpalshPath = os.path.join(srcDir, "splash/protrait")
	print srcSpalshPath
	if os.path.exists(srcSpalshPath):
		modified = False
		for imageName in os.listdir(srcSpalshPath):
			imagePath = os.path.join(srcSpalshPath, imageName)
			destPath = getFilePathForProj(imageName, XcodeProject)
			if destPath:
				destPath = os.path.join(destDir, destPath)
				ret = fileutils.copyFile(imagePath, destPath)
				if ret:
					print "[ %s ] Error! no src file: %s" % (sdk, imagePath)
					return 1
			else:
				print "add image:", imagePath
				XcodeProject.add_file(imagePath)
		ret = delProjectBuildConfig(XcodeProject, "ASSETCATALOG_COMPILER_LAUNCHIMAGE_NAME")
		if ret:
			return 1
		ret = delInfoPlistKey(sdk, destDir, XcodeProject, "UILaunchStoryboardName")
		if ret:
			return 1

	print "[ %s ] modify splash finish" % sdk
	return 0

def delProjectBuildConfig(XcodeProject, key):
	phases = XcodeProject.get_build_phases_by_name('XCBuildConfiguration')
	base = 'buildSettings'
	for build_phase in phases:
		if base in build_phase and key in build_phase[base]:
			build_phase[base][key] = ''
	return 0

def delInfoPlistKey(sdk, destDir, XcodeProject, key):
	infoPlist = getInfoPlistPath(XcodeProject)
	if not infoPlist:
		print "[ %s ] Error! doesnt find info.plist" % sdk
		return 1
	infoPlist = os.path.join(destDir, infoPlist)
	plist = biplist.readPlist(infoPlist)
	modified = False
	for pKey in plist.keys():
		if pKey == key:
			plist.pop(pKey)
			modified = True
	if modified:
		biplist.writePlist(plist, infoPlist, False)
	return 0
