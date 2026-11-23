const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();
for(const f of process.argv.slice(2)){const p=await b.newPage({viewport:{width:1500,height:900},deviceScaleFactor:1.5});await p.goto('file://'+path.join(__dirname,f+'.html'));await p.waitForTimeout(500);await p.screenshot({path:path.join(__dirname,f+'.png'),fullPage:true});}
await b.close()})();
