const electron =require('electron')
const dialog = electron.dialog
const fs = require('fs')
var exec = require('child_process').exec;
// const ipcMain = electron.ipcMain

exports.select_package = function(){
	var fileArr =  dialog.showOpenDialog(
	{
		properties: ['openFile'],
		filters: [{ name: 'app', extensions: ['app','ipa'] }]
	}
);
	if (fileArr==undefined) {
		console.log('file is null');
		return;
	}
	let appPath = fileArr.pop();
	console.log('have been select .app file,file path:'+appPath);
	return appPath;
}

exports.select_image=function(){
	var fileArr =  dialog.showOpenDialog(
	{
		properties: ['openFile'],
		filters: [{ name: 'png', extensions: ['png'] }]
	}
);
	if (fileArr==undefined) {
		console.log('file is null');
		return;
	}
	// console.log(fileArr);
	let path = fileArr.pop();
	console.log('have been select image file,file path:'+path);

	return path;
}

exports.add_config_file =function(){
	var fileArr =  dialog.showOpenDialog(
	{
		properties: ['openFile'],
		filters: [{ name: 'json', extensions: ['json'] }]
	}
);
	if (fileArr==undefined) {
		console.log('file is null');
		return;
	}
	let appPath = fileArr.pop();
	console.log('have been select json file,file path:'+appPath);
	return appPath;

}

function output_Ipa() {
	var filename =  dialog.showSaveDialog(
	{
		title:'选择导出ipa包的路径',
		filters:['ipa']
	}
);
	if (filename==undefined) {
		return;
	}
	return filename
	
}

exports.auto_package =function(arg,event){
	var output_path =output_Ipa();
	if (output_path==undefined) {
		dialog.showErrorBox('请指定ipa包的路径和文件名','')
		return;
	}
	event.sender.send('auto_package_button_disable','打包中...');
	console.log('out put path:'+output_path+'.ipa')
	console.log(arg);
	var subpackage_py_path =__dirname+'/python/subpackage.py';
	
	if (arg.icon_path==undefined) {
		arg.icon_path ="null";
	}
	if (arg.logo_path==undefined) {
		arg.logo_path ="null";
	}
	if (arg.config_path==undefined) {
		arg.config_path ="null";
	}
	let command = 'python '+subpackage_py_path+' '+arg.package_path+' '+output_path+' '
					+arg.config_path+' '+arg.icon_path+' '+arg.certificateName+' '+arg.logo_path
					+' ' +arg.provisionpath;
	console.log(command)
	exec(command,
	function(error,stdout,stderr){
		var log_path ='';
		// if (error) {
		// 	console.log(error);
		// 	event.sender.send('auto_package_button_disable','finished');
		// 	dialog.showErrorBox('打包失败',error)
		// }
		if (stderr) {
			console.log(stderr);
			event.sender.send('auto_package_button_disable','finished');
			dialog.showErrorBox('打包失败',stderr)
			log_path =output_path+'_error_log.txt'
			fs.writeFile(log_path,error,function(error){
				if (error) {
				console.log('write log fail '+error);
				dialog.showErrorBox('日志保存失败',error.message)	
				}
			});
			return; 
		}

		event.sender.send('auto_package_button_disable','finished');
		console.log(stdout);
		log_path =output_path+'_success_log.txt'
		fs.writeFile(log_path,stdout,function(error){
			if (error) {
				console.log('write log fail '+error);
				dialog.showErrorBox('日志保存失败',error.message)
				return ;
			}
			dialog.showErrorBox('打包完成','日志路径是'+log_path)		
			});
	}
	);
	


}