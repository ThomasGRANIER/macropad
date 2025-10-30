const { execFile } = require('child_process');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');
const { logLevel, log } = require('./logs')

let fileLog = "RunnerManager"

// Charger la config
const configPath = path.join(__dirname, '../conf.json');
let config;

try {
  const rawData = fs.readFileSync(configPath);
  config = JSON.parse(rawData);
  log(logLevel.info,fileLog,`Configuration chargée : ${JSON.stringify(config)}`);
} catch (err) {
  console.error("Erreur de lecture du fichier de configuration :", err);
}

const pythonPath = config.pythonCmd; // ou 'python' selon ton système

async function analyseYML(filePath, sendToSerialPort){
  const fileContents = fs.readFileSync(filePath, 'utf8');
  const data = yaml.load(fileContents);
  if(checkYmlCompliance(data))
  {
    if(data.notification){
      log(logLevel.serial,fileLog,`Nom du script : ${data.name}`);
      sendToSerialPort(data.name)
    }

    for (let i = 0; i < data.actions.length; i++) {
      switch (data.actions[i].type) {
        case "key":
          await runnerKey(data.actions[i].value)
          break;
        case "text":
          await runnerText(data.actions[i].value)
          break;
        case "delay":
          await runnerDelay(data.actions[i].value)
          break;
        case "cmd":
          await runnerCmd(data.actions[i].value)
          break;
        default:
          break;
      }
    }
  }
  else{
    log(logLevel.error,fileLog,"Yml file not compliance")
  }
}

function checkYmlCompliance(content){
  if(content != undefined)
  {
    if(!('name' in content)){
      log(logLevel.error,fileLog,"'name' not found")
      return false
    }

    if(!('notification' in content)){
      log(logLevel.error,fileLog,"'notification' not found")
      return false
    }

    if(!('actions' in content)){
      log(logLevel.error,fileLog,"'actions' not found")
      return false
    }

    for (let i = 0; i < content.actions.length; i++) {
      if(!('type' in content.actions[i])){
        log(logLevel.error,fileLog,"'type' not found")
        return false
      }

      if(!('value' in content.actions[i])){
        log(logLevel.error,fileLog,"'value' not found")
        return false
      }
    }

    return true
  }
  else{
    log(logLevel.error,fileLog,"Yml empty")
    return false
  }

}

async function runnerKey(entry){
  const scriptPath = path.join(__dirname, 'Runners/RunnerKey.py');
  await runPythonScript(scriptPath, entry)
}

async function runnerText(entry){
  const scriptPath = path.join(__dirname, 'Runners/RunnerText.py');
  await runPythonScript(scriptPath, entry)
}

async function runnerCmd(entry){
  const scriptPath = path.join(__dirname, 'Runners/RunnerCmd.py');
  await runPythonScript(scriptPath, entry)
}

async function runnerDelay(entry){
  await sleep(entry)
}

function runPythonScript(scriptPath, entry) {
  return new Promise((resolve, reject) => {
    execFile(pythonPath, [scriptPath, entry], (error, stdout, stderr) => {
      if (error) {
        console.error('Erreur :', error);
        return reject(error);
      }
      if (stderr) {
        console.error('Stderr :', stderr);
      }
      resolve(stdout);
    });
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = {
    analyseYML,
  };
