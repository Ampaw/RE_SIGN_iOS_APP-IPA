
#coding:utf-8

from config import Configer
import fileutils
import os
import sys
import copy
from pbxproj import XcodeProject
import xcodeutils
import biplist
import utils
import subpackage


def runSpecial(sdk, srcDir, destDir, sdkConfigFile, XcodeProject):
	print "[runSpecial] sdk is [%s]" % sdk
	print "[srcDir] is = ", srcDir
	print "[destDir] is = ", destDir
	print "[sdkConfigFile] is = ", sdkConfigFile

	phases = XcodeProject.get_build_phases_by_name('XCBuildConfiguration')
	base = 'buildSettings'
	key = "INFOPLIST_FILE"
	for build_phase in phases:
		if base in build_phase and key in build_phase[base]:
			infoPlist = build_phase[base][key]
	if infoPlist is not None:
		infoPlist = os.path.join(destDir, infoPlist)
		plist = biplist.readPlist(infoPlist)
	specialScript = os.path.join(srcDir, "special.py")
	if os.path.exists(specialScript):
		sysPath = copy.deepcopy(sys.path)
		sys.path.append(os.path.abspath(srcDir))
		import special
		ret = special.run(sdk, sdkConfigFile, os.path.abspath(destDir), plist, XcodeProject)

		if ret:
			print "[ %s ] Error! run special script" % sdk
			return 1
		del sys.modules["special"]
		if infoPlist is not None:
			biplist.writePlist(plist, infoPlist, False)
		sys.path = sysPath
	return 0

def addSdksToChannel(sdkName, destPath, config, project,buildPath):
	if sdkName == "base":
		sdks = config.getBaseSdkList()
		if len(sdks) == 0:
			return 0
	else:
		sdks = config.getChannelSdkList()
		print "[sdks] is = ", sdks
		if len(sdks) == 0:
			return 0
	for sdk in sdks:
		if len(sdk) == 0:
			continue
		srcSdkDir = config.getSdkDir(sdk)
		srcSdkConfigDir = config.getSdkConfigDir(sdk)
		sdkConfigFile = os.path.join(srcSdkConfigDir, "config.json")
		if os.path.exists(sdkConfigFile):
			sdkConfig = copy.deepcopy(config)
			sdkConfig.loadConfig(sdkConfigFile, None)
		else:
			sdkConfig = config

		# 复制渠道SDK到打包项目下的SDK目录
		fileutils.copyFiles(srcSdkDir,srcSdkConfigDir)

		# load ForXcode.json
		ret = xcodeutils.loadForXcodeConfigFile(sdk, os.path.join(srcSdkConfigDir, "ForXcode.json"))
		if ret:
			print "[ %s ] Error! no file ForXcode.json!" % sdk
			return 1

		# copy res files
		ret = xcodeutils.copySdkFilesToProj(sdk, srcSdkConfigDir, destPath, project,buildPath , config)
		if ret:
			print "[ %s ] Error! copy sdk files to xcode project" % sdk
			return 1
		
		# modify info.plist with ForXcode.json
		ret = xcodeutils.modifyInfoPlist(sdk, srcSdkConfigDir, destPath, project)
		if ret:
			print "[ %s ] Error! modify info.plist files to xcode project" % sdk
			return 1

		# run special script
		ret = runSpecial(sdk, srcSdkConfigDir, destPath, sdkConfigFile, project)
		if ret:
			return 1
	return 0

def Build(runPath, toolPath,buildType,configName=None):
	configFile = os.path.join(runPath, "config/config.json")
	if configName:
		configFile = os.path.join(runPath,"config",configName)

	if not os.path.exists(configFile):
		print "Error! no config file, path: %s" % configFile
		return
	config = Configer()
	# load the config.json
	config.loadConfig(configFile, toolPath)

	# new project path
	oldProjPath = config.getProjPath()
	if not os.path.exists(oldProjPath):
		print "Error! no project path, please set in config.json"
		return
	oldProjPath = os.path.abspath(oldProjPath)
	oldProjDirName = os.path.basename(oldProjPath)
	print "[oldProjDirName:]", oldProjDirName
	buildPath = os.path.abspath(oldProjPath + "./../")
	print "[buildPath:]", buildPath
	baseProjDirName = oldProjDirName
	

	packageName = ""
	destDir = ""

	# copy to new channel_sdk dir
	channelSdks = config.getChannels()
	print ("channelSdks = %s\n"%channelSdks)
	for sdk in channelSdks:
		destPath = os.path.join(buildPath, baseProjDirName + "_" + sdk)
		if os.path.exists(destPath):
			fileutils.clearDir(destPath)
		# copy Xcode Project
		fileutils.copyFiles(oldProjPath, destPath)

		index = sdk.find("_")
		if index != -1:
			parentSdk = sdk[0:index]
			print "parentSdk:" + parentSdk
		else:
			parentSdk = sdk
		
		# srcSdkDir is usually in: aonesdk/export/ios/sdks/sdkName
		srcSdkDir = config.getSdkDir(parentSdk)

		# srcSdkConfigDir is usually in:`autopack_lzws/ios/sdks/sdkName` for example
		srcSdkConfigDir = config.getSdkConfigDir(sdk)
		sdkConfigFile = os.path.join(srcSdkConfigDir, "config.json")

		# copy src sdk to the auto project
		print  "-----[begin copy src sdk to the autopackage project]-----\n"
		print ("srcSdkDir=%s\n" % srcSdkDir)
		fileutils.copyFiles(srcSdkDir,srcSdkConfigDir)
		print ("srcSdkConfigDir=%s\n" % srcSdkConfigDir)


		if os.path.exists(sdkConfigFile):
			sdkConfig = copy.deepcopy(config)
			sdkConfig.loadConfig(sdkConfigFile, None)
		else:
			sdkConfig = config

		# load ForXcode.json
		ret = xcodeutils.loadForXcodeConfigFile(sdk, os.path.join(srcSdkConfigDir, "ForXcode.json"))
		if ret:
			print "[ %s ] Error! no file ForXcode.json!" % sdk
			return

		# copy resource files to Xcode Project
		xcodeProjPath = os.path.join(destPath, config.getXcodeProjPath()) 
		print "[xcode proj path is ] = %s\n" % xcodeProjPath
		xcodeProjDir = os.path.dirname(xcodeProjPath)

		#  load Xcode Project
		project = XcodeProject.load(os.path.join(xcodeProjPath, "project.pbxproj"))

		if project == None:
			print "load xcode project fail"
			return
		
		print "-----[begin copy SdkFiles to proj]-----\n"
		ret = xcodeutils.copySdkFilesToProj(sdk, srcSdkConfigDir, xcodeProjDir, project,buildPath, config)

		if ret:
			print "[ %s ] Error! copy sdk files to xcode project" % sdk
			return
		
		# modify info.plist according to ForXcode.json
		print "-----[begin modify info.plist]-----\n"
		ret = xcodeutils.modifyInfoPlist(sdk, srcSdkConfigDir, xcodeProjDir, project)
		if ret:
			print "[ %s ] Error! modify info.plist files to xcode project" % sdk
			return

		#copy icon and logo 
		print "-----[begin copy icon and logo]-----\n"
		xcodeutils.modifyIconAndLogo(sdk,project,xcodeProjDir,config)
		

		# modify icon
		print "-----[begin modify icon]-----\n"
		ret = xcodeutils.modifyIcon(sdk, srcSdkConfigDir, xcodeProjDir, project)
		if ret:
			print "[ %s ] Error! modify icon" % sdk
			return

		# modify splash
		print "-----[begin modify splash]-----\n"
		if sdkConfig.getHasSplash() == "True":
			xcodeutils.modifySplash(sdk, srcSdkConfigDir, xcodeProjDir, project, sdkConfig.getAppOrientation())

		# run special script
		print "-----[begin run special]-----\n"
		ret = runSpecial(sdk, srcSdkConfigDir, xcodeProjDir, sdkConfigFile, project)
		if ret:
			return

		# add sdks to channel
		print "-----[add sdks to channel]-----\n"
		ret = addSdksToChannel(parentSdk, xcodeProjDir, config, project,buildPath)
		if ret:
			return

		# modify general settings, like displayName ,versionNumber, buildNumber,BundleID ...
		xcodeutils.modifyGeneralSetting(sdk, xcodeProjDir, project, config)

		# modity package settings, like developemntTeam , codeSign, profileSpecifier ....
		xcodeutils.modifyPackageSettings(sdk,project,config)
	
		# save the Xcode project
		project.save()


		# build
		print "-----[begin build xcodeproject]-----\n"
		os.chdir(xcodeProjDir) #change the workspace
		buildConfig = config.getBuildConfig()

		productName = xcodeutils.getProductName(project)
		print "[xcode prodcut name ] = %s\n" % productName

		if buildType == "Dev":
			signId = config.getSignId_dev()
			profileSpecifier = config.getProfileSpcifier_dev()
		else :
			signId = config.getSignId()
			profileSpecifier = config.getProfileSpecifier()

		command = 'xcodebuild -sdk iphoneos -configuration ' + buildConfig + ' CODE_SIGN_IDENTITY="' + signId + '"'+ ' PROVISIONING_PROFILE_SPECIFIER="' + profileSpecifier + '"'


		# command = 'xcodebuild -sdk iphoneos -configuration ' + buildConfig + ' CODE_SIGN_IDENTITY="' + signId + '"' + ' PROVISIONING_PROFILE="' + provisionFile + '"' + ' PROVISIONING_PROFILE_SPECIFIER="' + privisioningProfileSpecifier + '"'

		ret = utils.execCommand(command)
		if ret:
			return ret

		'''
		appPath = subpackage.getAppPath('/Users/lastYear/Desktop/autopack_lzws/ios/build')

		subpackage.modifyConfig('td_appid','1234455',appPath)

		subpackage.modifyConfig('td_channel','1234455',appPath)

		name ='吕布无双斩'
		subpackage.modifyPlist('CFBundleDisplayName',name,appPath)

		iconpath = '/Users/lastYear/Desktop/icon/logo/lbwsz'
		subpackage.modifyIcon(iconpath,appPath)

		subpackage.modifyIcon('/Users/lastYear/Desktop/icon/lbwsz',appPath)
		print 'TEST END\n'
		command = 'xcrun -sdk iphoneos PackageApplication -v ' +appPath +' -o '+'/Users/lastYear/Desktop/autopack_lzws/ios/build/temp/sub.ipa'
		ret = utils.execCommand(command)
		if ret:
			return ret

		'''
		appName = config.getDisplayName()
		
		command = 'xcrun -sdk iphoneos PackageApplication -v "' + xcodeProjDir +  '/build/' + buildConfig + '-iphoneos/' \
			+ productName + '.app" -o "' + destPath + '/' + appName + "_" +buildType + '.ipa"'
		ret = utils.execCommand(command)
		if ret:
			return ret
		

if __name__ == "__main__":
	print "-----auto pack start !!!-------\n"
	
	if len(sys.argv) < 4:
		print "request at lest 4 argv"
	else:
		runPath = sys.argv[1]
		toolPath = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "./../.."))
		buildType = sys.argv[2]
		configName = sys.argv[3]
		print "[runPath]=",runPath
		print "[toolPath]=",toolPath
		print "[buildType]=",buildType
		print "[configName]=",configName
		Build(runPath,toolPath,buildType,configName)

	print "-----auto pack finish !!!-------\n"
