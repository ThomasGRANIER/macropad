const { app, BrowserWindow, ipcMain } = require('electron/main')
const fs = require('fs');
const { openSerialPort, closeSerialPort, setProfile } = require('./library/SerialManagement');
const { dialog } = require('electron');
const path = require('path');
const { logLevel, log } = require('./library/logs');

let fileLog = "Main";
let profile = {
  current : 1,
  list : [1,2]
}

// Charger la config
const configPath = path.join(__dirname, 'conf.json');
let config;

try {
  const rawData = fs.readFileSync(configPath);
  config = JSON.parse(rawData);
  log(logLevel.info,fileLog,`Configuration chargée : ${JSON.stringify(config)}`);
} catch (err) {
  console.error("Erreur de lecture du fichier de configuration :", err);
}

require('electron-reload')(__dirname, {
  electron: path.join(__dirname, 'node_modules', '.bin', 'electron'),
  // Si tu veux aussi recharger à la modification de fichiers .css/.html :
  hardResetMethod: 'exit',
});

const createWindow = () => {
  const win = new BrowserWindow({
    width: 950,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  })
  // win.setMenu(null)
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

// Permet au renderer de lire la valeur actuelle
ipcMain.handle('get-profile', () => {
  return profile;
});

// Permet au renderer de la modifier
ipcMain.on('set-profile', (event, newProfile) => {
  profile.current = parseInt(newProfile);
  log(logLevel.info,fileLog, `Profil selectionné : ${profile.current}`)
  //setProfile(profile.current)
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

ipcMain.on('EditPage', (event, data) => {
  const { id, profile } = data;
  const win = BrowserWindow.getFocusedWindow();
  if (win) {
    win.loadFile('EditPage/EditPage.html', { query: { btnId: id, profile: profile } });
  }
});


ipcMain.on('go-back', (event) => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) {
    win.loadFile('index.html');
  }
});

ipcMain.handle('show-exit-dialog', async () => {
  const result = await dialog.showMessageBox({
    type: 'warning',
    buttons: ['Annuler', 'Quitter sans sauvegarder', 'Sauvegarder et quitter'],
    defaultId: 2, // sélection par défaut sur "Sauvegarder et quitter"
    cancelId: 0,
    title: 'Quitter',
    message: 'Vous avez des modifications non sauvegardées. Que voulez-vous faire ?',
  });

  return result.response; // 0, 1 ou 2 selon le bouton cliqué
});

app.whenReady().then(() => {
  openSerialPort(profile.current, config.SerialPort, 115200);
});
