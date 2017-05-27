const electron = require('electron')
// Module to control application life.
const app = electron.app
// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow
const certificate =require('./certificate.js')
const path = require('path')
const url = require('url')
const ipcMain = electron.ipcMain
const render = require('./renderer.js')


// console.log(url);

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow


function createWindow () {
  // Create the browser window.
  mainWindow = new BrowserWindow({width: 850, height: 650})

  // and load the index.html of the app.
  mainWindow.loadURL('file://' + __dirname + '/app/index.html')
  
  // Open the DevTools.
  // mainWindow.webContents.openDevTools()

  mainWindow.webContents.on('did-finish-load', function() {
    // window.webContents.send('ping', 'whoooooooh!');
    certificate.get_certificate(mainWindow);
    // var paths =path.exist('/User/LastYear');

    // console.log(paths);
    certificate.get_provision(mainWindow);
  });
  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
    app.quit()
  })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow,function () {
  
  

});

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', function () {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  // console.log('app activate');
  
  if (mainWindow === null) {
    createWindow()
  }
})



//主进程收到渲染进程消息
ipcMain.on('asynchronous-message', (event, arg) => {

  if (arg==='selectPackage') {

   let app_path= render.select_package();
   event.sender.send('selectPackage-reply',app_path);

  }else if (arg==='selectIcon') {

    let icon_path =render.select_image();
    event.sender.send('selectIcon-reply',icon_path);

  }else if (arg==='selectLogo') {

    let logo_path =render.select_image();
    event.sender.send('selectLogo-reply',logo_path);
    
  }else if (arg==='add_config_file') {
    let config_path= render.add_config_file();
    console.log('config_path:'+config_path);
    event.sender.send('add_config_file_reply',config_path);
   
  }

});


ipcMain.on('auto_package_message',(event,arg)=>{

  render.auto_package(arg,event);
  
});



// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
