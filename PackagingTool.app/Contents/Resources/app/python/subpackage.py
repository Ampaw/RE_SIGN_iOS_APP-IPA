#coding:utf-8

import utils 
import os
import biplist
import shutil
import fileutils
import sys
from config import Configer
# import xcodeutils
import json
import argparse

#需要签名的文件
sign_arr =[]


'''read json file from disk'''
def loadJson(filepath):
	reload(sys)
	sys.setdefaultencoding('utf-8')
	with open(filepath) as fp:
		jsonData = json.load(fp)
	return jsonData

'''write jsonfile into disk'''
def writeJson(jsonfile,filepath):
	file =json.dumps(jsonfile)
	with open(filepath, 'wb') as fp:
		fp.write(file)
	

'''更改plist文件,只能修改已经有了的字段'''
def modifyPlist(key,value,appPath):
	plistPath = os.path.join(appPath,'Info.plist')
	command ="/usr/libexec/PlistBuddy -c 'Set :"+key+" "+value+"'"+' '+plistPath
	return utils.execCommand(command)

'''更改icon'''
def modifyIcon(iconPath,appPath):
	try:
		filelist=os.listdir(iconPath)
		leng =len(filelist)
	except Exception as e:
		raise e
	if leng==23:
		for files in filelist:
			if os.path.splitext(files)[1]=='.png':
				for oldIcon in os.listdir(appPath):
					if files==oldIcon:
						try:
							newIconPath=iconPath+'/'+files
							oldIconPath=appPath+'/'+oldIcon
							fileutils.copyFile(newIconPath,oldIconPath)
						except Exception as e:
							raise e			
			else:
				print 'icon suffix not png,please check'
	else:
		print 'icon count is wrong'			
	

'''logo'''
def modifyLogo(logoPath,appPath):
	try:
		return fileutils.copyFile(logoPath,appPath+'/logo.png')
	except Exception as e:
		raise e	
	
'''修改uuconfig.json,可以修改AppStore_AppleId，td_appid，td_channel'''

def modifyConfig(key,value,appPath):
	try:
		jsonData=loadJson(appPath+'/uuSdkConfig.json')
		tempArr=[]
		if jsonData.has_key('sdks'):
			for sdk in jsonData['sdks']:
				for keys in sdk:
					if keys =='init_params':
						for param in sdk['init_params']:
							if param==key:
								sdk['init_params'][key]=value
				tempArr.append(sdk)
		jsonData['sdks']=tempArr
		writeJson(jsonData,appPath+'/uuSdkConfig.json')
	except Exception as e:
		raise e
				
'''修改aonesdk.json,只能修改已经有了的字段'''
def modifyAonesdk(key,value,appPath):
	jsonData = loadJson(os.path.join(appPath,'aonesdk.json'))
	for keys in jsonData:
		if keys==key:
			jsonData[key]=value
			print 'modify aonesdk success ,key: %s,value: %s' %(key,value)
	writeJson(jsonData,appPath+'/aonesdk.json')

def getEntitlements_plist(path,appath):
	temp_path =os.path.split(appath)[0]
	provision_path =os.path.join(temp_path,'mobileprovision.plist')
	execStr ='security cms -D -i '+path+' >'+provision_path
	ret = utils.execCommand(execStr)
	if ret:
		raise Exception(execStr+'command error')
	entitlements_path =os.path.join(temp_path,'entitlements.plist')
	execStr ="/usr/libexec/PlistBuddy -x -c 'Print:Entitlements' "+provision_path+'>'+entitlements_path
	ret =utils.execCommand(execStr)
	if ret:
		raise Exception(execStr+'command error')
	os.remove(provision_path)
	if os.path.exists(entitlements_path):
		return entitlements_path
	

def recursive_file(path):
	sign_arr_suffix =[".dylib",".so",".0",".vis",".pvr",".framework",".appex",".app"]
	for files in os.listdir(path):
		files_path =os.path.join(path,files)
		#取应该签名的文件
		if os.path.splitext(files)[1] in sign_arr_suffix:
			sign_arr.append(files_path)
			print 'found  file need resign %s' %sign_arr

		#删除CodeResources文件
		if os.path.split(files_path)[1]=='CodeResources':
			_CodeResources =os.path.split(files_path)[0] 
			print 'will delete _CodeResources %s' %_CodeResources
			command = "rm -r " +_CodeResources 
			if utils.execCommand(command):
				raise Exception('remove _CodeResources dir fail')
			if os.path.exists(_CodeResources):
				print 'delete _CodeSignature dir failed'
				raise Exception('remove _CodeResources dir fail')
			else:
				print 'delete _CodeSignature dir success'
		
		if os.path.isdir(files_path):
			recursive_file(files_path)	

def getAppIdentifier(path):
	plist = biplist.readPlist(path)
	if not plist.has_key('application-identifier'):
		return
	strs =plist['application-identifier']
	arr =strs.split('.')
	identifier =''
	for index,value in enumerate(arr):
		if index!=0:
			if index==len(arr)-1:
				identifier =identifier+value
			else:
				identifier =identifier+value+'.'	
	return identifier


def re_sign(appPath,certificateName,provisonpath):
	#证书名
	# codeSign =''
	#配置文件路径
	mobileprovision_path =provisonpath
	#授权文件路径
	entitlements_path =''
	certificateName =certificateName.replace('kongge',' ')
	certificateName =certificateName.replace('kuohao','(')
	
	certificateName =certificateName.replace('fankuoshao',')')

	print 'certificate name :%s\n' %certificateName
	
	if os.path.exists(mobileprovision_path):
		ret =fileutils.copyFile(mobileprovision_path,os.path.join(appPath,'embedded.mobileprovision'))
		if ret:
			raise Exception('copy embedded.mobileprovision faid into'+appPath)
		print 'replace mobileprovision file success' 
	else:
		print 'mobileprovision file don\'t exist'
		raise Exception('mobileprovision file don\'t exist')
	
	#生成getEntitlements_plist文件
	entitlements_path=getEntitlements_plist(mobileprovision_path,appPath)
	if entitlements_path:
		print 'generate entitlements.plist success,path:%s' %entitlements_path
	else:
		raise Exception('generate entitlements.plist error')

	#修改bundleid
	appIdentifier =getAppIdentifier(entitlements_path)
	if appIdentifier:
		ret =modifyPlist('CFBundleIdentifier',appIdentifier,appPath)
		if ret:
			raise Exception('modify bundle id fail')
		else:
			print 'modify CFBundleIdentifier success value : %s' %appIdentifier
	else:
		raise Exception('getAppIdentifier fail')
	
	#找到需要签名的文件
	print 'resursive file...\n'
	recursive_file(appPath)
	print 'resursive success \n'

	print 'start resign \n'
	print 'signfile: %s \n' %sign_arr
	for signfile in sign_arr:
		execStr = '/usr/bin/codesign -vvv -fs ' +'"'+certificateName+'"'+' --no-strict --entitlements '+entitlements_path+' '+signfile
		ret = utils.execCommand(execStr)
		if ret:
			raise Exception('sign fail --'+signfile)
	
	command = '/usr/bin/codesign -vvv -fs ' +'"'+certificateName+'"'+' --no-strict --entitlements '+entitlements_path+' '+appPath
	ret = utils.execCommand(command)
	if ret:
		print 'sign fail'
		raise Exception('sign fail --'+appPath)
	command ='/usr/bin/codesign --verify '+appPath
	ret =utils.execCommand(command)
	if ret:
		print 'sign error'
		raise Exception('verify sign fail')
	print '%s sign success \n' %appPath

	command ='/usr/bin/codesign -vv -d '+appPath
	utils.execCommand(command)

	#开始压缩
	print 'start compress \n'
	
	Payload_path = os.path.join(os.path.split(appPath)[0],"Payload")
	if not os.path.exists(Payload_path):
		command = "mkdir " + Payload_path
		if utils.execCommand(command):
			raise Exception('mkdir Payload fail')
		print 'mk dir Payload success'
	else:
		for files in os.listdir(Payload_path):
			path = os.path.join(Payload_path,files)
			command ='rm -f '+path
			if utils.execCommand(command):
				raise Exception('remove fail '+path)
	command = "mv " + appPath + " " + Payload_path
	if utils.execCommand(command):
		raise Exception('move .app into Payload dir fail')

	print 'move .app into /Payload/ success'
	os.chdir(os.path.split(appPath)[0])
	command = "zip -q -r -m " + os.path.join(os.path.split(appPath)[0],'re_sign_dev.ipa') + " " +'./Payload'
	ret =utils.execCommand(command)
	if ret:
		print 'zip fail'
		raise Exception('zip fail') 
	print 'zip Payload success'
	print 'delete Payload dir success'
	for files in os.listdir(os.path.split(appPath)[0]):
		files_path = os.path.join(os.path.split(appPath)[0],files)
		if files!='re_sign_dev.ipa':
			command = 'rm -rf '+files_path
			utils.execCommand(command)
	return os.path.join(os.path.split(appPath)[0],'re_sign_dev.ipa')


def get_app_path(path,root_path):

	temp_path =os.path.join(root_path,'Library','AutoPack/temp')
	if not os.path.exists(temp_path):
		command ='mkdir -p '+temp_path
		utils.execCommand(command)
	else:
		for files in os.listdir(temp_path):
			command ='rm -rf '+os.path.join(temp_path,files)
			utils.execCommand(command)
	
	print 'start copy app into %s' % temp_path

	command = "cp -R " + path + " " +temp_path
	if utils.execCommand(command):
		raise Exception('copy app fail into '+temp_path)
	
	tempo_filename =os.path.split(path)[1]
	if os.path.splitext(tempo_filename)[1]=='.ipa':
		command ='unzip -q -o '+os.path.join(temp_path,tempo_filename) +' -d '+temp_path
		ret =utils.execCommand(command)
		if ret:
			print 'unzip fail'
			raise Exception('copy app fail into '+temp_path)
		if not os.path.exists(os.path.join(temp_path,'Payload')):
			print 'not Payload dir'
			raise Exception('not Payload dir')
		else:
			command ='rm -rf '+os.path.join(temp_path,tempo_filename)
			if utils.execCommand(command):
				raise Exception('remove temp ipa fail')
			print 'delete temp ipa file success'

		for files in os.listdir(os.path.join(temp_path,'Payload')):
			if not os.path.splitext(files)[1]=='.app':
				continue
			command ='mv '+os.path.join(temp_path,'Payload',files)+' '+temp_path
			ret =utils.execCommand(command)
			if ret:
				print 'move file fail'
				raise Exception('move file fail')
			command ='rm -rf '+os.path.join(temp_path,'Payload')
			if utils.execCommand(command):
				raise Exception('remove null Payload  dir fail')
			return os.path.join(temp_path,files)
	else:
		return os.path.join(temp_path,tempo_filename)
	
def cut_image_py(icon_path,path,current_path):
	tempath =os.path.split(path)[0]
	ret = fileutils.copyFile(icon_path,os.path.join(tempath,'icon.png'))
	if ret:
		return ret
	print 'copy icon into %s success' %tempath
	command ='python '+os.path.join(current_path,'modify_icon.py')+' '+os.path.join(tempath,'icon.png')
	ret =utils.execCommand(command)
	if ret:
		print 'cut image fail'
		return ret
	icon_arr_path =os.path.join(tempath,'icon')
	modifyIcon(icon_arr_path,appPath)
	print 'modify icon success'
	#修改icon成功，开始清除中途产生的资源 
	fileutils.clearDir(icon_arr_path)
	os.rmdir(icon_arr_path)
	os.remove(os.path.join(tempath,'icon.png'))

def move_clear(path,outpath):
	if not path:
		print 'no ipa path ,resign error'
		raise Exception('no ipa path ,resign error')
	dir_path =os.path.split(path)[0]
	output_path =str(outpath)+'.ipa'
	command = 'mv -f '+path +' '+output_path
	if utils.execCommand(command):
		raise Exception('move ipa fail into'+output_path)	
	command = 'rm -rf '+dir_path
	if utils.execCommand(command):
		raise Exception('remove temp dir fail')	

def modify_configfile(app_path,config_path):
	#读config文件
	jsonData = loadJson(config_path)
	if not jsonData:
		raise Exception('read json file error')
	
	#修改info.plist
	if jsonData.has_key('InfoPlist'):
		infoplist =jsonData['InfoPlist']
		for keys in infoplist:
			if keys=="_comment":
				continue
			print 'key: %s,value: %s' %(keys,infoplist[keys])
			ret =modifyPlist(keys,infoplist[keys],app_path)
			if ret:
				raise Exception("modify plist fail")
	#修改uuconfig.json
	if jsonData.has_key('uuconfigJson'):
		uuconfigJson = jsonData['uuconfigJson']
		for jsons in uuconfigJson:
			if jsons.has_key('init_params'):
				initParam =jsons['init_params']
				for keys in initParam:
					if keys=='_comment':
						continue
					print 'key: %s,value: %s' %(keys,initParam[keys])
					modifyConfig(keys,initParam[keys],app_path)
	#修改aonesdk.json
	if jsonData.has_key('aonesdkJson'):
		aonesdkJson =jsonData['aonesdkJson']
		for keys in aonesdkJson:
			modifyAonesdk(keys,aonesdkJson[keys],app_path)

	#修改游戏版本
	if jsonData.has_key('game_version_number'):
		version =jsonData['game_version_number']
		if not version:
			raise Exception('game_version_number is null')
		with open(os.path.join(app_path,'version'), 'wb') as fp:
			fp.write(version)
		print 'modify game version success,new version :%s' %version

def getRootPath(currentPath):
    rootArr =currentPath.split("/")
    for (index,value) in enumerate(rootArr):
        if value=='Users':
            path =os.path.join('/',value,rootArr[index+1])
            return path

#程序开始
if __name__ == "__main__":
	print "\n----- AUTO PACKAGE START-------\n"
	currentPath = sys.argv[0]
	appPath =sys.argv[1]
	output_path = sys.argv[2]
	config_path = sys.argv[3]
	icon_path = sys.argv[4]
	certificateName = sys.argv[5]
	logo_path = sys.argv[6]
	provison_path = sys.argv[7]

	#当前路径
	currentPath =os.path.split(currentPath)[0]
	# print 'apppath :%s \n output path: %s \n config path: %s \n icon path: %s \n logo path: %s' %(appPath,output_path,config_path,icon_path,logo_path)
	print 'current path: '+currentPath
	print 'app path :'+appPath
	print 'output path: '+output_path
	print 'config path: '+config_path
	print 'icon path: ' +icon_path
	print 'logo path: '+logo_path
	print 'certificate name' +certificateName
	print 'provision path '+provison_path

	#根路径
	rootpath =getRootPath(provison_path)
	print 'rootpath: '+rootpath

	#拿到最终的app路径
	appPath = get_app_path(appPath,rootpath)
	if not appPath:
		print 'get app path error'
		raise Exception('get app path error')	
	print 'temp app path %s' %appPath

	# 开始修改logo
	if logo_path!="null":
		print "start modify logo..."
		ret = modifyLogo(logo_path,appPath)
		if ret:
			raise Exception('modify logo fail')
		print "modify logo success"

	# 修改logo成功，开始修改icon
	if icon_path!="null":
		print "start modify icon..."
		if cut_image_py(icon_path,appPath,currentPath):
			raise Exception('modify icon fail')
		print 'modify icon success'


	# 根据配置文件修改游戏包内内容
	if config_path!="null":
		print 'start modify game configuration by json file'
		modify_configfile(appPath,config_path)
		print 'success to modify game configuration'
	
	#开始重签
	print 'start RE_SIGN'
	
	ipa_path= re_sign(appPath,certificateName,provison_path)
	
	#移动ipa 清除产生的资源
	move_clear(ipa_path,output_path)
	print 'RE_SIGN SUCCESS \n'
	print ' -----AUTO PACKAGE END-----\n'
	

	

