 
from config import Configer
import fileutils
import apkutils
import utils
import os
import sys
# import shutil
import copy


# modify contents.xcworkspacedata
contentsFile = newProj + '/project.xcworkspace/contents.xcworkspacedata'
fileRefList = rootNode.getElementsByTagName('FileRef')
        for fileRefNode in fileRefList:
            fileRefNode.setAttribute('location', fileRefNode.getAttribute('location').replace(originProjName, newProjName))
# modify info.plist
originPlist = project.get_infoplistfile()
newPlist = workDir + '/Info.plist'
file_operate.copyFile(originPlist, newPlist)
removeFileOrReference(project, os.path.basename(originPlist))
addFile(project, newPlist)
project.set_infoplistfile(newPlist)

# modify Images.xcassets, AppIcon.appiconset
    newXcassets = workDir + '/Images.xcassets'
    file_operate.copyFiles(originXcassets, newXcassets)
    if not os.path.exists(newXcassets + '/AppIcon.appiconset'):
        file_operate.copyFiles(file_operate.getFullPath('../config/Images.xcassets/AppIcon.appiconset'), newXcassets + '/AppIcon.appiconset')
    project.remove_file_by_name('Images.xcassets')
    addFile(project, newXcassets)

# splash

# modify cfbundlename, cfbundleidentifier

# add framework, lib
addSystemFrameworks(project, 'MobileCoreServices.framework', True)
addUsrLib(project, 'libz.dylib', True)

# add files: aonesdk.json, uuSdkConfig.json

 if os.path.exists(SDKSrcDir + '/Codes'):
                        file_operate.copyFiles(SDKSrcDir + '/Codes', SDKDestDir + '/Codes')
                        addFolder(project, SDKDestDir + '/Codes')
                    scriptPath = SDKSrcDir + '/script.pyc'
                    if os.path.exists(scriptPath):
                        sys.path.append(SDKSrcDir)
                        import script
                        script.script(SDK, workDir, target_name, usrSDKConfig, SDKDestDir, project)
                        del sys.modules['script']
                        sys.path.remove(SDKSrcDir)
                    if os.path.exists(SDKSrcDir + '/Frameworks'):
                        addFolder(project, SDKSrcDir + '/Frameworks')
                    if os.path.exists(SDKSrcDir + '/Resources'):
                        addFolder(project, SDKSrcDir + '/Resources')
                    if os.path.exists(SDKSrcDir + '/References'):
                        for dir in os.listdir(SDKSrcDir + '/References'):
                            if os.path.isdir(SDKSrcDir + '/References/' + dir):
                                addFile(project, SDKSrcDir + '/References/' + dir)

                    xmlFile = SDKSrcDir + '/config.xml'
                    doc = minidom.parse(xmlFile)
                    rootNode = doc.documentElement
                    sysFrameworksList = rootNode.getElementsByTagName('sysFrameworks')
                    for sysFrameworksNode in sysFrameworksList:
                        name = sysFrameworksNode.getAttribute('name')
                        required = False
                        if sysFrameworksNode.getAttribute('required') == '0':
                            required = True
                        if sysFrameworksNode.getAttribute('path') == 'xcodeFrameworks':
                            addSystemFrameworks(project, name, required)
                        elif sysFrameworksNode.getAttribute('path') == 'xcodeUsrlib':
                            addUsrLib(project, name, required)
                        else:
                            path = sysFrameworksNode.getAttribute('path') + sysFrameworksNode.getAttribute('name')
                            addFile(project, path)

                    for child in SDK['operateLs']:
                        if child['name'] == 'RemoveValidArchs_arm64':
                            project.modify_validarchs()
                            if project.modified:
                                project.save()
                        if child['name'] == 'AddOtherLinkerFlags':
                            flags = child['param']
                            addLdflags(project, flags)
                        if child['name'] == 'AddUrlSchemes':
                            if child['param'] == '':
                                urlSchemes = child['front'] + child['back']
                                urlName = child['urlname']
                                addUrlSchemes(newPlist, urlSchemes, urlName)
                            else:
                                for param in usrSDKConfig['param']:
                                    if param['name'] == child['param']:
                                        urlSchemes = child['front'] + param['value'] + child['back']
                                        urlName = child['urlname']
                                        addUrlSchemes(newPlist, urlSchemes, urlName)

# build
if mode == 0:
    cmd = 'xcodebuild ' + useSDK + ' -arch i386 >xcodebuild.txt'
else:
    cmd = 'xcodebuild ' + useSDK + ' >xcodebuild.txt'

# package 
if mode == 0:
    appDir = project_config + '-iphonesimulator/'
else:
    appDir = project_config + '-iphoneos/'
ipaName = game['gameName'] + '_' + channelName + '_' + versionName + '.ipa'
cmd = 'xcrun -sdk iphoneos PackageApplication -v ' + '"' + xcodeDir + '/build/' + appDir + project_name + '.app" -o "' + outputDir + '/' + ipaName + '"'













def runSpecial(sdk, srcDir, destDir, manifestFile, sdkConfigFile):
	specialScript = os.path.join(srcDir, "special.py")
	if os.path.exists(specialScript):
		sysPath = copy.deepcopy(sys.path)
		sys.path.append(os.path.abspath(srcDir))
		import special
		ret = special.run(sdk, manifestFile, sdkConfigFile, os.path.abspath(destDir))
		if ret:
			print "[ %s ] Error! run special script" % sdk
			return 1
		del sys.modules["special"]
		sys.path = sysPath
	return 0

def runSpecialAfterR(sdk, srcDir, destDir, manifestFile, sdkConfigFile):
	specialScript = os.path.join(srcDir, "special_afterR.py")
	if os.path.exists(specialScript):
		sysPath = copy.deepcopy(sys.path)
		sys.path.append(os.path.abspath(srcDir))
		import special_afterR
		ret = special_afterR.run(sdk, manifestFile, sdkConfigFile, os.path.abspath(destDir))
		if ret:
			print "[ %s ] Error! run special_afterR script" % sdk
			return 1
		del sys.modules["special_afterR"]
		sys.path = sysPath
	return 0


def Build(configFile, toolPath):
	# configFile = "./config/config.json"
	if not os.path.exists(configFile):
		print "Error! no config file, path: %s" % configFile
		return
	config = Configer()
	config.loadConfig(configFile, toolPath)

	# unpack apk
	apkPath = config.getApkPath()
	if not apkPath:
		print "Error! no apk path, please set in config.json"
		return
	apkPath = os.path.abspath(apkPath)
	apkName = config.getApkName()
	destDir = config.getUnpackPath()
	if not destDir:
		print "Error! no dest dir, please set in config.json"
		return
	destDir = os.path.abspath(destDir)
	destPath = os.path.join(destDir, apkName)
	fileutils.copyFile(apkPath, destPath)

	apkutils.init(toolPath)
	unpackPath = os.path.join(destDir, "apk_unpack")
	ret = apkutils.decompileApk(destPath, unpackPath)
	if ret:
		return
	
	basePath = unpackPath
	sdks = config.getSdkList()

	if len(sdks) > 0:
		basePath = os.path.join(destDir, "apk_base")
		if os.path.exists(basePath):
			fileutils.clearDir(basePath)
		fileutils.copyFiles(unpackPath, basePath)

	packageName = ""
	# copy to base dir
	for sdk in sdks:
		destPath = basePath
		
		# obtain sdk config
		srcSdkDir = config.getSdkDir(sdk)
		srcSdkConfigDir = config.getSdkConfigDir(sdk)
		sdkConfigFile = os.path.join(srcSdkConfigDir, "config.json")
		if os.path.exists(sdkConfigFile):
			sdkConfig = copy.deepcopy(config)
			sdkConfig.loadConfig(sdkConfigFile, None)
		else:
			sdkConfig = config

		# obtain mainfest file
		manifestFile = os.path.abspath(os.path.join(destPath, "AndroidManifest.xml"))
		
		# copy res files
		ret = apkutils.copySdkFilesToApk(sdk, srcSdkDir, destPath, manifestFile, sdkConfig.getAppOrientation())
		if ret:
			print "[ %s ] Error! copy sdk files to apk" % sdk
			return

		# modify aonesdk.json
		newChannelName = sdkConfig.getChannelName()
		if newChannelName is not None and len(newChannelName) > 0:
			destAonesdkJson = os.path.join(destPath, "assets/aonesdk.json")
			ret = apkutils.modifyAonesdkJsonChannelName(destAonesdkJson, newChannelName)
			if ret:
				print "[ %s ] Error! modify aonesdk.json" % sdk
				return
		
		# modify package name
		if packageName != config.getPackageName():
			packageName = apkutils.modifyPackageName(sdk, manifestFile, config.getPackageName())

		# run special script
		ret = runSpecial(sdk, srcSdkDir, destPath, manifestFile, sdkConfigFile)
		if ret:
			return
		# specialScript = os.path.join(srcSdkDir, "special.py")
		# if os.path.exists(specialScript):
		# 	sysPath = copy.deepcopy(sys.path)
		# 	sys.path.append(os.path.abspath(srcSdkDir))
		# 	import special
		# 	ret = special.run(sdk, manifestFile, sdkConfigFile, os.path.abspath(destPath))
		# 	if ret:
		# 		print "[ %s ] Error! run special script" % sdk
		# 		return
		# 	del sys.modules["special"]
		# 	sys.path = sysPath

	# copy to new channel_sdk dir
	channelSdks = config.getChannelSdkList()
	for sdk in channelSdks:
		destPath = os.path.join(destDir, "apk_" + sdk)
		if os.path.exists(destPath) and sdk != "base":
			fileutils.clearDir(destPath)
		if basePath != destPath:
			fileutils.copyFiles(basePath, destPath)
		
		# obtain sdk config
		srcSdkDir = config.getSdkDir(sdk)
		srcSdkConfigDir = config.getSdkConfigDir(sdk)
		sdkConfigFile = os.path.join(srcSdkConfigDir, "config.json")
		if os.path.exists(sdkConfigFile):
			sdkConfig = copy.deepcopy(config)
			sdkConfig.loadConfig(sdkConfigFile, None)
		else:
			sdkConfig = config

		# obtain mainfest file
		manifestFile = os.path.abspath(os.path.join(destPath, "AndroidManifest.xml"))
		
		# copy res files
		ret = apkutils.copySdkFilesToApk(sdk, srcSdkDir, destPath, manifestFile, sdkConfig.getAppOrientation())
		if ret:
			print "[ %s ] Error! copy sdk files to apk" % sdk
			return
		
		# modify aonesdk.json
		srcAonesdkJson = os.path.join(srcSdkDir, "assets/aonesdk.json")
		destAonesdkJson = os.path.join(destPath, "assets/aonesdk.json")
		ret = apkutils.modifyAonesdkJson(srcAonesdkJson, destAonesdkJson)
		if ret:
			print "[ %s ] Error! modify aonesdk.json" % sdk
			return

		# add splash
		if sdkConfig.getHasSplash() == "True":
			apkutils.addSplash(sdk, srcSdkDir, destPath)

		# modify package name
		if packageName != sdkConfig.getPackageName() or sdk != "base":
			packageName = apkutils.modifyPackageName(sdk, manifestFile, sdkConfig.getPackageName())
		
		# run special script
		ret = runSpecial(sdk, srcSdkDir, destPath, manifestFile, sdkConfigFile)
		if ret:
			return
		# specialScript = os.path.join(srcSdkDir, "special.py")
		# if os.path.exists(specialScript):
		# 	sysPath = copy.deepcopy(sys.path)
		# 	sys.path.append(os.path.abspath(srcSdkDir))
		# 	import special
		# 	ret = special.run(sdk, manifestFile, sdkConfigFile, os.path.abspath(destPath))
		# 	if ret:
		# 		print "[ %s ] Error! run special script" % sdk
		# 		return
		# 	del sys.modules["special"]
		# 	sys.path = sysPath

		# todo. modify app name
		# apkutils.modifyAppName(sdk, manifestFile, sdkConfig)

		# generate R file
		ret = apkutils.generateR(sdk, destPath, manifestFile, packageName)
		if ret:
			print "[ %s ] Error! generate R file" % sdk
			return
		
		# run special after generating R file
		for otherSdk in sdks:
			ret = runSpecialAfterR(otherSdk, config.getSdkDir(otherSdk), destPath, manifestFile, sdkConfigFile)
			if ret:
				return
		
		# modify icon
		ret = apkutils.modifyIcon(sdk, srcSdkDir, destPath)
		if ret:
			print "[ %s ] Error! modify icon" % sdk
			return

		# compile apk
		newApkName = apkName[0:-4] + "_" + sdk + ".apk"
		newApkPath = destDir
		newApkPath = os.path.join(newApkPath, newApkName)
		newApkPath = os.path.abspath(newApkPath)
		ret = apkutils.compileApk(newApkPath, destPath)
		if ret:
			print "[ %s ] Error! compile apk" % sdk
			return

		# add unknown files to apk
		unknownDir = os.path.join(destPath, "unknown")
		if os.path.exists(unknownDir):
			apkutils.addUnknownFilesToApk(newApkPath, unknownDir)
		
		# sign apk
		ret = apkutils.signApk(newApkPath, sdkConfig.getKeyStoreData())
		if ret:
			print "[ %s ] Error! sign apk" % sdk
			return

		# align apk
		destApkPath = os.path.join(os.path.dirname(apkPath), "output")
		if not os.path.exists(destApkPath):
			os.mkdir(destApkPath)
		destApkPath = os.path.join(destApkPath, newApkName)
		destApkPath = os.path.abspath(destApkPath)
		ret = apkutils.alignApk(newApkPath, destApkPath)
		if ret:
			print "[ %s ] Error! align apk" % sdk
			return

if __name__ == "__main__":
	print "auto pack start !!!"
	toolPath = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "./../.."))
	Build(sys.argv[1], toolPath)
	print "auto pack finish !!!"
