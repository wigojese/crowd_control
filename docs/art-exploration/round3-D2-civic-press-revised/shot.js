const {chromium}=require('playwright');const path=require('path');
const files=process.argv.slice(2);
(async()=>{const b=await chromium.launch();
for(const f of files){const p=await b.newPage({viewport:{width:1400,height:700},deviceScaleFactor:1.5});await p.goto('file://'+path.join(__dirname,f+'.html'));await p.waitForTimeout(400);await p.screenshot({path:path.join(__dirname,f+'.png'),fullPage:true});}
await b.close()})();
