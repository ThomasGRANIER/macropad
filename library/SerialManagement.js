const { SerialPort } = require('serialport');

SerialPort.list().then(ports => {
    ports.forEach(port => {
      console.log(`Port détecté : ${port.path} - ${port.vendorId || 'inconnu'} - ${port.productId || 'inconnu'}`);
    });
  });

let currentPort = null;
let currentPortPath = null;
let currentBaudRate = 115200;
let isTryingToReconnect = false;
let reconnectInterval = null;

/**
 * Tente d'ouvrir le port série
 * @param {string} portPath
 * @param {number} baudRate
 */
function openSerialPort(portPath, baudRate = 115200) {
  currentPortPath = portPath;
  currentBaudRate = baudRate;

  if (currentPort) {
    currentPort.close(err => {
      if (err) {
        console.error('Erreur en fermant le port existant :', err.message);
      }
    });
    currentPort = null;
  }

  console.log(`Tentative d'ouverture du port : ${portPath}`);

  currentPort = new SerialPort({
    path: portPath,
    baudRate: baudRate,
    autoOpen: false,
  });

  currentPort.open(err => {
    if (err) {
      console.error('Erreur à l’ouverture du port :', err.message);
      scheduleReconnect();
      return;
    }

    console.log(`✅ Port série ouvert : ${portPath}`);
    clearReconnect();
  });

  currentPort.on('data', data => {
    console.log(`📨 Données reçues : ${data.toString()}`);
  });

  currentPort.on('error', err => {
    console.error('💥 Erreur du port série :', err.message);
    scheduleReconnect();
  });

  currentPort.on('close', () => {
    console.warn(`⚠️ Port série fermé : ${portPath}`);
    scheduleReconnect();
  });
}

/**
 * Programme une reconnexion automatique
 */
function scheduleReconnect() {
  if (isTryingToReconnect || !currentPortPath) return;

  isTryingToReconnect = true;

  reconnectInterval = setInterval(() => {
    console.log(`🔁 Tentative de reconnexion sur ${currentPortPath}...`);
    openSerialPort(currentPortPath, currentBaudRate);
  }, 3000); // toutes les 3 secondes
}

/**
 * Annule la reconnexion automatique si elle est en cours
 */
function clearReconnect() {
  if (reconnectInterval) {
    clearInterval(reconnectInterval);
    reconnectInterval = null;
  }
  isTryingToReconnect = false;
}

/**
 * Ferme proprement le port série
 */
function closeSerialPort() {
  if (currentPort && currentPort.isOpen) {
    currentPort.close(err => {
      if (err) {
        console.error('Erreur à la fermeture du port :', err.message);
      }
    });
  }
  clearReconnect();
}

module.exports = {
  openSerialPort,
  closeSerialPort,
};
