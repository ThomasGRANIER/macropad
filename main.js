const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');
const { SerialPort } = require('serialport');
const fs = require('fs');
const notifier = require('node-notifier');

let mainWindow;
let tray;
let config = {};

// Déplace runCommands ici, en dehors de loadConfig
function runCommands(cmds, i = 0) {
  if (i >= cmds.length) return;
  const cmd = cmds[i];
  const delay = 0.2; // Délai en secondes (tu peux ajuster)
  setTimeout(() => {
    if (cmd.type === 'cmd') require('child_process').exec(cmd.value);
    if (cmd.type === 'text') require('child_process').exec(`xdotool type '${cmd.value}'`);
    if (cmd.type === 'key') require('child_process').exec(`xdotool key ${cmd.value}`);
    runCommands(cmds, i + 1);
  }, delay * 1000); // Retard de la commande suivante
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 400,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'icon.png')
  });
  mainWindow.loadFile('index.html');
}

function loadConfig() {
  const raw = fs.readFileSync('config.json');
  config = JSON.parse(raw);
}

function startSerialListening(portPath = '/dev/ttyUSB0', baudRate = 9600) {
  const port = new SerialPort({ path: portPath, baudRate });

  port.on('data', data => {
    const key = data.toString().trim();
    if (config[key]) {
      const action = config[key];
      if (action.notif) {
        notifier.notify({ title: key, message: action.notif });
      }
      runCommands(action.cmd); // Appelle la fonction avec délai
    }
  });
}

app.whenReady().then(() => {
  loadConfig();
  createWindow();
  startSerialListening();

  tray = new Tray(path.join(__dirname, 'icon.png'));
  tray.setToolTip('Macropad Electron');
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'Afficher', click: () => mainWindow.show() },
    { label: 'Quitter', click: () => app.quit() }
  ]));
});
