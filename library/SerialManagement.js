const { SerialPort } = require('serialport');
const { analyseYML } = require('./RunnerManager');
const { regexButton, regexEncodeur} = require('./const')

// ### Liste des port avec leur vendorID + producID ###
// SerialPort.list().then(ports => {
//     ports.forEach(port => {
//       console.log(`Port détecté : ${port.path} - ${port.vendorId || 'inconnu'} - ${port.productId || 'inconnu'}`);
//     });
//   });

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
      console.error('Erreur ouverture du port :', err.message);
      scheduleReconnect();
      return;
    }

    console.log(`Port série ouvert : ${portPath}`);
    clearReconnect();
  });

  currentPort.on('data', data => {
    if(!data.toString().includes("|") && (regexButton.test(data.toString().trim()) || regexEncodeur.test(data.toString().trim()))){
      console.log(`Données reçues : ${data.toString().trim()}`);
      analyseYML("scripts/1/" + data.toString().trim() + ".yml", sendToSerialPort)
    }
  });

  currentPort.on('error', err => {
    console.error('Erreur du port série :', err.message);
    scheduleReconnect();
  });

  currentPort.on('close', () => {
    console.warn(`Port série fermé : ${portPath}`);
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
    console.log(`Tentative de reconnexion sur ${currentPortPath}...`);
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

function sendToSerialPort(message) {
  if (currentPort && currentPort.isOpen) {
    currentPort.write(message + '\n', err => {
      if (err) {
        return console.error('Erreur lors de l’envoi :', err.message);
      }
      console.log(`Message envoyé : ${message}`);
    });
  } else {
    console.warn('Impossible d’envoyer le message : port non ouvert');
  }
}

module.exports = {
  openSerialPort,
  closeSerialPort,
};
