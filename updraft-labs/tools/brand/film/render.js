const { chromium } = require('playwright');
(async () => { const [, , page, out, W, H, fps, dur, step] = process.argv; const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +W, height: +H } }); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('file://' + page, { waitUntil: 'networkidle' }); await p.evaluate(() => window.ready); await p.waitForTimeout(500);
  const N = Math.round(+fps * +dur);
  for (let f = 0; f < N; f += (+step || 1)) { await p.evaluate(t => window.render(t), f / +fps); await p.screenshot({ path: `${out}/${String(f).padStart(4, '0')}.png` }); }
  await b.close(); console.log('frames', N); })();
