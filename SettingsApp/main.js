const { app, BrowserWindow } = require('electron')
const path = require('path')
const url = require('url')

let jsdom = require('jsdom');
let $ = require('jquery')(new jsdom.JSDOM().window);

require('select2')

function createWindow() {

    let mainWindow = new BrowserWindow({
        frame: false,
        width: 800,
        height: 600,
        backgroundColor: '#222',
        icon: url.format(path.join(__dirname, '/icon.png')),
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            enableRemoteModule: true, 
        }
    })

    mainWindow.setMenuBarVisibility(false)

    mainWindow.loadFile('index.html')

    mainWindow.webContents.once('dom-ready', () => {
        $('#reward-list').select2();
    });

    // Emitted when the window is closed.
    mainWindow.on('closed', function () {
        mainWindow = null
    })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    createWindow()

    app.on('activate', function () {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.

