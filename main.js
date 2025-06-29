const { app, BrowserWindow } = require('electron/main')
const { openSerialPort } = require('./library/SerialManagement');

const path = require('path');
require('electron-reload')(__dirname, {
  electron: path.join(__dirname, 'node_modules', '.bin', 'electron'),
  // Si tu veux aussi recharger à la modification de fichiers .css/.html :
  hardResetMethod: 'exit',
});

const createWindow = () => {
  const win = new BrowserWindow({
    width: 800,
    height: 600
  })

  win.loadFile('index.html')
}

app.disableHardwareAcceleration();
app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.whenReady().then(() => {
  openSerialPort('/dev/tty.usbmodem1101', 115200); 
});
