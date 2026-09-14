#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

const frontendDir = 'c:\\Users\\i2383\\Downloads\\MANGANEX_AI_READY_VS_CODE\\frontend';
process.chdir(frontendDir);

console.log('Starting Vite dev server...');

const vite = spawn('node', [
  path.join(frontendDir, 'node_modules', '.bin', 'vite'),
  '--host', '0.0.0.0',
  '--port', '5173'
], {
  stdio: 'inherit',
  shell: true
});

vite.on('close', (code) => {
  console.log(`Dev server exited with code ${code}`);
  process.exit(code);
});
