const fs=require('fs');const g=require('./gen2x.js');const I=g.internals;const {C,F}=I;
const embed=(svg,x,y,w,h)=>svg.replace(/<svg [^>]*>/,`<svg x="${x}" y="${y}" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">`);
// ---------- frame with system insets ----------
function frame(W,H,top,bottom,inner,tag){const hc=H-top-bottom;
 let s=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="${C.bright}"/>`;
 s+=embed(inner,0,top,W,hc);
 s+=`<rect width="${W}" height="${top}" fill="${C.bright}"/><text x="${W<340?14:24}" y="${top-8}" font-family="${F.ui}" font-size="13" font-weight="700" fill="${C.ink}">9:41</text><rect x="${W-46}" y="${top-17}" width="24" height="11" rx="2.5" fill="none" stroke="${C.ink}" stroke-width="1.4"/><rect x="${W-44}" y="${top-15}" width="17" height="7" fill="${C.ink}"/>`;
 if(bottom)s+=`<rect y="${H-bottom}" width="${W}" height="${bottom}" fill="${C.bright}"/><rect x="${W/2-67}" y="${H-Math.min(10,bottom/2+3)}" width="134" height="5" rx="2.5" fill="${C.ink}"/>`;
 return s+'</svg>'}
// ---------- screens on R1 (sockets A and B) ----------
function base(W,Hc,uid){const l=I.L(W,Hc);const id='s'+uid;const mapBottom=Hc-l.dockH;const mh=mapBottom-l.mapTop-4;const T=I.fit(l,l.mapTop,mh);return{l,id,mapBottom,mh,T,W,Hc}}
const bg=(b,defs)=>`<defs>${I.defs(b.id)}${I.clip(b.id,b.l,b.l.mapTop,b.mh)}${defs||''}</defs><rect width="${b.W}" height="${b.Hc}" fill="${C.stock}"/><rect width="${b.W}" height="${b.Hc}" fill="url(#gr${b.id})"/><rect width="${b.W}" height="${b.Hc}" filter="url(#tooth${b.id})" opacity=".5"/>`;
const svgWrap=(b,body)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${b.W}" height="${b.Hc}" viewBox="0 0 ${b.W} ${b.Hc}">${body}</svg>`;
function chev(T,e,ts,col){return ts.map(t=>{const p=I.S(T,I.pt(e,t));return`<path d="M-4,-5 L3,0 L-4,5" transform="translate(${p[0].toFixed(1)},${p[1].toFixed(1)}) rotate(${I.ang(e,t).toFixed(0)})" fill="none" stroke="${col}" stroke-width="2.8" stroke-linejoin="round"/>`}).join('')}
function planScreen(W,Hc,uid,o={}){const b=base(W,Hc,uid);const{l,T}=b;const cp=l.compact;let s=bg(b)+I.hud(l,0,'0:32',0)+I.mapGroup(l,b.id,T,{roadCol:C.ink});
 const pa=I.S(T,I.N.A),pb=I.S(T,I.N.B);
 if(o.preview!==false)s+=chev(T,'AB',[.3,.6],C.mustD)+chev(T,'AC',[.3,.6],C.mustD);
 s+=I.crowd(I.WAIT,T)+I.sealsAt(T,l,{});
 s+=I.socketRing(pb[0],pb[1],false)+I.socketRing(pa[0],pa[1],o.sign!=='none'&&o.sign!=='dock'&&o.sign!==undefined?true:false);
 if(o.sign==='lift')s+=I.sign(pa[0],pa[1]-2,'E','lift');
 s+=I.labelsMain(T,l,[['A',0,-44],['B',-4,-44],['F',0,42],['G',0,42]]);
 s+=I.dock(l,{sign:o.dockSign||'none',l1:o.l1||'Place the sign',l2:o.l2||(cp?'Drag to a ringed spot':'Drag it to a ringed junction'),btn:'Start',bk:'disabled'});
 return svgWrap(b,s)}
function runScreen(W,Hc,uid,o={}){const b=base(W,Hc,uid);const{l,T}=b;const cp=l.compact;let s=bg(b)+I.hud(l,9,'0:18',14/32)+I.mapGroup(l,b.id,T,{roadCol:C.ink,hot:['BD'],trace:{AB:3.2,AC:3.6,DF:2.8,CE:2.4}})+I.crowd(I.RUN,T);
 const pa=I.S(T,I.N.A),pb=I.S(T,I.N.B);
 s+=I.sealsAt(T,l,{cnt:{F:[3,12],G:[2,8]}})+I.socketRing(pb[0],pb[1],false);
 s+=I.sign(pa[0],pa[1]-2,'E','placed');
 if(o.lock){const a=.62*2*Math.PI,r=30,x2=pa[0]+Math.sin(a)*r,y2=pa[1]-2-Math.cos(a)*r;s+=`<circle cx="${pa[0]}" cy="${pa[1]-2}" r="${r}" fill="none" stroke="${C.stone}" stroke-width="3"/><path d="M${pa[0]},${pa[1]-2-r} A${r},${r} 0 ${a>Math.PI?1:0} 1 ${x2.toFixed(1)},${y2.toFixed(1)}" fill="none" stroke="${C.ox}" stroke-width="3.4" stroke-linecap="round"/>`}
 s+=I.labelsMain(T,l,[['A',-4,-48],['B',-4,-48],['F',0,42],['G',0,42]]);
 s+=I.dock(l,{sign:'none',l1:o.l1||'Sign locked 3.1 s',l2:o.l2||'Then tap or drag it',btn:o.btn||'Pause',bk:'secondary'});
 return svgWrap(b,s)}
// ---------- overlays ----------
function overlayPause(W,Hc){const l=I.L(W,Hc);const y=l.mapTop;const cw=Math.min(W-60,300),cx=(W-cw)/2,cy=Hc*0.3;
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${Hc}"><rect x="0" y="${y}" width="${W}" height="${Hc-y}" fill="${C.stock}" opacity=".82"/><rect x="${cx+3}" y="${cy+3}" width="${cw}" height="236" fill="${C.stone}"/><rect x="${cx}" y="${cy}" width="${cw}" height="236" fill="${C.bright}" stroke="${C.ink}" stroke-width="2.4"/><text x="${cx+20}" y="${cy+42}" font-family="${F.disp}" font-size="26" font-weight="700" fill="${C.ink}">Paused</text>${I.routeLine(cx+20,cy+54,120)}<text x="${cx+20}" y="${cy+82}" font-family="${F.ui}" font-size="13.5" fill="${C.ink}">Clock and lock are stopped.</text><text x="${cx+20}" y="${cy+100}" font-family="${F.ui}" font-size="13.5" fill="${C.ink}">The sign can't be changed while paused.</text>${I.btn(cx+20,cy+118,cw-40,52,'Resume','primary')}${I.btn(cx+20,cy+180,(cw-52)/2,48,'Restart','secondary')}${I.btn(cx+32+(cw-52)/2,cy+180,(cw-52)/2,48,'Home','secondary')}</svg>`}
function overlayIntro(W,Hc){const l=I.L(W,Hc);const y=Hc-l.dockH;const cp=l.compact;
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${Hc}"><rect x="0" y="${y}" width="${W}" height="${l.dockH}" fill="${C.bright}"/><rect x="0" y="${y}" width="${W}" height="2.4" fill="${C.ink}"/><text x="22" y="${y+40}" font-family="${F.disp}" font-size="${cp?14:15.5}" font-weight="700" fill="${C.ink}">One sign. A hundred decisions.</text><text x="22" y="${y+64}" font-family="${F.ui}" font-size="14" fill="${C.ink}">Deliver 18 of 20 before 0:32.</text>${I.btn(W-122,y+30,104,48,'Skip','secondary')}</svg>`}
function overlayRetry(W,Hc,uid){const b=base(W,Hc,'r'+uid);return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${Hc}"><defs>${I.defs(b.id)}</defs><g opacity=".3">${I.ribbons(b.T,b.id,.7)}</g>${I.tag(16,b.l.mapTop+30,'Last run, fading')}</svg>`}
function overlayExplore(W,Hc){const l=I.L(W,Hc);const x=W-40,y0=l.mapTop+36,y1=Hc-l.dockH-60;const py=y0+(y1-y0)*.35;
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${Hc}"><line x1="${x}" y1="${y0}" x2="${x}" y2="${y1}" stroke="${C.stone}" stroke-width="4" stroke-linecap="round"/><rect x="${x-14}" y="${py-24}" width="28" height="48" rx="3" fill="${C.ink}"/><line x1="${x-6}" y1="${py-6}" x2="${x+6}" y2="${py-6}" stroke="${C.bright}" stroke-width="2"/><line x1="${x-6}" y1="${py+6}" x2="${x+6}" y2="${py+6}" stroke="${C.bright}" stroke-width="2"/>${I.btn((W-190)/2,Hc-l.dockH-60,190,46,'Return to sign','secondary')}</svg>`}
const stack=(a,b)=>a.replace(/<\/svg>\s*$/,'')+b.replace(/<svg [^>]*>/,'<g>').replace(/<\/svg>\s*$/,'</g>')+'</svg>';
// ---------- states sheet (390 x 844 frames at 0.52) ----------
const W=390,H=844,TOP=47,BOT=34,HC=H-TOP-BOT;
const states=[
 ['HOME','Tap Play. Nothing else is tappable.',frame(W,H,TOP,BOT,g.screen('title',W,HC,'h'))],
 ['INTRO','Plays once, then shows the map. Tap Skip to cut it.',frame(W,H,TOP,BOT,stack(planScreen(W,HC,'i',{sign:'none',preview:false}),overlayIntro(W,HC)))],
 ['PLACEMENT','Drag the sign to a ring, or tap a ring. Tap the sign to turn it. Start stays dim until it is placed.',frame(W,H,TOP,BOT,planScreen(W,HC,'p',{sign:'lift'}))],
 ['RUNNING','Tap the sign to turn it, or drag it to the other ring. 4 s rest between actions.',frame(W,H,TOP,BOT,runScreen(W,HC,'u',{lock:true}))],
 ['PAUSED','Resume, Restart or Home. The sign cannot be touched.',frame(W,H,TOP,BOT,stack(runScreen(W,HC,'q',{lock:true,btn:'Resume'}),overlayPause(W,HC)))],
 ['RESULT','Try again is the big button. Inspect decision is second.',frame(W,H,TOP,BOT,g.screen('result',W,HC,'z'))],
 ['RETRY','Last run fades to ghost ink in 320 ms; sign returns to the tray; no score carried over.',frame(W,H,TOP,BOT,stack(planScreen(W,HC,'y',{sign:'none',dockSign:'dock',l1:'Place the sign',preview:false}),overlayRetry(W,HC,'y')))],
 ['EXPLORE','Optional. Drag the rail or two fingers to look around. One tap returns to the sign.',frame(W,H,TOP,BOT,stack(runScreen(W,HC,'e',{lock:false,l1:'Free look',l2:'Round keeps running',btn:'Pause'}),overlayExplore(W,HC)))],
];
const sc=.54;let st=`<html><body style="margin:0;background:#D9CAB0;font-family:Inter;color:${C.ink}"><div style="padding:28px 34px 22px;width:${4*(Math.round(W*sc)+20)}px"><div style="font:700 30px 'Bitstream Charter',serif">Stage 04: the eight screen states</div><div style="font-size:14.5px;margin:6px 0 18px;max-width:1000px">390×844 with system insets drawn in (47 top, 34 bottom, typical iPhone values; the game must read them at runtime). Level R1: sockets at North Gate and Canal Turn, goal 18 of 20. All numbers are mock data.</div><div style="display:grid;grid-template-columns:repeat(4,auto);gap:22px 20px">`;
states.forEach(([n,cap,svg])=>{st+=`<div style="width:${Math.round(W*sc)}px"><div style="width:${Math.round(W*sc)}px;height:${Math.round(H*sc)}px;overflow:hidden;box-shadow:0 8px 22px rgba(30,26,23,.3)"><div style="transform:scale(${sc});transform-origin:0 0;width:${W}px;height:${H}px">${svg}</div></div><div style="margin-top:8px;font:700 16px 'Bitstream Charter',serif">${n}</div><div style="font-size:12.5px;line-height:1.35;margin-top:2px">${cap}</div></div>`});
fs.writeFileSync('d4-states.html',st+'</div></div></body></html>');
// ---------- hit maps ----------
function hitmap(Wd,Hd,top,bottom,uid,mode){const hc=Hd-top-bottom;const l=I.L(Wd,hc);
 const inner=mode==='place'?planScreen(Wd,hc,uid,{sign:'lift'}):runScreen(Wd,hc,uid,{lock:true});
 const base0=frame(Wd,Hd,top,bottom,inner);
 const b=base(Wd,hc,uid);const T=b.T;const P=n=>{const p=I.S(T,I.N[n]);return[p[0],p[1]+top]};
 const A=P('A'),B=P('B');const y=hc-l.dockH;const cx=l.compact?44:50,cy=y+l.dockH/2+2+top;const bw=l.compact?92:104;const btnR={x:Wd-bw-18,y:cy-24,w:bw,h:48};
 const edge=24;let o='';const lab=(n,x,yy)=>`<g><circle cx="${x}" cy="${yy}" r="10" fill="${C.ink}"/><text x="${x}" y="${yy+4.5}" text-anchor="middle" font-family="${F.num}" font-size="12" font-weight="800" fill="${C.bright}">${n}</text></g>`;
 const R=(x,yy,w,h,col,fill,dash)=>`<rect x="${x}" y="${yy}" width="${w}" height="${h}" fill="${fill||'none'}" stroke="${col}" stroke-width="2" ${dash?'stroke-dasharray="6 4"':''}/>`;
 o+=`<defs><pattern id="hx${uid}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3" height="6" fill="${C.ox}" opacity=".35"/></pattern></defs>`;
 o+=R(0,0,Wd,top,C.ink,`url(#hx${uid})`)+lab(1,Wd-18,16);
 o+=R(0,top+(l.compact?0:0),Wd,l.mapTop,C.stone,C.stone+'33')+lab(2,16,top+l.mapTop-14);
 o+=R(0,top+l.mapTop,edge,hc-l.mapTop-l.dockH,C.ox,`url(#hx${uid})`)+R(Wd-edge,top+l.mapTop,edge,hc-l.mapTop-l.dockH,C.ox,`url(#hx${uid})`)+lab(3,12,top+l.mapTop+40)+lab(3,Wd-12,top+l.mapTop+40);
 o+=R(edge,top+l.mapTop,Wd-2*edge,hc-l.mapTop-l.dockH,C.olive,C.olive+'14',true)+lab(4,Wd/2,top+l.mapTop+hc*0.5);
 [[A,'A'],[B,'B']].forEach(([p,n])=>{o+=`<circle cx="${p[0]}" cy="${p[1]}" r="28" fill="${C.ver}22" stroke="${C.ver}" stroke-width="2"/>`});
 o+=lab(5,A[0]+34,A[1]-26)+lab(5,B[0]+34,B[1]-26);
 o+=R(8,y+top+10,Wd-16,l.dockH-20,C.mustD,C.must+'18',true)+lab(6,18,y+top+22);
 o+=`<circle cx="${cx}" cy="${cy-4}" r="28" fill="none" stroke="${C.ver}" stroke-width="2"/>`+lab(7,cx+30,cy-30);
 o+=R(btnR.x,btnR.y,btnR.w,btnR.h,C.ink,C.ink+'22')+lab(8,btnR.x-2,btnR.y-2);
 o+=R(0,Hd-bottom,Wd,bottom,C.ink,`url(#hx${uid})`)+lab(9,Wd-18,Hd-bottom/2);
 if(mode==='run'){const r=34;o+=`<circle cx="${A[0]}" cy="${A[1]-2}" r="${r}" fill="none" stroke="${C.ox}" stroke-width="1.6" stroke-dasharray="3 3"/>`;}
 return `<div style="position:relative;width:${Wd}px;height:${Hd}px;box-shadow:0 8px 22px rgba(30,26,23,.3)">${base0}<svg xmlns="http://www.w3.org/2000/svg" width="${Wd}" height="${Hd}" style="position:absolute;left:0;top:0">${o}</svg></div>`}
const legend=(Wd,compact)=>{const tops=compact?24:47,bots=compact?16:34;const rows=[
 [1,'System inset, top',`${tops} px`,'No controls. Clock and status live here.'],
 [2,'HUD band',`${compact?54:112} px`,'Read-only. No gesture starts here.'],
 [3,'Edge reserve, each side','24 px','No drag or tap starts here, so the OS back swipe wins. Measure on device.'],
 [4,'Map zone','rest','One finger pans, two fingers pinch. A drag over 12 px is a pan.'],
 [5,'Socket and sign hit area','56×56 px','Drawn ring is 44 px. The hit area is larger than it looks.'],
 [6,'Control dock',`${compact?104:106} px`,'Taps only. Sits above the bottom inset.'],
 [7,'Sign tray','56×56 px','Drag starts after 8 px.'],
 [8,'Start / Pause',`${compact?92:104}×48 px`,'Above the 44 px minimum.'],
 [9,'System inset, bottom',`${bots} px`,'Home indicator. Swipes up here belong to the OS.']];
 return `<div style="width:${compact?330:400}px;font-size:13px"><div style="font:700 17px 'Bitstream Charter',serif;margin-bottom:8px">Hit regions (logical px)</div>${rows.map(r=>`<div style="display:flex;gap:9px;margin:0 0 9px"><div style="flex:none;width:21px;height:21px;border-radius:50%;background:${C.ink};color:${C.bright};font:800 12px 'JetBrains Mono';display:flex;align-items:center;justify-content:center">${r[0]}</div><div><b>${r[1]}</b> <span style="font-family:'JetBrains Mono';font-size:12px">${r[2]}</span><br><span style="color:${C.soft}">${r[3]}</span></div></div>`).join('')}<div style="margin-top:10px;color:${C.soft};line-height:1.4">Inset sizes shown are typical values. The game reads the real ones from the OS at start-up and on rotation.</div></div>`};
function hitPage(Wd,Hd,top,bottom,name,compact){return `<html><body style="margin:0;background:#D9CAB0;font-family:Inter;color:${C.ink}"><div style="padding:28px 34px;display:inline-block"><div style="font:700 30px 'Bitstream Charter',serif">${name}</div><div style="font-size:14.5px;margin:6px 0 18px;max-width:1100px">Left: PLACEMENT, sign being dragged to a ring. Middle: RUNNING, sign locked for 3.1 s. Colours: oxblood hatching is OS-owned or reserved, olive dashes the map, vermilion the sign targets, mustard the dock. Mock numbers.</div><div style="display:flex;gap:26px;align-items:flex-start">${hitmap(Wd,Hd,top,bottom,'a','place')}${hitmap(Wd,Hd,top,bottom,'b','run')}${legend(Wd,compact)}</div></div></body></html>`}
fs.writeFileSync('d4-hit390.html',hitPage(390,844,47,34,'Stage 04: hit regions at 390×844',false));
fs.writeFileSync('d4-hit320.html',hitPage(320,568,24,16,'Stage 04: hit regions at 320×568, laid out for the small phone',true));
// ---------- arbitration diagram ----------
const NW=200,NH=60;
const nodes={IDLE:[30,300,'IDLE','finger up, nothing owned'],UI:[30,90,'UI_PRESS','a button: acts once'],DD:[330,60,'DOCK_DRAG','down on the tray sign'],SP:[330,270,'SIGN_PENDING','down on sign or ring'],MP:[330,520,'MAP_PENDING','down on blank map'],SD:[680,60,'SIGN_DRAG','sign follows the finger'],ST:[680,170,'SIGN_TAP','turn 90 degrees if allowed'],SI:[680,280,'SIGN_INSPECT','callout, no turn'],LR:[680,390,'LOCK_REJECT','shake, no pan, no pickup'],PAN:[680,500,'PAN','map follows the finger'],PI:[680,630,'PINCH','two fingers own the map']};
const col={UI:C.mustD,DD:C.ver,SD:C.ver,ST:C.ver,SI:C.ver,LR:C.ox,PAN:C.olive,PI:C.olive};
let ds=`<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="900" viewBox="0 0 1120 900"><defs><marker id="ah" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M1,1 L9,5 L1,9" fill="none" stroke="${C.ink}" stroke-width="1.6"/></marker></defs><rect width="1120" height="900" fill="${C.stock}"/>`;
const pt_=(k,side,f=.5)=>{const[x,y]=nodes[k];return side==='r'?[x+NW,y+NH*f]:side==='l'?[x,y+NH*f]:side==='t'?[x+NW*f,y]:[x+NW*f,y+NH]};
const line=(a,as,af,b,bs,bf,t,tf=.55)=>{const p=pt_(a,as,af),q=pt_(b,bs,bf);const mx=p[0]+(q[0]-p[0])*tf,my=p[1]+(q[1]-p[1])*tf;return`<line x1="${p[0]}" y1="${p[1]}" x2="${q[0]}" y2="${q[1]}" stroke="${C.ink}" stroke-width="1.6" marker-end="url(#ah)"/><text x="${mx}" y="${my-6}" text-anchor="middle" font-family="${F.ui}" font-size="12.5" fill="${C.ink}" paint-order="stroke" stroke="${C.stock}" stroke-width="5" stroke-linejoin="round">${t}</text>`};
ds+=line('IDLE','t',.5,'UI','b',.5,'down on a button',.5);
ds+=line('IDLE','r',.2,'DD','l',.5,'down on the tray sign',.5)+line('IDLE','r',.5,'SP','l',.5,'down on sign or ring',.72)+line('IDLE','r',.85,'MP','l',.5,'down on blank map',.5);
ds+=line('DD','r',.5,'SD','l',.5,'move over 8 px',.5);
ds+=line('SP','r',.2,'SD','l',.75,'drag over 8 px',.55)+line('SP','r',.4,'ST','l',.5,'tap: up within 220 ms',.55)+line('SP','r',.6,'SI','l',.5,'hold over 420 ms',.55)+line('SP','r',.85,'LR','l',.5,'drag while locked',.55);
ds+=line('MP','r',.35,'PAN','l',.5,'move over 12 px',.55)+line('MP','r',.8,'PI','l',.5,'second finger',.5);
Object.entries(nodes).forEach(([k,[x,y,n,sub]])=>{const c=col[k]||C.ink;ds+=`<rect x="${x+3}" y="${y+3}" width="${NW}" height="${NH}" fill="${C.stone}"/><rect x="${x}" y="${y}" width="${NW}" height="${NH}" fill="${C.bright}" stroke="${c}" stroke-width="2.4"/><text x="${x+12}" y="${y+25}" font-family="${F.num}" font-size="14.5" font-weight="800" fill="${C.ink}">${n}</text><text x="${x+12}" y="${y+45}" font-family="${F.ui}" font-size="12.5" fill="${C.soft}">${sub}</text>`});
ds+=`<text x="30" y="40" font-family="${F.disp}" font-size="28" font-weight="700" fill="${C.ink}">Who owns a touch</text>`;
ds+=`<rect x="30" y="730" width="760" height="150" fill="${C.bright}" stroke="${C.ink}" stroke-width="1.6"/><text x="46" y="758" font-family="${F.ui}" font-size="14" font-weight="700" fill="${C.ink}">Rules</text>`;
['One owner per finger, from touch-down to touch-up.','Only a second finger can take over (PINCH). It cancels the first action cleanly.','A cancel never leaves the sign half-moved: it snaps back.','A locked sign swallows the drag (LOCK_REJECT), so it never turns into a pan.','Thresholds are starting values to tune on a real phone.'].forEach((t,i)=>{ds+=`<text x="46" y="${782+i*21}" font-family="${F.ui}" font-size="13.5" fill="${C.ink}">${t}</text>`});
ds+='</svg>';
fs.writeFileSync('d4-arbitration.html',`<html><body style="margin:0;background:#D9CAB0">${ds}</body></html>`);
console.log('written');

module.exports={frame,planScreen,runScreen,embed,base,bg,svgWrap,chev};
