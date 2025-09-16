// Simple logging middleware for development server
const fs = require('fs');
const path = require('path');

// Create frontend log file in project root
const logFile = path.join(__dirname, '..', '..', 'frontend.log');

// Ensure log file exists
if (!fs.existsSync(logFile)) {
  fs.writeFileSync(logFile, `Frontend logging started at ${new Date().toISOString()}\n`, 'utf8');
}

// Function to write log entry to file
function writeLog(entry) {
  const logLine = `${entry.timestamp} [${entry.level}] ${entry.message}${entry.data ? ' | ' + JSON.stringify(entry.data) : ''}\n`;
  fs.appendFileSync(logFile, logLine, 'utf8');
}

module.exports = { writeLog };