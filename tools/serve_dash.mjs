// serve_dash.mjs — Codex-Bulut-Backtests dashboard sunucusu
// Kullanim: node tools/serve_dash.mjs  ->  http://localhost:8125/
import { createServer } from 'node:http';
import { createReadStream } from 'node:fs';
import { readFile, stat } from 'node:fs/promises';
import { gzipSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { dirname, extname, join, normalize, sep } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DASH = join(ROOT, 'dashboard');
const DATA = join(DASH, 'data');
const PORT = 8125;

const ROUTES = {
  '/': join(DASH, 'dashboard_pro.html'),
  '/pro': join(DASH, 'dashboard_pro.html'),
  '/eski': join(DASH, 'index.html'),
  '/tara': join(DASH, 'scan_pro.html'),
  '/scan': join(DASH, 'scan_pro.html'),
};
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
};

const htmlCache = new Map();
async function loadHtml(file) {
  if (!htmlCache.has(file)) {
    const raw = await readFile(file);
    htmlCache.set(file, { raw, gz: gzipSync(raw, { level: 6 }), mime: MIME[extname(file).toLowerCase()] });
  }
  return htmlCache.get(file);
}

function safeDataPath(url) {
  const rel = decodeURIComponent(url.slice('/data/'.length));
  const file = normalize(join(DATA, rel));
  if (!file.startsWith(DATA + sep)) return null;
  return file;
}

createServer(async (req, res) => {
  const url = (req.url || '/').split('?')[0];

  if (url.startsWith('/data/')) {
    const file = safeDataPath(url);
    if (!file) {
      res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Yasak yol');
      return;
    }
    try {
      const st = await stat(file);
      res.writeHead(200, {
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Length': st.size,
        'Cache-Control': 'no-cache',
      });
      createReadStream(file).pipe(res);
    } catch {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Veri bulunamadi: ' + url);
    }
    return;
  }

  const file = ROUTES[url];
  if (!file) {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Bulunamadi: ' + url + '\nMevcut: ' + Object.keys(ROUTES).join(', ') + ', /data/*');
    return;
  }
  try {
    const entry = await loadHtml(file);
    const ae = req.headers['accept-encoding'] || '';
    if (ae.includes('gzip')) {
      res.writeHead(200, { 'Content-Type': entry.mime, 'Content-Encoding': 'gzip', 'Content-Length': entry.gz.length, 'Cache-Control': 'no-cache' });
      res.end(entry.gz);
    } else {
      res.writeHead(200, { 'Content-Type': entry.mime, 'Content-Length': entry.raw.length, 'Cache-Control': 'no-cache' });
      res.end(entry.raw);
    }
  } catch (e) {
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Hata: ' + e.message);
  }
}).listen(PORT, () => console.log('[serve] http://localhost:' + PORT + ' hazir · rotalar: ' + Object.keys(ROUTES).join(', ') + ', /data/*'));
