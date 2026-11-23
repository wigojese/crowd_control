// Renders Stage 13 scenario frames. Usage: node shot13.js ; then ffmpeg per scenario (see README in docs/BEHAVIOR_MATRIX.md)
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  for (const sc of fs.readdirSync('frames_svg')) {
    fs.mkdirSync('png_' + sc, { recursive: true });
    for (const f of fs.readdirSync('frames_svg/' + sc).filter(x => x.endsWith('.svg')).sort()) {
      await p.setContent(`<body style="margin:0;background:#000">${fs.readFileSync('frames_svg/' + sc + '/' + f, 'utf8')}</body>`);
      await p.screenshot({ path: 'png_' + sc + '/' + f.replace('.svg', '.png') });
    }
  }
  await b.close();
})();
