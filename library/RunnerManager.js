const { execFile } = require('child_process');
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

const pythonPath = 'python3'; // ou 'python' selon ton système

async function analyseYML(filePath){
  const fileContents = fs.readFileSync(filePath, 'utf8');
  const data = yaml.load(fileContents);

  if(data.notification){
    console.log(data.name)
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
      default:
        break;
    }
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
      console.log(stdout);
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
