import subprocess
import commands

def execCommand(cmd):
	print "[commond]=%s\n"%cmd
	# s = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	# stdoutput, erroutput = s.communicate()
	(status,output)=commands.getstatusoutput(cmd)
	
	# print erroutput
	ret = status
	print output

	if ret:
		print "Execute Command Error! code:" + str(ret)
		# print erroutput
	else:
		print "Execute Command success!\n"
	return ret	


def execCD(cmd):
	s = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	stdoutput, erroutput = s.communicate()
	ret = s.wait()
	if ret:
		raise Exception(erroutput)
		

	