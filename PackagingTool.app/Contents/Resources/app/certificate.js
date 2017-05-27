const electron =require('electron')
const dialog = electron.dialog
const fs = require('fs')
var exec = require('child_process').exec;
const ipcMain = electron.ipcMain
const path = require('path')

// electron.

exports.get_certificate =function (window) {
    var command ='security find-identity -v -p codesigning'
    exec(command,
    function (error,stdout,stderr) {

        if (error) {
            console.log(error);
            dialog.showErrorBox('证书出错',stderr)
            return;
        }
        var output =stdout;
        var regexp =RegExp('\"([^\"]*)\"','m');
        var arr =output.split(regexp);
        var outArr =[];   
        outIndex =0;
        for (var index = 0; index < arr.length; index++) {
            if (index%2!=0) {
                var element = arr[index];
                console.log(element);
                var value ='';
                regexp =RegExp(' ','g');
                value =element.replace(regexp,'kongge');
                value =value.replace('(','kuohao');
                value =value.replace(')','fankuoshao'); 
                outArr[++outIndex] =[element,value];                      
            }      
        }
        window.webContents.send('select_certificate_reply', outArr);
    }
    );


}
exports.get_provision = function (window) {

    exec('python '+path.join(__dirname,'python','provision.py')+' '+ __dirname,function (error,stdout,stderr) {
        if (error) {
            dialog.showErrorBox(error,'');
            // console.log(error);
            return;
        }
        console.log(stdout);
        var provisonStr =eval('('+ stdout +')') 
        // console.log(provisonStr);
        // dialog.showErrorBox(__dirname,'');
        // dialog.showErrorBox(stdout,'');
        window.webContents.send('provision_reply', provisonStr);
    });
    
}


