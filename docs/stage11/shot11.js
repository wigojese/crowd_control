// Renders Stage 11 preview SVGs with the pre-installed Chromium. Usage: node shot11.js
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const page = async (w, h, dpr) => b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: dpr });
  const shot = async (p, svg, out) => { await p.setContent(`<body style="margin:0;background:#000">${svg}</body>`); await p.screenshot({ path: out }); };
  let p = await page(390, 844, 2);
  for (const n of ['zoom_city', 'zoom_district', 'zoom_street']) await shot(p, fs.readFileSync(n + '.svg', 'utf8'), n + '.png');
  await p.close();
  p = await page(320, 568, 2);
  await shot(p, fs.readFileSync('narrow320.svg', 'utf8'), 'narrow320.png');
  await p.close();
  p = await page(390, 844, 1);
  fs.mkdirSync('frames_png', { recursive: true });
  const files = fs.readdirSync('frames_svg').filter(f => f.endsWith('.svg')).sort();
  for (const f of files) await shot(p, fs.readFileSync('frames_svg/' + f, 'utf8'), 'frames_png/' + f.replace('.svg', '.png'));
  await p.close();
  const svgs = ['zoom_city', 'zoom_district', 'zoom_street'].map(n => `<div style="margin:6px">${fs.readFileSync(n + '.svg', 'utf8')}</div>`).join('');
  p = await page(3 * 402, 860, 1);
  await shot(p, `<div style="display:flex;background:#222;width:${3 * 402}px">${svgs}</div>`, 'contact_three_zooms.png');
  await b.close();
})();
