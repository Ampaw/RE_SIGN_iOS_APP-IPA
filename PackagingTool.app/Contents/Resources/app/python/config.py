#coding:utf-8
import os
import sys
import json

class Configer(object):
	_projPath = ""
	_xcodeProjPath = ""
	_sdksPath = ""
	_sdksConfigPath = ""
	_base_sdkList = []
	_channelList = []
	_channel_sdkList = []
	_channelName = ""
	_appOrientation = ""
	_packageName = ""
	_hasSplash = ""

	_signId = ""                # 签名证书 发布版本
	_signId_dev = ""            # 签名证书 测试版本
	_developmentTeam = ""       # iOS打包证书组织单位名称
	_profileSpecifier = ""      # 授权文件名称 发布版本
	_profileSpecifier_dev = ""  # 授权文件名称 测试版本
	_idenditifier = ""          # 游戏包名
	_displayName = ""           # 游戏名称
	_buildConfig = ""

	_keystore = ""
	_keyAlias = ""
	_keyStorePwd = ""
	_keyAliasPwd = ""

	_special = ""

	_versionNumber = "" # 应用程序发布标示
	_buildNumber = ""   # 应用程序内部标示
	

	_appleId = ""    # 苹果支付插件需要的appleID
	_tdAppId = ""    # talkingdata插件需要的appid
	_tdChannel = ""  # talkingdata插件需要的渠道
	_reyunAppId = "" # ReyunTrack 插件需要的appId

	_iconPath = ""   # icon路径
	_appName = ""    # 游戏内需要显示的名称

	def __init__(self):
		pass

	def loadConfig(self, configFile, toolPath):
		if not os.path.exists(configFile):
			return

		config_path = os.path.dirname(configFile)
		
		fp = open(configFile)
		jsonData = json.load(fp)
		fp.close()

		# 系统默认的编码格式是ASCII编码，通过sys.getdefaultencoding()来查询
		# 如果有中文，需要设置编码的格式
		reload(sys)
		sys.setdefaultencoding('utf-8')
		if (jsonData.has_key("projPath")):
			self._projPath = os.path.join(config_path, "../build", jsonData["projPath"])

		if (jsonData.has_key("xcodeProjPath")):
			self._xcodeProjPath = jsonData["xcodeProjPath"]

		if not self._sdksPath and toolPath:
			self._sdksPath = os.path.join(toolPath, "./../../export/ios/sdks")

		if not self._sdksConfigPath:
			self._sdksConfigPath = os.path.join(config_path, "../sdks")

		if (jsonData.has_key("signId")):
			self._signId = jsonData["signId"]

		if (jsonData.has_key("signId_dev")):
			self._signId_dev = jsonData["signId_dev"]

		if (jsonData.has_key("DevelopmentTeam")):
			self._developmentTeam = jsonData["DevelopmentTeam"]

		if (jsonData.has_key("ProvisioningProfileSpecifier")):
			self._profileSpecifier = jsonData["ProvisioningProfileSpecifier"]

		if (jsonData.has_key("ProvisioningProfileSpecifier_dev")):
			self._profileSpecifier_dev = jsonData["ProvisioningProfileSpecifier_dev"]

		if (jsonData.has_key("appIdentifier")):
			self._idenditifier = jsonData["appIdentifier"]

		if (jsonData.has_key("displayName")):
			self._displayName = jsonData["displayName"]

		if (jsonData.has_key("buildConfig")):
			self._buildConfig = jsonData["buildConfig"]
		
		if (jsonData.has_key("base_sdks")):
			self._base_sdkList = jsonData["base_sdks"]

		if (jsonData.has_key("channels")):
			self._channelList = jsonData["channels"]

		if (jsonData.has_key("channel_sdks")):
			self._channel_sdkList = jsonData["channel_sdks"]

		if (jsonData.has_key("channel_name")):
			self._channelName = jsonData["channel_name"]
		
		if (jsonData.has_key("key.store") and jsonData["key.store"]):
			keystorePath = os.path.join(config_path, jsonData["key.store"])
			self._keystore = keystorePath
		if not self._keystore and toolPath:
			self._keystore = os.path.join(toolPath, "buildFiles/ios/aonesdk.keystore")
		
		if (jsonData.has_key("key.alias") and self._keystore):
			self._keyAlias = jsonData["key.alias"]
		if not self._keyAlias:
			self._keyAlias = "aonesdk.keystore"
		
		if (jsonData.has_key("key.store.password") and self._keystore):
			self._keyStorePwd = jsonData["key.store.password"]
		if not self._keyStorePwd:
			self._keyStorePwd = "aonesoft"
		
		if (jsonData.has_key("key.alias.password") and self._keystore):
			self._keyAliasPwd = jsonData["key.alias.password"]
		if not self._keyAliasPwd:
			self._keyAliasPwd = "aonesoft"

		if (jsonData.has_key("packageName")):
			self._packageName = jsonData["packageName"]
		if (jsonData.has_key("appOrientation")):
			self._appOrientation = jsonData["appOrientation"]
		if (jsonData.has_key("hasSplash")):
			self._hasSplash = jsonData["hasSplash"]

		if (jsonData.has_key("special")):
			self._special = jsonData["special"]

		if (jsonData.has_key("appVersion")):
			self._versionNumber = jsonData["appVersion"]

		if (jsonData.has_key("buildNumber")):
			self._buildNumber = jsonData["buildNumber"]


		if (jsonData.has_key("AppStore_AppleId")):
			self._appleId = jsonData["AppStore_AppleId"]

		if (jsonData.has_key("td_appid")):
			self._tdAppId = jsonData["td_appid"]

		if (jsonData.has_key("td_channel")):
			self._tdChannel = jsonData["td_channel"]

		if (jsonData.has_key("iconPath")):
			self._iconPath = jsonData["iconPath"]

		if (jsonData.has_key("reyun_appId")):
			self._reyunAppId = jsonData["reyun_appId"]

		if (jsonData.has_key("appName")):
			self._appName = jsonData["appName"]

	def getSignId(self):
		return self._signId

	def getSignId_dev(self):
		return self._signId_dev

	def getDevelopmentTeam(self):
		return self._developmentTeam

	def getProfileSpecifier(self):
		return self._profileSpecifier	

	def getProfileSpcifier_dev(self):
		return self._profileSpecifier_dev

	def getIdentifier(self):
		return self._idenditifier

	def getDisplayName(self):
		return self._displayName

	def getBuildConfig(self):
		return self._buildConfig

	def getProjPath(self):
		return self._projPath

	def getXcodeProjPath(self):
		return self._xcodeProjPath

	def getSdkDir(self, sdk):
		return os.path.join(self._sdksPath, sdk)

	def getSdkConfigDir(self, sdk):
		return os.path.join(self._sdksConfigPath, sdk)

	def getBaseSdkList(self):
		return self._base_sdkList

	def getChannels(self):
		return self._channelList

	def getChannelSdkList(self):
		return self._channel_sdkList

	def getChannelName(self):
		return self._channelName

	def getAppOrientation(self):
		return self._appOrientation

	def getPackageName(self):
		return self._packageName

	def getHasSplash(self):
		return self._hasSplash

	def getKeyStoreData(self):
		return { 'keystore': self._keystore, 
				'keyalias': self._keyAlias, 
				'keystorePwd': self._keyStorePwd, 
				'keyaliasPwd': self._keyAliasPwd }

	def getSpeical(self):
		return self._special

	def getVersionNumber(self):
		return self._versionNumber

	def getBuildNumber(self):
		return self._buildNumber
	

	def getAppleId(self):
		return self._appleId

	def getTDAppId(self):
		return self._tdAppId

	def getTDChannel(self):
		return self._tdChannel

	def getIconPath(self):
		return self._iconPath

	def getReyunAppId(self):
		return self._reyunAppId

	def getAppName(self):
		return self._appName
		
	def printMe(self):
		print self.getProjPath()
		print self.getUnpackPath()
		print self.getSdkDir("baidu")
		print self.getSdkConfigDir("baidu")
		print self.getSdkList()
		print self.getChannelSdkList()
		print self.getChannelName()
		print self.getAppOrientation()
		print self.getPackageName()
		print self.getKeyStoreData()
		print self.getDisplayName()
		print self.getAppleId()