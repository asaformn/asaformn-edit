// Kullanim:
//  node render.mjs --still 9.8 --out x.png [--alpha] [--sahne sahneler/uyku-ornek.json]
//  node render.mjs --clip --out x.mp4|x.mov [--alpha]   (.mov + --alpha = DaVinci icin PNG-MOV) [--from 0 --to 2] [--fps 60]
import { chromium } from 'playwright-core';
import http from 'http'; import fs from 'fs'; import path from 'path'; import { spawn } from 'child_process'; import { fileURLToPath } from 'url';
const A = process.argv.slice(2), arg = (k, d) => { const i = A.indexOf('--' + k); return i < 0 ? d : (A[i + 1] && !A[i + 1].startsWith('--') ? A[i + 1] : true) };
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const sahne = arg('sahne', 'sahneler/uyku-ornek.json'), alpha = !!arg('alpha', false), out = arg('out'), fps = +arg('fps', 60);
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.ttf': 'font/ttf' };
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end() } else { r.writeHead(200, { 'content-type': mime[path.extname(f)] || 'application/octet-stream' }); r.end(d) } }) }).listen(0);
const port = srv.address().port;
const br = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const pg = await br.newPage({ viewport: { width: 1920, height: 1080 } });
pg.on('console', m => m.type() === 'error' && console.error('[page]', m.text())); pg.on('pageerror', e => console.error('[pageerror]', e.message));
await pg.goto(`http://localhost:${port}/motor/asaformn-edit/index.html?sahne=${sahne}${alpha ? '&alpha=1' : ''}`);
await pg.waitForFunction('window.READY===true', null, { timeout: 30000 });
const err = await pg.evaluate('window.ERR'); if (err) throw new Error(err);
const frame = t => pg.evaluate(t => { window.render(t); return document.getElementById('c').toDataURL('image/png').slice(22) }, t);
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
if (arg('still', null) !== null) { fs.writeFileSync(out, Buffer.from(await frame(+arg('still')), 'base64')) }
else if (arg('clip', false)) {
  const dur = await pg.evaluate('window.DUR'), t0 = +arg('from', 0), t1 = +arg('to', dur), n = Math.round((t1 - t0) * fps);
  const mov = out.endsWith('.mov');
  // .mov = PNG kodekli MOV (alfa). Resolve 21.1.2 ffmpeg'in ProRes 4444 alfasini yok sayiyor; PNG-MOV ve qtrle calisiyor (25 Kasim testi).
  const enc = mov ? ['-c:v', 'png', '-pix_fmt', 'rgba'] : ['-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p'];
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-', ...enc, '-r', String(fps), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) { if (!ff.stdin.write(Buffer.from(await frame(t0 + i / fps), 'base64'))) await new Promise(r => ff.stdin.once('drain', r)) }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await br.close(); srv.close();
