// Renders Stage 12 frames and one contact sheet per transition. Usage: node shot12.js ; then ffmpeg (see make_videos.sh)
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  for (const id of fs.readdirSync('.').filter(d => fs.existsSync(d + '/frames'))) {
    fs.mkdirSync(id + '/png', { recursive: true });
    const files = fs.readdirSync(id + '/frames').filter(f => f.endsWith('.svg')).sort();
    for (const f of files) {
      await p.setContent(`<body style="margin:0;background:#000">${fs.readFileSync(id + '/frames/' + f, 'utf8')}</body>`);
      await p.screenshot({ path: id + '/png/' + f.replace('.svg', '.png') });
    }
    const idx = JSON.parse(fs.readFileSync(id + '/sheet.json'));
    const row = idx.map(i => `<div style="margin:4px">${fs.readFileSync(id + '/frames/f' + String(i).padStart(3, '0') + '.svg', 'utf8').replace('width="390" height="844"', 'width="260" height="563"')}</div>`).join('');
    const q = await b.newPage({ viewport: { width: 6 * 268, height: 575 }, deviceScaleFactor: 1 });
    await q.setContent(`<body style="margin:0;background:#222"><div style="display:flex">${row}</div></body>`);
    await q.screenshot({ path: id + '_sheet.png' });
    await q.close();
  }
  await b.close();
})();
