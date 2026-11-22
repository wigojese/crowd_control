const fs=require('fs'),path=require('path');
const C={stock:'#EDE1CC',bright:'#F7F0E3',ink:'#1E1A17',soft:'#433B33',ver:'#D6522F',verd:'#B2401F',olive:'#7A7B55',oliveD:'#585A38',must:'#C39B34',mustD:'#8A650F',ox:'#7D3B42',rust:'#A86135',rustD:'#8A4A27',mass:'#DDCFB8',stone:'#A49A8B',lilac:'#8C6A78'};
const F={disp:"'Bitstream Charter','DejaVu Serif',serif",ui:"'Inter',sans-serif",num:"'JetBrains Mono',monospace"};
const lum=h=>{const c=[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255).map(v=>v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4));return .2126*c[0]+.7152*c[1]+.0722*c[2]};
const cr=(a,b)=>{const x=lum(a),y=lum(b);return +((Math.max(x,y)+.05)/(Math.min(x,y)+.05)).toFixed(2)};
const N={A:[180,50],B:[92,145],C:[262,155],D:[120,286],E:[254,290],F:[106,470],G:[266,475]};
const NAME={A:'North Gate',B:'Canal Turn',C:'Market',D:'Bridge West',E:'Bridge East',F:'School',G:'Plaza'};
const E={AB:['A','B',14],AC:['A','C',-14],BC:['B','C',-22],BD:['B','D',10],CE:['C','E',-8],DE:['D','E',0],DF:['D','F',10],EG:['E','G',-10],FG:['F','G',16]};
const NARROW={BD:1,DE:1};
function ctrl(e){const[a,b,k]=E[e];const A=N[a],B=N[b];const dx=B[0]-A[0],dy=B[1]-A[1],l=Math.hypot(dx,dy);return[(A[0]+B[0])/2+(-dy/l)*k*2,(A[1]+B[1])/2+(dx/l)*k*2]}
const dd=e=>{const[a,b]=E[e];const c=ctrl(e);return`M${N[a][0]},${N[a][1]} Q${c[0].toFixed(1)},${c[1].toFixed(1)} ${N[b][0]},${N[b][1]}`};
function pt(e,t){const[a,b]=E[e];const A=N[a],B=N[b],c=ctrl(e),u=1-t;return[u*u*A[0]+2*u*t*c[0]+t*t*B[0],u*u*A[1]+2*u*t*c[1]+t*t*B[1]]}
function ang(e,t){const p=pt(e,Math.max(0,t-.01)),q=pt(e,Math.min(1,t+.01));return Math.atan2(q[1]-p[1],q[0]-p[0])*180/Math.PI}
const CANALX=187;
const arrow=s=>`M${-s},${-s*.34} L${s*.12},${-s*.34} L${s*.12},${-s*.8} L${s},0 L${s*.12},${s*.8} L${s*.12},${s*.34} L${-s},${s*.34}Z`;
const HEAD={N:-90,E:0,S:90,W:180};
// ---------- defs ----------
function defs(id){return`<pattern id="gr${id}" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" r=".6" fill="${C.ink}" opacity=".09"/><circle cx="3.7" cy="3.4" r=".5" fill="${C.ink}" opacity=".07"/></pattern>
<filter id="tooth${id}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4"/><feColorMatrix type="matrix" values="0 0 0 0 .22  0 0 0 0 .16  0 0 0 0 .1  .9 0 0 0 -.32"/></filter>
<filter id="ink${id}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".07" numOctaves="2" seed="7" result="t"/><feDisplacementMap in="SourceGraphic" in2="t" scale="1.5" xChannelSelector="R" yChannelSelector="G"/></filter>
<pattern id="ht${id}" width="4.6" height="4.6" patternUnits="userSpaceOnUse"><rect width="4.6" height="4.6" fill="${C.bright}" opacity=".7"/><circle cx="1.2" cy="1.2" r="1.55" fill="${C.ox}"/><circle cx="3.5" cy="3.5" r="1.55" fill="${C.ox}"/></pattern>
<pattern id="st${id}" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="1.6" cy="1.8" r="1" fill="${C.olive}" opacity=".75"/><circle cx="5" cy="5.2" r="1" fill="${C.olive}" opacity=".75"/></pattern>
<pattern id="dg${id}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3.5" height="7" fill="${C.soft}" opacity=".85"/></pattern>
<pattern id="aw${id}" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="5" height="10" fill="${C.rust}"/><rect x="5" width="5" height="10" fill="${C.bright}"/></pattern>
<pattern id="ck${id}" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="5" height="5" fill="${C.stone}" opacity=".55"/><rect x="5" y="5" width="5" height="5" fill="${C.stone}" opacity=".55"/></pattern>
<linearGradient id="sp${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.stock}" stop-opacity="0"/><stop offset="1" stop-color="${C.stock}" stop-opacity=".0"/></linearGradient>`}
// ---------- landmarks (authored) ----------
function lm(k,x,y,w,h,id){const off=`transform="translate(1.6,1.2)"`;let s='';const ol=`fill="none" stroke="${C.soft}" stroke-width="1.3"`;
 if(k==='court'){s+=`<g ${off}><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${C.mass}"/></g><rect x="${x}" y="${y}" width="${w}" height="${h}" ${ol}/><rect x="${x+14}" y="${y+14}" width="${w-28}" height="${h-28}" fill="${C.olive}" fill-opacity=".38" stroke="${C.soft}" stroke-width="1"/>`}
 if(k==='strip'){s+=`<g ${off}><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${C.mass}"/></g><rect x="${x}" y="${y}" width="${w}" height="${h}" ${ol}/>`;s+=`<rect x="${x}" y="${y}" width="${w}" height="${h/4}" fill="${C.rust}" opacity=".4"/><rect x="${x}" y="${y+h/2}" width="${w}" height="${h/4}" fill="${C.rust}" opacity=".4"/>`;for(let i=1;i<4;i++)s+=`<line x1="${x}" y1="${y+i*h/4}" x2="${x+w}" y2="${y+i*h/4}" stroke="${C.soft}" stroke-width="1"/>`}
 if(k==='school'){s+=`<g ${off}><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${C.must}" opacity=".55"/></g><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="none" stroke="${C.soft}" stroke-width="1.4" stroke-dasharray="1.5 3.5"/><rect x="${x+8}" y="${y+8}" width="${w-16}" height="${h*.34}" fill="${C.bright}" stroke="${C.soft}" stroke-width="1.3"/><path d="M${x+w/2-5},${y+8} l5,-8 l5,8" fill="${C.soft}"/><line x1="${x+10}" y1="${y+h*.62}" x2="${x+w-10}" y2="${y+h*.62}" stroke="${C.bright}" stroke-width="2"/><line x1="${x+10}" y1="${y+h*.8}" x2="${x+w-10}" y2="${y+h*.8}" stroke="${C.bright}" stroke-width="2"/><circle cx="${x+w/2}" cy="${y+h*.71}" r="5" fill="none" stroke="${C.bright}" stroke-width="1.6"/>`}
 if(k==='market'){s+=`<g ${off}><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${C.mass}"/></g><rect x="${x}" y="${y}" width="${w}" height="${h}" ${ol}/><rect x="${x}" y="${y}" width="${w}" height="${h*.4}" fill="url(#aw${id})" stroke="${C.soft}" stroke-width="1.3"/>`;for(let i=0;i<3;i++)for(let j=0;j<2;j++)s+=`<rect x="${x+6+i*(w-12)/3}" y="${y+h*.52+j*9}" width="${(w-12)/3-4}" height="6" fill="${C.stock}" stroke="${C.soft}" stroke-width="1"/>`}
 if(k==='industrial'){s+=`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="url(#dg${id})"/><rect x="${x}" y="${y}" width="${w}" height="${h}" ${ol}/><rect x="${x+w-14}" y="${y-8}" width="7" height="12" fill="${C.soft}"/>`}
 if(k==='civic'){s+=`<g ${off}><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="url(#ck${id})"/></g><rect x="${x}" y="${y}" width="${w}" height="${h}" ${ol}/><rect x="${x+w/2-14}" y="${y+h/2-9}" width="28" height="18" fill="${C.bright}" stroke="${C.soft}" stroke-width="1.3"/><path d="M${x+w/2-17},${y+h/2-9} L${x+w/2},${y+h/2-18} L${x+w/2+17},${y+h/2-9}Z" fill="${C.olive}" stroke="${C.soft}" stroke-width="1.1"/>`}
 if(k==='hall'){s+=`<g ${off}><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${C.mass}"/></g><rect x="${x}" y="${y}" width="${w}" height="${h}" ${ol}/><path d="M${x},${y} L${x+w/2},${y-12} L${x+w},${y}" fill="${C.mass}" stroke="${C.soft}" stroke-width="1.3"/><rect x="${x+w/2-6}" y="${y+h-16}" width="12" height="16" fill="${C.soft}"/>`}
 if(k==='park'){s+=`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="url(#st${id})" stroke="${C.olive}" stroke-width="1.4" stroke-dasharray="3 3"/>`;[[.25,.3],[.6,.22],[.75,.6],[.35,.7],[.5,.48]].forEach(([a,b])=>s+=`<circle cx="${x+w*a}" cy="${y+h*b}" r="6.5" fill="${C.olive}" stroke="${C.soft}" stroke-width="1.1"/>`)}
 return s}
const BLK=[['court',14,190,60,64],['strip',14,326,64,70],['school',16,420,66,76],['market',292,206,58,50],['industrial',296,332,54,70],['park',150,322,90,100],['civic',150,512,72,50],['hall',292,512,58,56],['court',28,66,46,42],['strip',292,64,50,44]];
function geo(id,o){let s='';
 // canal: pale waveline with retaining-wall marks; bridge shadow beneath crossing
 const cx=CANALX;
 s+=`<rect x="${cx-15}" y="196" width="30" height="246" fill="${C.bright}"/><line x1="${cx-15}" y1="196" x2="${cx-15}" y2="442" stroke="${C.soft}" stroke-width="1.6"/><line x1="${cx+15}" y1="196" x2="${cx+15}" y2="442" stroke="${C.soft}" stroke-width="1.6"/>`;
 for(let y=200;y<442;y+=8){s+=`<line x1="${cx-15}" y1="${y}" x2="${cx-20}" y2="${y}" stroke="${C.soft}" stroke-width="1.1"/><line x1="${cx+15}" y1="${y}" x2="${cx+20}" y2="${y}" stroke="${C.soft}" stroke-width="1.1"/>`}
 for(let y=206;y<440;y+=13)s+=`<path d="M${cx-10},${y} q5,-3.5 10,0 t10,0" fill="none" stroke="${C.stone}" stroke-width="1.3"/>`;
 for(let i=0;i<7;i++)s+=`<line x1="${cx-14+i*4.6}" y1="296" x2="${cx-10+i*4.6}" y2="310" stroke="${C.soft}" stroke-width="1" opacity=".55"/>`;
 // plaza radial paving around G
 const [gx,gy]=N.G;s+=`<circle cx="${gx}" cy="${gy}" r="38" fill="${C.bright}" stroke="${C.soft}" stroke-width="1.2" stroke-dasharray="2 3"/><circle cx="${gx}" cy="${gy}" r="28" fill="none" stroke="${C.stone}" stroke-width="1.2"/>`;for(let i=0;i<16;i++){const a=i*Math.PI/8;s+=`<line x1="${gx+Math.cos(a)*28}" y1="${gy+Math.sin(a)*28}" x2="${gx+Math.cos(a)*38}" y2="${gy+Math.sin(a)*38}" stroke="${C.stone}" stroke-width="1.2"/>`}
 BLK.forEach(([k,x,y,w,h])=>s+=lm(k,x,y,w,h,id));
 const hot=o.hot||[],trace=o.trace||{};
 s+=`<g filter="url(#ink${id})">`;
 Object.keys(E).forEach(e=>{if(hot.includes(e))s+=`<path d="${dd(e)}" fill="none" stroke="url(#ht${id})" stroke-width="${NARROW[e]?17:19}" stroke-linecap="round"/>`});
 Object.keys(E).forEach(e=>{const nw=NARROW[e];s+=`<path d="${dd(e)}" fill="none" stroke="${o.roadCol}" stroke-width="${nw?8:11}" stroke-linecap="round"/>`});
 Object.keys(E).forEach(e=>{const nw=NARROW[e];s+=`<path d="${dd(e)}" fill="none" stroke="${C.stock}" stroke-width="${nw?4.4:7.4}" stroke-linecap="round"/>`});
 Object.keys(trace).forEach(e=>{s+=`<path d="${dd(e)}" fill="none" stroke="${C.rust}" stroke-width="${trace[e]}" stroke-linecap="round" opacity=".85"/>`});
 s+=`</g>`;
 for(let i=0;i<8;i++)s+=`<line x1="${cx-15+i*4.3}" y1="283" x2="${cx-15+i*4.3}" y2="294" stroke="${o.roadCol}" stroke-width="1.3"/>`;
 return s}
function nodesW(){let s='';['B','C','D','E'].forEach(n=>{const[x,y]=N[n];const sock=n==='B'||n==='C';s+=`<circle cx="${x}" cy="${y}" r="${sock?8.5:6}" fill="${C.bright}" stroke="${C.ink}" stroke-width="2.2"/>`});return s}
// ---------- seals (screen space) ----------
function seal(k,x,y,r,cnt,tot){const fill=k==='F'?C.must:k==='G'?C.olive:C.bright;let s=`<circle cx="${x}" cy="${y}" r="${r+3.4}" fill="${C.stock}"/><circle cx="${x+1.6}" cy="${y+1.2}" r="${r}" fill="${fill}"/><circle cx="${x}" cy="${y}" r="${r}" fill="none" stroke="${C.ink}" stroke-width="2.4"/>`;
 const g=r/17,ic=k==='G'?C.bright:C.ink;
 if(cnt!=null&&cnt>=tot)s+=`<circle cx="${x}" cy="${y}" r="${r+6.2}" fill="none" stroke="${C.ink}" stroke-width="3.2"/>`;else if(cnt!=null){const a=2*Math.PI*cnt/tot;const x2=x+Math.sin(a)*(r+6.2),y2=y-Math.cos(a)*(r+6.2);s+=`<path d="M${x},${y-r-6.2} A${r+6.2},${r+6.2} 0 ${a>Math.PI?1:0} 1 ${x2.toFixed(1)},${y2.toFixed(1)}" fill="none" stroke="${C.ink}" stroke-width="3.2" stroke-linecap="round"/>`}
 if(k==='F')s+=`<path d="M${x-8*g},${y+5*g} L${x},${y-7*g} L${x+8*g},${y+5*g}M${x-5*g},${y+6*g} h${10*g}" fill="none" stroke="${C.ink}" stroke-width="${2.3*g}" stroke-linejoin="round" stroke-linecap="round"/>`;
 if(k==='G'){s+=`<circle cx="${x}" cy="${y}" r="${5.4*g}" fill="none" stroke="${ic}" stroke-width="${2*g}"/>`;for(let i=0;i<8;i++){const a=i*Math.PI/4;s+=`<line x1="${x+Math.cos(a)*7.6*g}" y1="${y+Math.sin(a)*7.6*g}" x2="${x+Math.cos(a)*10*g}" y2="${y+Math.sin(a)*10*g}" stroke="${ic}" stroke-width="${1.8*g}"/>`}}
 if(k==='A')s+=`<path d="M${x-7*g},${y+7*g} V${y-1*g} A${7*g},${7*g} 0 0 1 ${x-1.2*g},${y-8*g} M${x+1.2*g},${y-8*g} A${7*g},${7*g} 0 0 1 ${x+7*g},${y-1*g} V${y+7*g}" fill="none" stroke="${C.ink}" stroke-width="${2.3*g}" stroke-linecap="round"/>`;
 return s}
// ---------- people: stamp figures ----------
function person(p,detail){ // unit figure ~ 26 tall, facing +x, origin at body centre
 let s='';const leg=(a,b)=>`<g stroke="${C.ink}" stroke-width="2.1" stroke-linecap="round"><line x1="-1.8" y1="5" x2="${-1.8-a}" y2="11"/><line x1="1.8" y1="5" x2="${1.8+b}" y2="11"/></g>`;
 if(p==='C'){s+=leg(2.4,2.4)+`<path d="M-4.4,-5.4 L4.4,-5.4 L4.9,5.6 L-4.9,5.6Z" fill="${C.ink}"/><circle cy="-9.2" r="3.1" fill="${C.ink}"/><rect x="-4.6" y="-12.6" width="9.2" height="1.8" fill="${C.ink}"/><rect x="-2.8" y="-15.4" width="5.6" height="3.2" fill="${C.ink}"/><rect x="3.4" y="2.2" width="5.2" height="4.2" fill="${C.rust}" stroke="${C.ink}" stroke-width=".9"/>`;if(detail)s+=`<path d="M3.4,2.2 v-1.4 h3 v1.4" fill="none" stroke="${C.ink}" stroke-width=".9"/><path d="M0,-5.4 L0,5.6" stroke="${C.bright}" stroke-width=".7"/><rect x="-4.6" y="-12.6" width="9.2" height=".9" fill="${C.rust}"/>`}
 if(p==='F'){s+=leg(1.6,1.6)+`<circle cy=".4" r="5.5" fill="${C.ink}"/><circle cy="-9" r="3.4" fill="${C.ink}"/><path d="M-3.4,-10.2 a3.4,3.4 0 0 1 6.8,0Z" fill="${C.must}" stroke="${C.ink}" stroke-width=".8"/><circle cy="-13.3" r="1.5" fill="${C.must}" stroke="${C.ink}" stroke-width=".7"/><rect x="-4.2" y="-5.6" width="8.4" height="1.7" fill="${C.bright}"/><line x1="-5" y1="3" x2="-9" y2="5" stroke="${C.ink}" stroke-width="1"/><circle cx="-10.6" cy="5.4" r="2.3" fill="${C.ink}"/>`}
 if(p==='I'){s+=leg(4.4,3.8)+`<path d="M-4,5.6 L-5.6,-5 L5,-6.4 L3.8,5.6Z" fill="${C.ink}" transform="rotate(-6)"/><circle cx="2" cy="-9.6" r="3" fill="${C.ink}"/><path d="M-5.6,-4 L-10,-1 L-6,3Z" fill="${C.olive}" stroke="${C.ink}" stroke-width=".9"/><g stroke="${C.ink}" stroke-width="1.3" stroke-linecap="round"><line x1="-12" y1="-3" x2="-17" y2="-3"/><line x1="-12" y1="1" x2="-19" y2="1"/></g>`;if(detail)s+=`<path d="M-5.2,-5 L2.6,3" stroke="${C.bright}" stroke-width=".8"/>`}
 return s}
function glyph(x,y,a,p,k=1,detail=false){const dir=Math.cos(a*Math.PI/180)<-.05?-1:1;return`<g transform="translate(${x.toFixed(1)},${y.toFixed(1)}) scale(${dir*k},${k})">${person(p,detail)}</g>`}
// ---------- sign ----------
function sign(x,y,h,st){const a=HEAD[h];const lift=st==='lift';let s=`<g transform="translate(${x},${y})">`;
 if(lift)s+=`<circle cx="4" cy="6" r="22" fill="${C.bright}" stroke="${C.stone}" stroke-width="1"/><ellipse cx="4" cy="32" rx="12" ry="3.4" fill="${C.ink}" opacity=".2"/>`;
 else s+=`<ellipse cx="2" cy="27" rx="13" ry="4" fill="${C.ink}" opacity=".32"/><circle cx="2.4" cy="2.4" r="22" fill="${C.ink}" opacity=".22"/>`;
 const oy=lift?-5:0;
 s+=`<g transform="translate(0,${oy})"><path d="M-6,14 h12 v11 l-6,-3.5 l-6,3.5Z" fill="${C.soft}"/><circle r="22" fill="${C.ink}"/><circle r="18.6" fill="none" stroke="${C.bright}" stroke-width="1.1"/>`;
 [45,135,225,315].forEach(d=>{const r=Math.PI*d/180;s+=`<circle cx="${(Math.cos(r)*20.2).toFixed(1)}" cy="${(Math.sin(r)*20.2).toFixed(1)}" r="1.1" fill="${C.stone}"/>`});
 s+=`<g transform="rotate(${a})"><path d="M23,-4.6 L23,4.6 L17,0Z" fill="${C.stock}"/><path d="${arrow(14.5)}" fill="${C.ver}" stroke="${C.bright}" stroke-width="1.8" stroke-linejoin="round"/></g></g></g>`;return s}
function socketRing(x,y,on){return`<circle cx="${x}" cy="${y}" r="${on?25:22}" fill="none" stroke="${C.ver}" stroke-width="${on?3:2}" ${on?'':'stroke-dasharray="4 4"'}/>${on?`<circle cx="${x}" cy="${y}" r="29.5" fill="none" stroke="${C.ver}" stroke-width="1"/>`:''}`}
// ---------- type quirk: route-line underline + clipped notices ----------
const routeLine=(x,y,w,col=C.ink)=>`<circle cx="${x+3}" cy="${y}" r="3.2" fill="${C.bright}" stroke="${col}" stroke-width="1.8"/><path d="M${x+7},${y} H${x+w-22} L${x+w-14},${y+0} " fill="none" stroke="${col}" stroke-width="2.2"/><path d="M${x+w-22},${y} q4,0 4,-0 " stroke="${col}"/><path d="M${x+w-9},${y-4.4} L${x+w-3},${y} L${x+w-9},${y+4.4}" fill="none" stroke="${C.rust}" stroke-width="2.4" stroke-linejoin="round"/>`;
const halo=(x,y,t,o={})=>`<text x="${x}" y="${y}" text-anchor="${o.a||'middle'}" font-family="${F.ui}" font-size="${o.fs||13}" font-weight="${o.w||600}" fill="${o.c||C.ink}" paint-order="stroke" stroke="${C.stock}" stroke-width="4.5" stroke-linejoin="round">${t}</text>`;
function tag(x,y,t,o={}){const w=t.length*(o.mono?8:7.1)+20;const bar=o.bar||C.rust;const fam=o.mono?F.num:F.ui;return`<g><path d="M${x},${y-17} H${x+w-8} L${x+w},${y-9} V${y+8} H${x}Z" fill="${C.bright}" stroke="${C.ink}" stroke-width="1.4"/><rect x="${x}" y="${y-17}" width="5" height="25" fill="${bar}"/><text x="${x+11}" y="${y}" font-family="${fam}" font-size="${o.fs||13}" font-weight="700" fill="${C.ink}">${t}</text></g>`}
const reg=(x,y)=>`<g stroke="${C.ink}" stroke-width="1" opacity=".7"><circle cx="${x}" cy="${y}" r="5" fill="none"/><line x1="${x-9}" y1="${y}" x2="${x+9}" y2="${y}"/><line x1="${x}" y1="${y-9}" x2="${x}" y2="${y+9}"/></g>`;
// ---------- layout ----------
function L(W,H){const compact=W<340;return{W,H,compact,dockH:compact?104:106,mapTop:compact?54:112,hudRuleY:compact?50:104}}
function fit(l,mapTop,mapH,k=1){const s=Math.min((l.W-24)/342,mapH/470)*k;return{s,ox:l.W/2-181*s,oy:mapTop+(mapH-470*s)/2-30*s}}
const S=(T,p)=>[T.ox+p[0]*T.s,T.oy+p[1]*T.s];
function hud(l,arr,time,frac){let s=`<rect width="${l.W}" height="${l.mapTop}" fill="${C.bright}"/>`;
 if(l.compact){s+=`<text x="14" y="30" font-family="${F.disp}" font-size="16" font-weight="700" fill="${C.ink}">School Crossing</text><text x="${l.W-14}" y="31" text-anchor="end" font-family="${F.num}" font-size="20" font-weight="800" fill="${C.ink}">${arr}<tspan font-size="13" font-weight="500" fill="${C.soft}">/20</tspan> <tspan font-size="15" font-weight="700">${time}</tspan></text><rect x="14" y="40" width="${l.W-28}" height="5" fill="${C.mass}"/><rect x="14" y="40" width="${(l.W-28)*frac}" height="5" fill="${C.ink}"/>`}
 else{s+=`<text x="22" y="40" font-family="${F.disp}" font-size="20" font-weight="700" fill="${C.ink}">School Crossing</text>${routeLine(22,50,176)}<text x="22" y="72" font-family="${F.ui}" font-size="13.5" fill="${C.ink}">Deliver 16 of 20 before 0:32</text><text x="368" y="52" text-anchor="end" font-family="${F.num}" font-size="34" font-weight="800" fill="${C.ink}">${arr}<tspan font-size="17" font-weight="500" fill="${C.soft}">/20</tspan></text><text x="368" y="72" text-anchor="end" font-family="${F.num}" font-size="14.5" font-weight="700" fill="${C.ink}">${time} left</text><rect x="22" y="84" width="346" height="7" fill="${C.mass}"/><rect x="22" y="84" width="${346*frac}" height="7" fill="${C.ink}"/><rect x="368" y="80" width="2" height="15" fill="${C.ink}"/>`}
 s+=`<rect x="0" y="${l.hudRuleY}" width="${l.W}" height="2.4" fill="${C.ink}"/>`;return s}
function btn(x,y,w,h,t,k){
 if(k==='primary')return`<rect x="${x+2.5}" y="${y+2.5}" width="${w}" height="${h}" fill="${C.rust}"/><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${C.ink}"/><text x="${x+w/2}" y="${y+h/2+6}" text-anchor="middle" font-family="${F.ui}" font-size="17" font-weight="700" fill="${C.bright}">${t}</text>`;
 if(k==='secondary')return`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${C.bright}" stroke="${C.ink}" stroke-width="2"/><text x="${x+w/2}" y="${y+h/2+6}" text-anchor="middle" font-family="${F.ui}" font-size="16" font-weight="700" fill="${C.ink}">${t}</text>`;
 return`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${C.mass}" stroke="${C.stone}" stroke-width="1.6" stroke-dasharray="4 3"/><text x="${x+w/2}" y="${y+h/2+6}" text-anchor="middle" font-family="${F.ui}" font-size="17" font-weight="700" fill="${C.soft}">${t}</text>`}
function dock(l,c){const y=l.H-l.dockH,W=l.W;let s=`<path d="M0,${y} H${W} V${l.H} H0Z" fill="${C.bright}"/><rect x="0" y="${y}" width="${W}" height="2.4" fill="${C.ink}"/>`;
 const ty=y+12,th=l.dockH-24;s+=`<path d="M12,${ty} H${W-12} V${ty+th} H12Z" fill="${C.mass}"/><path d="M12,${ty} H${W-12}" stroke="${C.stone}" stroke-width="1.6"/>`;
 const cx=l.compact?44:50,cy=y+l.dockH/2+2;
 if(c.sign==='dock')s+=sign(cx,cy-4,'S','dock');else s+=`<circle cx="${cx}" cy="${cy}" r="25" fill="none" stroke="${C.stone}" stroke-width="1.6" stroke-dasharray="4 4"/>`;
 const tx=cx+38;s+=`<text x="${tx}" y="${cy-3}" font-family="${F.ui}" font-size="${l.compact?14:15.5}" font-weight="700" fill="${C.ink}">${c.l1}</text><text x="${tx}" y="${cy+16}" font-family="${F.ui}" font-size="${l.compact?12.5:13}" fill="${C.soft}">${c.l2}</text>`;
 const bw=l.compact?92:104;s+=btn(W-bw-18,cy-24,bw,48,c.btn,c.bk||'primary');return s}
const clip=(id,l,top,h)=>`<clipPath id="cl${id}"><rect x="0" y="${top}" width="${l.W}" height="${h}"/></clipPath>`;
function mapGroup(l,id,T,o,body){return`<g clip-path="url(#cl${id})"><g transform="translate(${T.ox.toFixed(2)},${T.oy.toFixed(2)}) scale(${T.s.toFixed(4)})">${geo(id,o)}${body||''}${nodesW()}</g></g>`}
const crowd=(list,T,k)=>list.map(([e,t,p])=>{const q=pt(e,t);return glyph(...S(T,q),ang(e,t),p,k||(T.s<.9?.8:.95))}).join('');
const WAIT=[['AB',.05,'C'],['AB',.13,'F'],['AC',.06,'C'],['AC',.14,'F'],['AB',.22,'I'],['AC',.24,'I'],['AB',.32,'C']];
const RUN=[['AB',.32,'C'],['AB',.64,'F'],['AC',.3,'I'],['AC',.64,'C'],['BD',.15,'C'],['BD',.27,'F'],['BD',.4,'F'],['BD',.5,'C'],['BD',.6,'I'],['DE',.35,'F'],['DE',.66,'C'],['DF',.22,'C'],['DF',.52,'I'],['DF',.82,'C'],['CE',.5,'C'],['CE',.8,'F'],['EG',.4,'C'],['FG',.5,'I']];
const FLUX={AB:13,AC:6,BD:15,BC:2,CE:5,DE:3,DF:9,EG:4,FG:2};
function ribbons(T,id,k=1,hot=['BD','DE'],col=C.rust){let s='';Object.keys(FLUX).forEach(e=>{const w=Math.max(3,FLUX[e]*k*T.s);const h=hot.includes(e);const tr=`transform="translate(${T.ox},${T.oy}) scale(${T.s})"`;
 s+=`<path d="${dd(e)}" ${tr} fill="none" stroke="${C.ink}" stroke-width="${(w+3)/T.s}"/><path d="${dd(e)}" ${tr} fill="none" stroke="${h?C.ox:col}" stroke-width="${w/T.s}"/>`;
 if(h)s+=`<path d="${dd(e)}" ${tr} fill="none" stroke="url(#ht${id})" stroke-width="${(w-1)/T.s}" opacity=".95"/>`;
 const n=Math.max(2,Math.round(Math.hypot(N[E[e][0]][0]-N[E[e][1]][0],N[E[e][0]][1]-N[E[e][1]][1])/34));
 for(let i=0;i<n;i++){const t=(i+.5)/n,p=S(T,pt(e,t)),a=ang(e,t),hh=Math.max(3,w*.38);s+=`<path d="M${-hh*.7},${-hh} L${hh*.7},0 L${-hh*.7},${hh}" transform="translate(${p[0].toFixed(1)},${p[1].toFixed(1)}) rotate(${a.toFixed(0)})" fill="none" stroke="${C.bright}" stroke-width="${Math.min(2.6,w*.2)}" stroke-linejoin="round"/>`}});return s}
const labelsMain=(T,l,list)=>list.filter(x=>!(l.compact&&x[0]==='A')).map(([n,dx,dy,a])=>halo(S(T,N[n])[0]+dx,S(T,N[n])[1]+dy,NAME[n],{a:a||'middle'})).join('');
const sealsAt=(T,l,o)=>[['F'],['G'],['A']].map(([n])=>{const p=S(T,N[n]);const r=n==='A'?13:(o.r||(l.compact?15:17));const c=o.cnt&&o.cnt[n];return seal(n,p[0],p[1],r,c?c[0]:null,c?c[1]:1)}).join('');
// ---------- screens ----------
function screen(kind,W,H,uid){const l=L(W,H);const id=kind+W+uid;const mapBottom=H-l.dockH;let s=`<rect width="${W}" height="${H}" fill="${C.stock}"/><rect width="${W}" height="${H}" fill="url(#gr${id})"/><rect width="${W}" height="${H}" filter="url(#tooth${id})" opacity=".55"/>`;
 let dx=defs(id);const mh=mapBottom-l.mapTop-4;const cp=W<340;
 const TR={AB:3.2,AC:2.4,DF:2.8,CE:2.4};
 if(kind==='title'){const top=cp?250:372;const T=fit(l,top,mapBottom-top,.92);dx+=clip(id,l,top-10,mapBottom-top+10);
  s+=mapGroup(l,id,T,{roadCol:C.stone});s+=crowd(WAIT.concat(RUN.slice(0,6)),T,.7);s+=sealsAt(T,l,{});
  s+=`<text x="${cp?20:28}" y="${cp?72:124}" font-family="${F.disp}" font-size="${cp?44:62}" font-weight="700" fill="${C.ink}" letter-spacing="-1">Crowd</text><text x="${cp?20:28}" y="${cp?116:186}" font-family="${F.disp}" font-size="${cp?44:62}" font-weight="700" fill="${C.ink}" letter-spacing="-1">Control</text>`;
  s+=routeLine(cp?20:28,cp?134:206,cp?170:250)+`<text x="${cp?20:28}" y="${cp?160:236}" font-family="${F.ui}" font-size="${cp?14:17}" fill="${C.ink}">One sign. A hundred decisions.</text>`;
  s+=`<g transform="translate(${W-(cp?56:56)},${cp?96:128}) scale(${cp?1.5:1.6})">${sign(0,0,'S','lift')}</g>`;
  [[0,'C'],[1,'F'],[2,'I']].forEach(([i,p])=>{s+=glyph((cp?34:44)+i*(cp?56:64),cp?214:292,0,p,cp?1.7:2.3,true)});
  s+=reg(16,top-4)+reg(W-16,top-4);
  s+=`<path d="M0,${H-l.dockH} H${W} V${H} H0Z" fill="${C.bright}"/><rect y="${H-l.dockH}" width="${W}" height="2.4" fill="${C.ink}"/>`+btn(20,H-l.dockH+26,W-40,56,'Play','primary')}
 if(kind==='plan'){const T=fit(l,l.mapTop,mh);dx+=clip(id,l,l.mapTop,mh);s+=hud(l,0,'0:32',0);s+=mapGroup(l,id,T,{roadCol:C.ink});
  const pb=S(T,N.B);['BC','BD'].forEach(e=>{[.22,.5,.78].forEach(t=>{const p=S(T,pt(e,t));s+=`<path d="M-4,-5 L3,0 L-4,5" transform="translate(${p[0].toFixed(1)},${p[1].toFixed(1)}) rotate(${ang(e,t).toFixed(0)})" fill="none" stroke="${C.mustD}" stroke-width="2.8" stroke-linejoin="round"/>`})});
  s+=crowd(WAIT,T);s+=sealsAt(T,l,{});const pc=S(T,N.C);s+=socketRing(pc[0],pc[1],false)+socketRing(pb[0],pb[1],true)+sign(pb[0],pb[1]-2,'S','lift');
  s+=labelsMain(T,l,[['B',6,-48],['C',8,-48],['D',-46,6],['F',0,42],['G',0,42],['A',0,-24]]);
  s+=dock(l,{sign:'none',l1:'Place the sign',l2:cp?'Drag to a ringed spot':'Drag it to a ringed junction',btn:'Start',bk:'disabled'})}
 if(kind==='run'){const T=fit(l,l.mapTop,mh);dx+=clip(id,l,l.mapTop,mh);s+=hud(l,9,'0:18',14/32);s+=mapGroup(l,id,T,{roadCol:C.ink,hot:['BD'],trace:TR});s+=crowd(RUN,T);
  const pb=S(T,N.B);[.08,.15].forEach(t=>{const p=S(T,pt('BD',t));s+=`<path d="M-3,-5 L3,0 L-3,5" transform="translate(${p[0].toFixed(1)},${p[1].toFixed(1)}) rotate(${ang('BD',t).toFixed(0)})" fill="none" stroke="${C.ver}" stroke-width="2.8"/>`});
  s+=sealsAt(T,l,{cnt:{F:[3,12],G:[2,8]}});s+=sign(pb[0],pb[1]-2,'S','placed');
  const q=S(T,pt('BD',.5));s+=`<line x1="${q[0]+8}" y1="${q[1]}" x2="${q[0]+34}" y2="${q[1]}" stroke="${C.ink}" stroke-width="1.4"/>`+tag(q[0]+34,q[1]+4,'5 waiting',{bar:C.ox});
  const fp=S(T,pt('DF',.52));s+=`<circle cx="${fp[0]}" cy="${fp[1]-2}" r="15" fill="none" stroke="${C.ink}" stroke-width="1.6" stroke-dasharray="3 3"/><line x1="${fp[0]+15}" y1="${fp[1]}" x2="${fp[0]+34}" y2="${fp[1]}" stroke="${C.ink}" stroke-width="1.4"/>`+tag(fp[0]+34,fp[1]+4,'Walker → School');
  s+=labelsMain(T,l,[['B',6,-48],['C',8,-48],['D',-46,6],['A',0,-24]]);s+=dock(l,{sign:'none',l1:'Turn the sign',l2:cp?'Tap sign. 1 left':'Tap the sign. 1 turn left',btn:'Pause',bk:'secondary'})}
 if(kind==='atlas'){const T=fit(l,l.mapTop+8,mh-8,.84);dx+=clip(id,l,l.mapTop,mh);s+=hud(l,11,'0:14',18/32);s+=mapGroup(l,id,T,{roadCol:C.stone});s+=ribbons(T,id,.9);
  const tg=(e,t,txt,x=0,y=0)=>{const p=S(T,pt(e,t));return tag(p[0]+x,p[1]+y+4,txt,{mono:1,bar:(e==='BD')?C.ox:C.rust})};
  s+=tg('AB',.5,'13',-56,0)+tg('BD',.5,'15',14,0)+tg('DF',.5,'9',-58,0)+tg('AC',.5,'6',14,0)+tg('CE',.5,'5',14,0)+tg('EG',.5,'4',14,0);
  [['F',12,7],['G',8,4],['A',null,null]].forEach(([n,tot,c])=>{const p=S(T,N[n]);s+=seal(n,p[0],p[1],n==='A'?14:22,c,tot||1)});
  const pb=S(T,N.B);s+=sign(pb[0],pb[1]-2,'S','placed');s+=halo(S(T,N.F)[0],S(T,N.F)[1]+44,'School')+halo(S(T,N.G)[0],S(T,N.G)[1]+44,'Plaza')+halo(S(T,N.A)[0],S(T,N.A)[1]-24,'North Gate');
  s+=tag(16,l.mapTop+28,'Thicker = more walkers');s+=dock(l,{sign:'none',l1:'Atlas view',l2:cp?'Real counts':'Counts are real walkers',btn:'Pause',bk:'secondary'})}
 if(kind==='result'||kind==='win'){const win=kind==='win';const rh=cp?236:402;const mapB=H-rh;const T=fit(l,cp?6:16,mapB-(cp?10:28),.9);dx+=clip(id,l,0,mapB);
  s+=mapGroup(l,id,T,{roadCol:C.stone,hot:win?[]:['BD'],trace:win?{AB:3.4,AC:3,BD:3.6,CE:3,DE:2.4,DF:3.6,EG:3}:{}});s+=ribbons(T,id,.55,win?[]:['BD','DE'],win?C.olive:C.rust);
  [['F',win?9:7,12],['G',win?8:7,8]].forEach(([n,c,t])=>{const p=S(T,N[n]);s+=seal(n,p[0],p[1],14,c,t)});
  const pb=S(T,N.B);s+=sign(pb[0],pb[1]-2,win?'E':'S','placed');
  if(!win){const q=S(T,pt('BD',.5));s+=`<line x1="${q[0]+6}" y1="${q[1]}" x2="${q[0]+26}" y2="${q[1]}" stroke="${C.ink}" stroke-width="1.4"/>`+tag(q[0]+26,q[1]+4,'5 waited here',{bar:C.ox})}
  s+=reg(14,mapB-14)+reg(W-14,mapB-14);
  const y0=mapB;s+=`<path d="M0,${y0+14} L16,${y0} H${W-16} L${W},${y0+14} V${H} H0Z" fill="${C.bright}"/><path d="M0,${y0+14} L16,${y0} H${W-16} L${W},${y0+14}" fill="none" stroke="${C.ink}" stroke-width="2.4"/>`;
  const px=22,n=win?17:14;
  if(!cp){s+=`<text x="${px}" y="${y0+84}" font-family="${F.num}" font-size="64" font-weight="800" fill="${C.ink}" letter-spacing="-3">${n}<tspan font-size="30" font-weight="500" fill="${C.soft}"> / 20</tspan></text><text x="${px}" y="${y0+110}" font-family="${F.ui}" font-size="16" font-weight="700" fill="${C.ink}">arrived. ${win?'Goal 16 met.':'Goal 16: 2 short.'}</text>`}
  else s+=`<text x="${px-4}" y="${y0+50}" font-family="${F.num}" font-size="40" font-weight="800" fill="${C.ink}" letter-spacing="-2">${n}<tspan font-size="20" font-weight="500" fill="${C.soft}"> / 20</tspan></text><text x="${px+118}" y="${y0+40}" font-family="${F.ui}" font-size="13.5" font-weight="700" fill="${C.ink}">arrived</text><text x="${px+118}" y="${y0+56}" font-family="${F.ui}" font-size="13.5" fill="${C.ink}">Goal 16</text>`;
  // stamp
  const sx=W-(cp?58:92),sy=y0+(cp?44:74);const sc=win?C.oliveD:C.ox;
  s+=`<g transform="translate(${sx},${sy}) rotate(-8)"><rect x="-${cp?44:60}" y="-${cp?15:20}" width="${cp?88:120}" height="${cp?30:40}" fill="${win?C.olive:'url(#ht'+id+')'}" opacity="${win?.18:.9}"/><rect x="-${cp?44:60}" y="-${cp?15:20}" width="${cp?88:120}" height="${cp?30:40}" fill="none" stroke="${sc}" stroke-width="3"/><rect x="-${cp?40:55}" y="-${cp?11:15}" width="${cp?80:110}" height="${cp?22:30}" fill="none" stroke="${sc}" stroke-width="1.2"/><text y="${cp?6:8}" text-anchor="middle" font-family="${F.disp}" font-size="${cp?15:21}" font-weight="700" fill="${sc}" letter-spacing=".5">${win?'Delivered':'2 short'}</text></g>`;
  const sx0=px,sw=W-2*px,sy0=y0+(cp?64:126),sh=cp?44:66;const X=t=>sx0+sw*t/32,Y=m=>sy0+sh-sh*m/20;
  const steps=win?[[0,0],[8,1],[10,2],[12,4],[14,5],[16,7],[18,9],[20,10],[22,12],[24,13],[26,14],[28,15],[29,16],[30,17],[32,17]]:[[0,0],[9,1],[11,2],[13,3],[15,4],[17,6],[19,7],[21,8],[23,9],[25,10],[27,11],[29,12],[31,13],[32,14]];
  let pth=`M${X(0)},${Y(0)}`;steps.forEach(([t,m],i)=>{if(i)pth+=` H${X(t)} V${Y(m)}`});
  s+=`<rect x="${sx0}" y="${sy0}" width="${sw}" height="${sh}" fill="none" stroke="${C.stone}" stroke-width="1"/><line x1="${sx0}" y1="${Y(16)}" x2="${sx0+sw}" y2="${Y(16)}" stroke="${C.mustD}" stroke-width="1.8" stroke-dasharray="5 4"/><text x="${sx0+6}" y="${Y(16)-5}" font-family="${F.num}" font-size="12.5" font-weight="700" fill="${C.mustD}">goal 16</text><path d="${pth}" fill="none" stroke="${C.ink}" stroke-width="2.6"/>`;
  if(win)s+=`<circle cx="${X(29)}" cy="${Y(16)}" r="5.5" fill="${C.must}" stroke="${C.ink}" stroke-width="1.6"/>`;
  const ty=sy0+sh+(cp?20:26),fs_=cp?13.5:15.5;
  if(!win)s+=`<text x="${px}" y="${ty}" font-family="${F.ui}" font-size="${fs_}" fill="${C.ink}">Most delays: <tspan font-weight="700">Canal Turn → Bridge West</tspan></text><text x="${px}" y="${ty+(cp?17:22)}" font-family="${F.ui}" font-size="${fs_}" fill="${C.ink}">5 people waited there.${cp?'':' Your sign pointed south.'}</text>`;
  else s+=`<text x="${px}" y="${ty}" font-family="${F.ui}" font-size="${fs_}" fill="${C.ink}">Sign at <tspan font-weight="700">Canal Turn</tspan> pointed east.</text><text x="${px}" y="${ty+(cp?17:22)}" font-family="${F.ui}" font-size="${fs_}" fill="${C.ink}">Goal reached at 0:29, 3 seconds early.</text>`;
  const by=H-(cp?64:84);s+=btn(px,by,cp?150:196,cp?48:56,win?'Next level':'Try again','primary')+btn(px+(cp?160:208),by,cp?W-2*px-160:W-2*px-208,cp?48:56,win?(cp?'Replay':'Replay run'):(cp?'Inspect':'Inspect decision'),'secondary')}
 if(kind==='replay'){const sc=cp?1.0:1.25;const T={s:sc,ox:cp?20:15,oy:(cp?168:196)-145*sc};const dy=H-(cp?176:196);dx+=clip(id,l,l.mapTop,dy-l.mapTop);
  dx+=`<radialGradient id="sp${id}" cx="${cp?.2:.2}" cy="${cp?.2:.22}" r=".75"><stop offset=".12" stop-color="${C.stock}" stop-opacity="0"/><stop offset=".7" stop-color="${C.stock}" stop-opacity=".78"/></radialGradient>`;
  s+=`<rect width="${W}" height="${l.mapTop}" fill="${C.bright}"/>`;
  if(cp)s+=`<text x="14" y="30" font-family="${F.disp}" font-size="16" font-weight="700" fill="${C.ink}">Canal Turn, 0:11</text><text x="${W-14}" y="31" text-anchor="end" font-family="${F.ui}" font-size="13" fill="${C.soft}">Replay</text>`;
  else s+=`<text x="22" y="42" font-family="${F.disp}" font-size="22" font-weight="700" fill="${C.ink}">Canal Turn, 0:11</text>${routeLine(22,54,190)}<text x="22" y="76" font-family="${F.ui}" font-size="14" fill="${C.ink}">Where the run turned</text><text x="368" y="42" text-anchor="end" font-family="${F.ui}" font-size="13" fill="${C.soft}">Replay</text>`;
  s+=`<rect x="0" y="${l.hudRuleY}" width="${W}" height="2.4" fill="${C.ink}"/>`;
  s+=mapGroup(l,id,T,{roadCol:C.ink,hot:['BD'],trace:{}});
  s+=`<rect x="0" y="${l.mapTop}" width="${W}" height="${dy-l.mapTop}" fill="url(#sp${id})"/>`;
  const pb=S(T,N.B);
  // proportional branch fan
  const fan=(e,w,col,t0,t1)=>{const a=S(T,pt(e,t0)),b=S(T,pt(e,t1));return`<path d="${dd(e)}" transform="translate(${T.ox},${T.oy}) scale(${T.s})" fill="none" stroke="${C.ink}" stroke-width="${(w+3)/T.s}" stroke-linecap="butt" opacity=".95"/><path d="${dd(e)}" transform="translate(${T.ox},${T.oy}) scale(${T.s})" fill="none" stroke="${col}" stroke-width="${w/T.s}" stroke-linecap="butt"/>`};
  s+=fan('BD',18,C.ox,0,1)+`<path d="${dd('BD')}" transform="translate(${T.ox},${T.oy}) scale(${T.s})" fill="none" stroke="url(#ht${id})" stroke-width="${16/T.s}"/>`+fan('BC',5,C.rust,0,1);
  for(let i=0;i<7;i++){const t=.1+i*.07;const p=S(T,pt('BD',t));s+=glyph(p[0],p[1]-14,ang('BD',t),['C','F','F','C','I','F','C'][i],.8)}
  [.2,.42].forEach((t,i)=>{const p=S(T,pt('BC',t));s+=glyph(p[0],p[1]-14,ang('BC',t),['I','C'][i],.8)});
  s+=`<circle cx="${pb[0]}" cy="${pb[1]}" r="36" fill="none" stroke="${C.ver}" stroke-width="2" stroke-dasharray="4 4"/>`+sign(pb[0],pb[1]-2,'S','placed');
  const d1=S(T,pt('BD',.66)),c1=S(T,pt('BC',.5));
  s+=tag(d1[0]+24,d1[1]-6,'78%  Bridge West',{bar:C.ox,fs:13.5})+tag(c1[0]-70,c1[1]+34,'22%  Market',{bar:C.rust,fs:13.5});
  s+=halo(S(T,N.C)[0]-6,S(T,N.C)[1]+32,'Market')+halo(S(T,N.D)[0]-14,S(T,N.D)[1]+26,'Bridge West');
  s+=`<path d="M0,${dy} H${W} V${H} H0Z" fill="${C.bright}"/><rect y="${dy}" width="${W}" height="2.4" fill="${C.ink}"/>`;
  const x0=22,x1=W-22,px_=x0+(x1-x0)*11/32;
  s+=`<line x1="${x0}" y1="${dy+30}" x2="${x1}" y2="${dy+30}" stroke="${C.stone}" stroke-width="3"/><line x1="${x0}" y1="${dy+30}" x2="${px_}" y2="${dy+30}" stroke="${C.ink}" stroke-width="4"/>`;
  for(let i=0;i<=32;i+=4)s+=`<line x1="${x0+(x1-x0)*i/32}" y1="${dy+24}" x2="${x0+(x1-x0)*i/32}" y2="${dy+36}" stroke="${C.ink}" stroke-width="1.2"/>`;
  s+=`<rect x="${px_-7}" y="${dy+20}" width="14" height="20" fill="${C.ver}" stroke="${C.ink}" stroke-width="1.6"/><text x="${x0}" y="${dy+58}" font-family="${F.num}" font-size="13" fill="${C.soft}">0:00</text><text x="${x1}" y="${dy+58}" text-anchor="end" font-family="${F.num}" font-size="13" fill="${C.soft}">0:32</text>`;
  s+=`<text x="${x0}" y="${dy+(cp?80:90)}" font-family="${F.ui}" font-size="${cp?13.5:15}" fill="${C.ink}">Sign pointed south.</text><text x="${x0}" y="${dy+(cp?97:110)}" font-family="${F.ui}" font-size="${cp?13.5:15}" fill="${C.ink}"><tspan font-weight="700">7 of 9</tspan> took the narrow walkway.</text>`;
  const by=H-(cp?60:74);s+=btn(22,by,cp?136:170,cp?48:54,'Back to result','secondary')+btn(22+(cp?146:180),by,W-44-(cp?146:180),cp?48:54,'Try again','primary')}
 return`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs>${dx}</defs>${s}</svg>`}
module.exports={screen,C,F,glyph,person,sign,seal,lm,tag,routeLine,defs,cr,geo,nodesW};
if(require.main===module){
 console.log('contrast on stock/bright:',['ink','soft','verd','oliveD','mustD','ox','rustD'].map(k=>k+' '+cr(C[k],C.stock)+'/'+cr(C[k],C.bright)).join(' | '));
 const pageOf=(title,cap,list,W,H,sc)=>{const pw=Math.round(W*sc),ph=Math.round(H*sc);let h=`<html><body style="margin:0;background:#D9CAB0;font-family:Inter;color:${C.ink}"><div style="padding:30px 36px 26px;width:${list.length*(pw+18)}px"><div style="display:flex;gap:22px;align-items:baseline"><div style="font:700 30px 'Bitstream Charter',serif">${title}</div><div style="font-size:14.5px;max-width:1000px">${cap}</div></div><div style="display:flex;gap:18px;margin-top:20px">`;
  list.forEach(([k,nm])=>{h+=`<div><div style="width:${pw}px;height:${ph}px;box-shadow:0 8px 24px rgba(30,26,23,.34);overflow:hidden"><div style="transform:scale(${sc});transform-origin:0 0;width:${W}px;height:${H}px">${screen(k,W,H,'p')}</div></div><div style="margin-top:8px;font-size:14px;font-weight:600">${nm}</div></div>`});return h+'</div></div></body></html>'};
 const note='All numbers are mock data, not simulation output.';
 fs.writeFileSync('d2-main.html',pageOf('D2 · The Civic Press, revised','390×844. Warmer printshop palette, redrawn stamp people, authored landmarks, ink spread and paper tooth. '+note,[['title','Title'],['plan','Planning'],['run','Mid-round'],['atlas','Atlas zoom']],390,844,.9));
 fs.writeFileSync('d2-end.html',pageOf('D2 · After the round','Failure, the replay as a postmortem, and a win that feels like something. '+note,[['result','Result: short of the goal'],['replay','Replay: the decisive junction'],['win','Result: goal met']],390,844,.9));
 fs.writeFileSync('d2-320.html',pageOf('D2 · 320×568','Re-laid out for the small phone, not scaled. '+note,[['plan','Planning'],['run','Mid-round'],['atlas','Atlas zoom'],['result','Result'],['replay','Replay'],['win','Goal met']],320,568,.85));
}
