// node render.js jobs.json  — each job: {src (file path) | html, w, h, out, transparent}
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2])); const b = await chromium.launch();
  for (const j of jobs) {
    const p = await b.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 1 });
    let html = j.html;
    if (!html) {
      const svg = fs.readFileSync(j.src, 'utf8').replace(/ width="[\d.]+" height="[\d.]+"/, ` style="width:${j.iw||j.w}px;height:${j.ih||j.h}px"`);
      html = `<html><body style="margin:0;background:transparent;display:grid;place-items:center;width:${j.w}px;height:${j.h}px">${svg}</body></html>`;
    }
    await p.setContent(html, { waitUntil: 'networkidle' }); await p.waitForTimeout(j.wait || 150);
    await p.screenshot({ path: j.out, omitBackground: !!j.transparent }); await p.close();
  }
  await b.close();
})();
