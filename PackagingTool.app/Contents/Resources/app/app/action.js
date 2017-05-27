
const electron = require('electron')
const ipcRenderer = electron.ipcRenderer
const shell =electron.shell

var object ={};
var provisionObj;
//选择app包后，主进程调用渲染进程
ipcRenderer.on('selectPackage-reply', (event, arg) => {
	// alert(arg);
	var package_name=  document.getElementById('spackage');
	if (!arg) {
		delete object.package_path;
		package_name.value ='';
		shell.beep();
		alert('没有选择任何东西');
		return;
	}
	package_name.value=arg;
	object.package_path =arg;

  });

ipcRenderer.on('selectIcon-reply', (event, arg) => {
	if (!arg) {
		
		delete object.icon_path;
		shell.beep();
		document.getElementById('icon_id').innerHTML = '<br/>点击选择icon';
		alert('没有选择任何东西');
		return;
	}
 	var icon =document.getElementById('icon_id');
 	var path ='file://'+arg;
 	var html ='<img src="'+path+'" '+'alt="点击选择icon" width="100%" height="100%">'
 	icon.innerHTML=html;

 	object.icon_path = arg;
  });

ipcRenderer.on('selectLogo-reply', (event, arg) => {
	if (!arg) {
		shell.beep();
		alert('没有选择任何东西');
		delete object.logo_path;
		document.getElementById('logo_id').innerHTML = '<br/>点击选择logo';
		return;
	}
 	var logo =document.getElementById('logo_id');
 	var path ='file://'+arg;
 	var html ='<img src="'+path+'" '+'alt="点击选择logo" width="100%" height="100%">'
 	logo.innerHTML=html;

 	object.logo_path =arg;
  });


ipcRenderer.on('add_config_file_reply', (event, arg) => {
	var config_button =document.getElementById('add_config');
	if (!arg) {
		config_button.innerText ='添加配置文件';
 		delete object.config_path;
		shell.beep();
		alert('没有选择任何东西');
		return;
	}
 	
	config_button.innerText ='添加配置文件 完成';
 	object.config_path =arg;
  });

ipcRenderer.on('auto_package_button_disable', (event, arg) => {
	var button = document.getElementById('autopackage_button');
	
	if (arg=="finished") {
		reset();
		button.innerText ="打包";
		button.disabled=false;
		document.getElementById('select_pack').disabled = false;
		document.getElementById('reset').disabled = false;
		document.getElementById('add_config').disabled = false;

	}else{
		document.getElementById('select_pack').disabled = true;
		document.getElementById('reset').disabled = true;
		document.getElementById('add_config').disabled = true;
		button.disabled=true;
		button.innerText =arg;

	}
	
	
  });

function selectIcon(){
	ipcRenderer.send('asynchronous-message', 'selectIcon');
}

function selectLogo(){
	
	ipcRenderer.send('asynchronous-message', 'selectLogo');
}

function selectPackage(){
	ipcRenderer.send('asynchronous-message', 'selectPackage');
}

ipcRenderer.on('select_certificate_reply', (event, arg) => {
	certificate_pulldown =document.getElementById('certificate')
	for (var index = 0; index < arg.length; index++) {
		var text = arg[index][0];
		var value =arg[index][1];
		if (value) {
			certificate_pulldown.options.add(new Option(text,value));
		}
		
	}

  });
ipcRenderer.on('provision_reply', (event, arg) => {
	
	provision_pulldown =document.getElementById('mobileprovision');
	if (arg.provisons==undefined&&arg.path==undefined) {
		alert('init provision file fail');
		return;
	}
	provisionObj =arg;

  });

function selectedCerAction(value) {
	try {
		var arr =value.split(': ')
		var str1 = arr[1];
		var arr1 =str1.split(' (');
		var name = arr1[0];
	} catch (error) {
		alert("error")
	}
	if (provisionObj==undefined) {
		alert('请稍等...');
		return;
	}

	provision_pulldown =document.getElementById('mobileprovision');
	provision_pulldown.options.length =0;
	var provisons = provisionObj.provisons;
	for (var index = 0; index < provisons.length; index++) {
		var obj = provisons[index];
		if (name==obj.teamName) {
			var text = obj.Name
			var value =provisionObj.path+'/'+obj.uuid+'.mobileprovision';
			provision_pulldown.options.add(new Option(text,value));
		}
		
	}
	 
	
}


function addConfigFile(){
	ipcRenderer.send('asynchronous-message', 'add_config_file');	
}

function reset(){
	document.getElementById('icon_id').innerHTML ='<br/>点击选择icon';
	document.getElementById('logo_id').innerHTML ='<br/>点击选择logo';
	document.getElementById('spackage').value='';
	document.getElementById('add_config').innerHTML ='添加配置文件';
	object= {};

}

function autoPackage(){
	
	var myselect=document.getElementById("certificate"); 
	var index=myselect.selectedIndex;
	object.certificateName = myselect.options[index].value;
	if (object.certificateName=='null') {
		alert('请选择一个证书');
		return;
	}
	var myselect1=document.getElementById("mobileprovision"); 
	var index=myselect1.selectedIndex;
	object.provisionpath = myselect1.options[index].value;
	// alert(object.provisionpath);
	if (object.provisionpath=='null') {
		alert('请选择一个配置文件');
		return;
	}
	if (object.package_path==undefined) {
		alert('请选择一个包')
		return ;
	}
	
	ipcRenderer.send('auto_package_message', object);

}