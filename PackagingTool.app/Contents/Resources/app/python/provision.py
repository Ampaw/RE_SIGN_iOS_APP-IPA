#coding:utf-8

import utils 
import os
import fileutils
import sys
import biplist

def get_provision_path(rootPath):

    #拿到配置文件路径
    profile_path =os.path.join(rootPath,'Library/MobileDevice/Provisioning Profiles/')
    if not os.path.exists(profile_path):
        raise Exception('no '+profile_path)
    new_profile_path =os.path.join(rootPath,'Library','tprovison')
    
    #拿到新的配置文件路径
    if not os.path.exists(new_profile_path):
        os.makedirs(new_profile_path)
    else:
        command ='rm -rf '+os.path.join(new_profile_path)
        utils.execCD(command)
        os.makedirs(new_profile_path)
        
    
    for files in os.listdir(profile_path):
        if os.path.splitext(files)[1]=='.mobileprovision':
            if fileutils.copyFile(os.path.join(profile_path,files),new_profile_path):
                raise Exception('copy file into provison/ fail')
    return new_profile_path
        
def get_provision_plist_dir(path):
    temp_plistdir =os.path.join(path,'provisonplist')
    if os.path.exists(temp_plistdir):
        for files in os.listdir(temp_plistdir):
            # os.remove(os.path.join(temp_plistpath,files))
            command ='rm -rf '+os.path.join(temp_plistdir,files)
            utils.execCD(command)
    else:
        os.mkdir(os.path.join(temp_plistdir))
    fileArr =os.listdir(path)
    for index,files in enumerate(fileArr):
        if os.path.splitext(files)[1]=='.mobileprovision':
            filepath =os.path.join(path,files)
            plistpath =os.path.join(temp_plistdir,os.path.splitext(files)[0]+'.plist')
            command ='/usr/bin/security cms -D -i '+filepath+">"+plistpath
            utils.execCD(command) 
            if not os.path.exists(plistpath):
                raise Exception('no plist file')
            # print 'index:%s,len:%s'%(index,len(fileArr))
            readplist(plistpath)
            
            
            
    # return temp_plistdir

def readplist(path):
    plist = biplist.readPlist(path)
    teamName = plist['TeamName']
    Name =plist['Name']
    uuid = plist['UUID']
    out ='{"teamName":"'+teamName+'","Name":"'+Name+'","uuid":"'+uuid+'"},'
    print out

def getRootPath(currentPath):
    rootArr =currentPath.split("/")
    for (index,value) in enumerate(rootArr):
        if value=='Users':
            path =os.path.join('/',value,rootArr[index+1])
            return path

if __name__ == "__main__":
    dirname =sys.argv[1]
    rootpath =getRootPath(dirname)
    #复制系统目录下的配置文件进入工作目录
    provision_dir_path = get_provision_path(rootpath)
    print '{"path":"'+provision_dir_path+'",'
    print '"provisons":['
    #遍历所有的配置文件，拿到相应的plist文件夹
    get_provision_plist_dir(provision_dir_path)
    print "]}"

    