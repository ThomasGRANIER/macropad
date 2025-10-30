import fs from 'fs';
import path from 'path';

const logFile = path.resolve('./logs/logs.txt');

// On réinitialise le fichier au démarrage
fs.writeFileSync(logFile, '', 'utf-8');

const logLevel = {
    info: "INFO",
    error: "ERROR",
    serial: "SERIAL"
}

function log(level, file, content){
    const now = new Date();
    const time = now.toLocaleString();
    const message = `${time} : ${level} : ${file} : ${content}\n`;

    console.log(message.trim());

    fs.appendFileSync(logFile, message, 'utf-8');
}

export {logLevel, log}
