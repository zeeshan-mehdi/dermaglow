// node caps.js <base url> <out dir> — site captures used by the film
const { chromium } = require('playwright');
(async () => { const [, , base, out] = process.argv; const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto(base + '/', { waitUntil: 'networkidle' });
  await p.addStyleTag({ content: 'html{scroll-behavior:auto!important} body::after{display:none}' });
  await p.waitForTimeout(2600); await p.mouse.move(1500, 420); await p.waitForTimeout(900);
  await p.screenshot({ path: out + '/hero.png' });
  await p.addStyleTag({ content: '.nav{display:none!important}' });
  await p.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')));
  await p.evaluate(() => { const e = document.querySelector('#engage'); window.scrollTo(0, e.getBoundingClientRect().top + scrollY + 40); });
  await p.mouse.move(5, 5); await p.waitForTimeout(1200); await p.screenshot({ path: out + '/tickets.png' });
  await b.close(); })();
