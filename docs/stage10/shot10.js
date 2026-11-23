// Renders the preview SVGs to PNG with the pre-installed Chromium (Playwright). Usage: node shot10.js
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const svg = n => fs.readFileSync(n + '.svg', 'utf8');
  async function shot(html, w, h, out, dpr = 2) {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: dpr });
    await p.setContent(`<body style="margin:0;background:#000">${html}</body>`);
    await p.waitForTimeout(150);
    await p.screenshot({ path: out });
    await p.close();
  }
  const five = ['s1_placement', 's2_run_AE_t120', 's3_run_nosign_t240', 's4_result_AE', 's5_result_nosign'];
  for (const n of five) await shot(svg(n), 390, 844, n + '.png');
  await shot(svg('v_highcontrast_t120'), 390, 844, 'v_highcontrast_t120.png');
  await shot(svg('v_result_AE_highcontrast'), 390, 844, 'v_result_AE_highcontrast.png');
  // no-colour comparison: the same pictures with a grayscale filter (an approximation of "colour off")
  await shot(`<div style="filter:grayscale(1)">${svg('s2_run_AE_t120')}</div>`, 390, 844, 'v_nocolor_t120.png');
  await shot(`<div style="filter:grayscale(1)">${svg('s4_result_AE')}</div>`, 390, 844, 'v_nocolor_result_AE.png');
  // narrow: the whole screen scaled to 320 px wide (not a re-laid-out 320x568 screen)
  await shot(`<div style="width:320px">${svg('s2_run_AE_t120').replace(/width="390" height="\d+"/, 'width="320"')}</div>`, 320, 693, 'v_narrow320_t120.png');
  await shot(`<div style="width:320px">${svg('s4_result_AE').replace(/width="390" height="\d+"/, 'width="320"')}</div>`, 320, 693, 'v_narrow320_result.png');
  // contact sheet
  const row = five.map(n => `<div style="margin:6px">${svg(n)}</div>`).join('');
  await shot(`<div style="display:flex;background:#222;width:${5 * 402}px">${row}</div>`, 5 * 402, 860, 'contact_five_states.png', 1);
  await b.close();
})();
