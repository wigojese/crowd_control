const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 620 }, deviceScaleFactor: 2 });
  for (const f of fs.readdirSync('.').filter(x => x.startsWith('route_') && x.endsWith('.svg'))) {
    await p.setContent(`<body style="margin:0;background:#000">${fs.readFileSync(f, 'utf8')}</body>`);
    await p.screenshot({ path: f.replace('.svg', '.png') });
  }
  const row = fs.readdirSync('.').filter(x => x.startsWith('route_') && x.endsWith('.svg')).sort().map(f => `<div style="margin:6px">${fs.readFileSync(f, 'utf8')}</div>`).join('');
  const q = await b.newPage({ viewport: { width: 3 * 402, height: 632 }, deviceScaleFactor: 1 });
  await q.setContent(`<body style="margin:0;background:#222"><div style="display:flex">${row}</div></body>`);
  await q.screenshot({ path: 'routes_contact.png' });
  await b.close();
})();
