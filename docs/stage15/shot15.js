const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  let p = await b.newPage({ viewport: { width: 900, height: 420 }, deviceScaleFactor: 2 });
  await p.setContent(`<body style="margin:0">${fs.readFileSync('muted_timeline.svg', 'utf8')}</body>`);
  await p.screenshot({ path: 'muted_timeline.png' });
  await p.close();
  for (const id of ['paper_unfolds', 'outcome_pullback']) {
    const a = fs.readFileSync(`reduced_${id}_start.svg`, 'utf8'), z = fs.readFileSync(`reduced_${id}_end.svg`, 'utf8');
    fs.mkdirSync(`rm_${id}`, { recursive: true });
    p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
    const times = [0, 33, 66, 100, 133, 150, 150, 150, 150, 150, 150, 150, 150];
    for (let i = 0; i < times.length; i++) {
      const f = Math.min(1, times[i] / 150);
      await p.setContent(`<body style="margin:0;background:#000;position:relative;width:390px;height:844px"><div style="position:absolute;inset:0;opacity:${1 - f}">${a}</div><div style="position:absolute;inset:0;opacity:${f}">${z}</div></body>`);
      await p.screenshot({ path: `rm_${id}/f${String(i).padStart(3, '0')}.png` });
    }
    await p.close();
    const frames = [0, 2, 3, 5].map(i => `<img src="file://${path.resolve(`rm_${id}`)}/f${String(i).padStart(3, '0')}.png" width="260" style="margin:4px"/>`).join('');
    const top = `<img src="file://${path.resolve(`../stage12/${id}_sheet.png`)}" width="1560" style="margin:4px"/>`;
    const q = await b.newPage({ viewport: { width: 1580, height: 1260 }, deviceScaleFactor: 1 });
    await q.setContent(`<body style="margin:0;background:#222;color:#EFE3C8;font:13px Inter,sans-serif"><div style="padding:6px">NORMAL: ${id.replace('_', ' ')} (six moments)</div>${top}<div style="padding:6px">REDUCED MOTION: cut to the end state with a 150 ms crossfade (frames at 0, 66, 100 and 150 ms)</div><div style="display:flex">${frames}</div></body>`);
    await q.waitForTimeout(300);
    await q.screenshot({ path: `reduced_motion_${id}.png` });
    await q.close();
  }
  await b.close();
})();
