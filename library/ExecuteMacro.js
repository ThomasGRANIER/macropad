const { execFile } = require('child_process');
const path = require('path');

function runPythonScript(filePath) {
  const pythonPath = 'python3'; // ou 'python' selon ton système
  const scriptPath = path.join(__dirname, 'Exec/Exec.py');

  execFile(pythonPath, [scriptPath, filePath], (error, stdout, stderr) => {
    if (error) {
      console.error('Erreur :', error);
      return;
    }
    if (stderr) {
      console.error('Stderr :', stderr);
    }
    console.log(stdout)
  });
}

module.exports = {
    runPythonScript,
  };
