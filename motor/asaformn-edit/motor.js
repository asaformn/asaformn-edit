// asaformn-edit motoru. Adapted from Lemo-Opuscar (MIT): iskelet/IK/yaylar (Stick-figure Explainer),
// ink/marker/kutu fikirleri (Sketchnote). Tek dosya; sahne = JSON (bkz. sahneler/uyku-ornek.json).
// Sozlesme: window.READY, window.render(t), window.DUR. ?sahne=yol.json  ?alpha=1 (kagitsiz)
(() => {
const Q = new URLSearchParams(location.search), ALPHA = Q.get('alpha') === '1', W = 1920, H = 1080;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const C = { kagit:'#F7F3EC', koyu:'#EDE6DA', ink:'#1F2A44', soluk:'#5B6477', mavi:'#2F5D8A', mercan:'#D9533F', hardal:'#F2B544', nane:'#2E8A78',
  dot:'#D9D7D4', m1:'rgba(31,42,68,.14)', m2:'rgba(31,42,68,.26)', m3:'rgba(31,42,68,.42)' };
const MK = { mavi:'rgba(47,93,138,.6)', mercan:'rgba(217,83,63,.55)', hardal:'rgba(242,181,68,.75)', nane:'rgba(46,138,120,.55)', ink:C.m1 };
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), lerp=(a,b,t)=>a+(b-a)*t, seg=(t,a,b)=>clamp((t-a)/(b-a));
const ss=t=>{t=clamp(t);return t*t*(3-2*t)}, eo=t=>1-Math.pow(1-clamp(t),3), eio=ss;
function mulberry(s){return function(){s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const hs=str=>{let h=2166136261;for(const c of String(str)){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0};
let FADE=1, BOIL=0;
const ga=a=>{ctx.globalAlpha=a*FADE};

// ---------- fontlar ----------
const FD='../../fontlar/shantell-sans/Shantell_Sans-';
const FONTS={xb:['SSxb','Informal_Bouncy_ExtraBold'],b:['SSb','Informal_Bouncy_Bold'],m:['SSm','Informal_Medium'],r:['SSr','Informal_Regular']};
const fam=k=>FONTS[k][0];

// ---------- yardimcilar: yollar, sekiller ----------
function path(P,close=true){const p=new Path2D();p.moveTo(P[0][0],P[0][1]);for(let i=1;i<P.length;i++)p.lineTo(P[i][0],P[i][1]);if(close)p.closePath();return p}
const circ=(cx,cy,r,n=40)=>Array.from({length:n},(_,i)=>[cx+Math.cos(i/n*6.2832)*r,cy+Math.sin(i/n*6.2832)*r]);
const ell=(cx,cy,rx,ry,n=40)=>Array.from({length:n},(_,i)=>[cx+Math.cos(i/n*6.2832)*rx,cy+Math.sin(i/n*6.2832)*ry]);
function rrect(x,y,w,h,r,n=6){const P=[],cs=[[x+w-r,y+r,-90],[x+w-r,y+h-r,0],[x+r,y+h-r,90],[x+r,y+r,180]];
  for(const [cx,cy,a] of cs)for(let i=0;i<=n;i++){const q=(a+i/n*90)*Math.PI/180;P.push([cx+Math.cos(q)*r,cy+Math.sin(q)*r])}return P}
const shift=(P,dx,dy)=>P.map(p=>[p[0]+dx,p[1]+dy]);
function quad(A,Pc,B,n=12){const o=[];for(let i=0;i<=n;i++){const u=i/n,v=1-u;o.push([v*v*A[0]+2*u*v*Pc[0]+u*u*B[0],v*v*A[1]+2*u*v*Pc[1]+u*u*B[1]])}return o}
function thru(A,E,B,n=12,k=.85){const Pe=[2*E[0]-(A[0]+B[0])/2,2*E[1]-(A[1]+B[1])/2];return quad(A,[E[0]+(Pe[0]-E[0])*k,E[1]+(Pe[1]-E[1])*k],B,n)}
function smooth(P,per=8){ // Catmull-Rom
  const o=[];for(let i=0;i<P.length-1;i++){const p0=P[Math.max(0,i-1)],p1=P[i],p2=P[i+1],p3=P[Math.min(P.length-1,i+2)];
    for(let k=0;k<per;k++){const u=k/per,u2=u*u,u3=u2*u;o.push([0,1].map(d=>.5*((2*p1[d])+(-p0[d]+p2[d])*u+(2*p0[d]-5*p1[d]+4*p2[d]-p3[d])*u2+(-p0[d]+3*p1[d]-3*p2[d]+p3[d])*u3)))}}
  o.push(P[P.length-1]);return o}
function resample(P,step){
  const L=[0];for(let i=1;i<P.length;i++)L.push(L[i-1]+Math.hypot(P[i][0]-P[i-1][0],P[i][1]-P[i-1][1]));
  const tot=L[L.length-1];if(tot<1e-6)return[P[0],P[0]];
  const n=Math.max(2,Math.ceil(tot/step)+1),out=[];let j=1;
  for(let k=0;k<n;k++){const s=tot*k/(n-1);while(j<P.length-1&&L[j]<s)j++;const u=(s-L[j-1])/((L[j]-L[j-1])||1);out.push([P[j-1][0]+(P[j][0]-P[j-1][0])*u,P[j-1][1]+(P[j][1]-P[j-1][1])*u])}
  return out}

// ---------- kalem cizgisi: 3 katmanli sinus dalgasi, 2 gecis, 2 karede bir 3'luk boil ----------
function ink(P,o={}){
  const {w=7,amp=2.2,col=C.ink,seed=1,alpha=1,closed=false,passes=2}=o;
  const base=resample(closed?P.concat([P[0]]):P,4);
  for(let p=0;p<passes;p++){
    const r=mulberry(seed*131+p*977+7),a1=r()*6.28,a2=r()*6.28,a3=r()*6.28,a4=r()*6.28,A=amp*(p?1.5:1),ph=BOIL*2.1,D=[];let s=0;
    for(let i=0;i<base.length;i++){
      if(i)s+=Math.hypot(base[i][0]-base[i-1][0],base[i][1]-base[i-1][1]);
      const a=base[Math.max(0,i-1)],b=base[Math.min(base.length-1,i+1)];let nx=-(b[1]-a[1]),ny=b[0]-a[0];const l=Math.hypot(nx,ny)||1;nx/=l;ny/=l;
      const d=A*(.55*Math.sin(s*.011+a1+ph*.3)+.3*Math.sin(s*.047+a2+ph*.8)+.15*Math.sin(s*.21+a3+ph*1.3));
      D.push([base[i][0]+nx*d,base[i][1]+ny*d,s]);
    }
    ga(alpha*(p?.5:.94));ctx.strokeStyle=col;ctx.lineCap='round';ctx.lineJoin='round';
    for(let i=0;i<D.length-1;i+=5){const e=Math.min(D.length-1,i+5);ctx.beginPath();ctx.moveTo(D[i][0],D[i][1]);for(let j=i+1;j<=e;j++)ctx.lineTo(D[j][0],D[j][1]);
      ctx.lineWidth=w*(p?.62:1)*(1+.12*Math.sin(D[i][2]*.03+a4));ctx.stroke()}
  }
  ga(1)}

// ---------- marker: yari saydam, multiply, tek aci, ust uste binen yer koyulasir ----------
function hatch(P,col,o={}){
  const {w=16,ang=-.6,gap=.6,seed=3,dx=3,dy=2,edge=true}=o,r=mulberry(seed);
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const p of P){x0=Math.min(x0,p[0]);x1=Math.max(x1,p[0]);y0=Math.min(y0,p[1]);y1=Math.max(y1,p[1])}
  const cx=(x0+x1)/2,cy=(y0+y1)/2,R=Math.hypot(x1-x0,y1-y0)/2+w;
  ctx.save();ctx.translate(dx,dy);ctx.clip(path(P));ctx.globalCompositeOperation='multiply';ctx.strokeStyle=col;ctx.lineCap='round';ga(1);
  ctx.translate(cx,cy);ctx.rotate(ang);
  for(let o2=-R;o2<R;o2+=w*gap*(.85+.3*r())){ctx.lineWidth=w*(.9+.18*r());ctx.beginPath();ctx.moveTo(-R+(r()-.5)*12,o2);
    ctx.quadraticCurveTo(0,o2+(r()-.5)*8,R+(r()-.5)*12,o2+(r()-.5)*4);ctx.stroke()}
  ctx.restore();
  if(edge){ctx.save();ctx.translate(dx,dy);ctx.clip(path(P));ctx.globalCompositeOperation='multiply';ctx.strokeStyle=col;ga(.45);ctx.lineWidth=4;ctx.stroke(path(P));ctx.restore()}}
// kapali sekil: hilal golge (sag-alt) -> kagit dolgu -> renkli marker -> murekkep kontur
function shape(P,o={}){
  const {fill=C.kagit,mk=null,mk2=null,sh=9,w=7,seed=5,hw=16,amp=2.2}=o;
  if(sh)hatch(shift(P,sh,sh),C.m2,{w:hw,seed:seed+1,edge:false,ang:-.6});
  ga(1);ctx.fillStyle=fill;ctx.fill(path(P));
  if(mk)hatch(P,MK[mk]||mk,{w:hw,seed:seed+2,ang:-.55});
  if(mk2)hatch(P,mk2,{w:hw,seed:seed+3,ang:-.55,gap:.8});
  ink(P,{w,seed,closed:true,amp})}

// ---------- yazi ----------
function txt(s,x,y,f,size,col,a=1,align='left'){ctx.font=`${size}px ${fam(f)}`;ctx.fillStyle=col;ctx.textAlign=align;ctx.textBaseline='alphabetic';ga(a);ctx.fillText(s,x,y);ga(1)}
function txtIn(s,x,y,f,size,col,ts,t,align='left',slide=18){const u=(t-ts)/.4;if(u<=0)return;txt(s,x,y+(1-eo(u))*slide,f,size,col,ss(u*1.6),align)}
function wrap(s,f,size,maxw){ctx.font=`${size}px ${fam(f)}`;const out=[];let line='';for(const wd of s.split(' ')){const tr=line?line+' '+wd:wd;if(ctx.measureText(tr).width>maxw&&line){out.push(line);line=wd}else line=tr}out.push(line);return out}

// ---------- yay: ~%20 tasma ----------
function pop(dt,w=17,z=.46){if(dt<=0)return 0;const wd=w*Math.sqrt(1-z*z);return 1-Math.exp(-z*w*dt)*(Math.cos(wd*dt)+z*w/wd*Math.sin(wd*dt))}

// ---------- cop adam iskeleti (adapted from Lemo-Opuscar Stick-figure Explainer, MIT) ----------
const GEO={thigh:.215,shin:.215,hipH:.42,spine:.285,sh:.065,upper:.18,fore:.155,headR:.112,stance:.09};
const BASE={hx:0,hy:0,lean:0,bend:0,head:0,la:-.4,lb:.22,ra:.4,rb:-.22,lfx:0,lfy:0,rfx:0,rfy:0,hdx:0,hdy:0,rot:0};
const KEYS=Object.keys(BASE),LIE={rot:-Math.PI/2,la:-.07,lb:.04,ra:.07,rb:-.04,lfx:.09,rfx:-.09};
const POSES={stand:{},lie:LIE,lookup:{...LIE,lean:.38,head:.5,la:-1.1,lb:1.05,ra:-.45,rb:.85},raise:{ra:2.5,rb:.35},sit:{hy:-.17,lfx:.27,rfx:.31,la:-.2,ra:.25},
  look:{head:.35,lean:-.05},wave:{ra:2.4,rb:.6,head:.1}};
const dirv=a=>[Math.sin(a),Math.cos(a)];
function ik(H,F,L1,L2,side){let dx=F[0]-H[0],dy=F[1]-H[1],d=Math.hypot(dx,dy);const m=(L1+L2)*.9995;
  if(d>m){F=[H[0]+dx/d*m,H[1]+dy/d*m];dx=F[0]-H[0];dy=F[1]-H[1];d=m}
  const a=(L1*L1-L2*L2+d*d)/(2*d),h=Math.sqrt(Math.max(0,L1*L1-a*a)),px=H[0]+a*dx/d,py=H[1]+a*dy/d;let nx=-dy/d,ny=dx/d;
  if(nx*side<0){nx=-nx;ny=-ny}return[[px+nx*h,py+ny*h],F]}
function joints(S,p){const gy=GEO.hipH*S,Hp=[p.hx*S,gy-(GEO.hipH-p.hy)*S],sd=dirv(Math.PI-p.lean),N=[Hp[0]+sd[0]*GEO.spine*S,Hp[1]+sd[1]*GEO.spine*S];
  const mid=[(Hp[0]+N[0])/2,(Hp[1]+N[1])/2],perp=[-sd[1],sd[0]],Cc=[mid[0]+perp[0]*p.bend*S,mid[1]+perp[1]*p.bend*S],u=1-GEO.sh/GEO.spine;
  const Sh=[(1-u)*(1-u)*Hp[0]+2*(1-u)*u*Cc[0]+u*u*N[0],(1-u)*(1-u)*Hp[1]+2*(1-u)*u*Cc[1]+u*u*N[1]];
  const lag=clamp(p.hdx/GEO.headR*.9,-.35,.35),hd=dirv(Math.PI-(p.lean+p.head+lag)),hr=GEO.headR*S,Hd=[N[0]+hd[0]*hr,N[1]+hd[1]*hr];
  const arm=(a,b)=>{const e=dirv(a),E=[Sh[0]+e[0]*GEO.upper*S,Sh[1]+e[1]*GEO.upper*S],w=dirv(a+b);return[E,[E[0]+w[0]*GEO.fore*S,E[1]+w[1]*GEO.fore*S]]};
  const fL=[(-GEO.stance+p.lfx)*S,gy-p.lfy*S],fR=[(GEO.stance+p.rfx)*S,gy-p.rfy*S];
  return{Hp,N,Cc,Sh,Hd,hr,aL:arm(p.la,p.lb),aR:arm(p.ra,p.rb),lL:ik(Hp,fL,GEO.thigh*S,GEO.shin*S,-1),lR:ik(Hp,fR,GEO.thigh*S,GEO.shin*S,1)}}
// yaylar: kalca hizli, ust kol orta, on kol yavas, kafa en gevsek; sabit adim, t0'dan baslar -> her t ayni
const SPR={hx:[20,.8],hy:[24,.62],lean:[13,.6],bend:[12,.55],head:[9,.42],la:[13,.58],ra:[13,.58],lb:[9.5,.46],rb:[9.5,.46],lfx:[30,.85],lfy:[30,.85],rfx:[30,.85],rfy:[30,.85],rot:[9,.7]},HEADSPR=[16,.38];
function simulate(target,t0,t1){
  const dt=1/480,every=4,out=[],p0=target(t0),s={p:{...p0},v:{},hp:null,hv:[0,0]};for(const k in SPR)s.v[k]=0;
  const rh=p=>{const hy=GEO.hipH-p.hy;return[p.hx+Math.sin(p.lean)*GEO.spine+Math.sin(p.lean+p.head)*GEO.headR,hy+Math.cos(p.lean)*GEO.spine+Math.cos(p.lean+p.head)*GEO.headR]};
  let step=0;for(let t=t0;t<=t1;t+=dt,step++){
    if(step%every===0)out.push({...s.p});const tg=target(t);
    for(const k in SPR){const[w,z]=SPR[k];s.v[k]+=(w*w*(tg[k]-s.p[k])-2*z*w*s.v[k])*dt;s.p[k]+=s.v[k]*dt}
    const R=rh(s.p);if(!s.hp)s.hp=[...R];const[w,z]=HEADSPR;
    for(let q=0;q<2;q++){s.hv[q]+=(w*w*(R[q]-s.hp[q])-2*z*w*s.hv[q])*dt;s.hp[q]+=s.hv[q]*dt}
    s.p.hdx=clamp(s.hp[0]-R[0],-.03,.03);s.p.hdy=clamp(s.hp[1]-R[1],-.03,.03)}
  return{at(t){const f=clamp((t-t0)*120,0,out.length-1.001),i=Math.floor(f),u=f-i,A=out[i],B=out[i+1],q={};for(const k of KEYS)q[k]=lerp(A[k],B[k],u);return q}}}
function figTarget(el){ // poses: [[t,'ad'|{kismi}],..]; kismi olan onceki pozun ustune biner
  const ks=[];let cur={...BASE};for(const[t,p]of el.poses){cur=typeof p==='string'?{...BASE,...POSES[p]}:{...cur,...p};ks.push([t,cur])}
  const ph=(hs(el.id)%100)/16;
  return t=>{let c=ks[0][1];for(const k of ks)if(k[0]<=t)c=k[1];const r={...c},b=Math.sin(t*6.2832/3.4+ph);r.hy+=.004*b;r.lean+=.005*b;return r}}
function drawFigure(el,t){
  const p=el.sim.at(t),S=el.S,j=joints(S,p),w=el.w||Math.max(5,S*.0205),col=el.col||C.ink,sd=hs(el.id),hid=el.hide||{};
  ctx.save();ctx.translate(j.Hp[0],j.Hp[1]);ctx.rotate(p.rot);ctx.translate(-j.Hp[0],-j.Hp[1]);
  ga(1);ctx.fillStyle=C.kagit;ctx.beginPath();ctx.arc(j.Hd[0],j.Hd[1],j.hr,0,6.2832);ctx.fill();
  ink(thru(j.lL[1],j.lL[0],j.Hp).concat(thru(j.Hp,j.lR[0],j.lR[1]).slice(1)),{w,col,seed:sd+1});
  let arms=[];if(!hid.L)arms=arms.concat(thru(j.aL[1],j.aL[0],j.Sh));if(!hid.R)arms=arms.concat(thru(j.Sh,j.aR[0],j.aR[1]).slice(arms.length?1:0));
  if(arms.length>1){if(hid.L||hid.R)ink(arms,{w,col,seed:sd+2});else ink(arms,{w,col,seed:sd+2})}
  const a0=Math.atan2(j.N[1]-j.Hd[1],j.N[0]-j.Hd[0]),sp=quad(j.Hp,j.Cc,j.N,10);
  for(let i=1;i<=40;i++){const a=a0+i/40*6.2832;sp.push([j.Hd[0]+Math.cos(a)*j.hr,j.Hd[1]+Math.sin(a)*j.hr])}
  ink(sp,{w,col,seed:sd+3});ctx.restore();el._j=j}

// ---------- ikonlar ----------
const R2=mulberry;
function crescent(R,r,ox,oy){const A=[],B=[];for(let i=0;i<72;i++){const a=i/72*6.2832,p=[Math.cos(a)*R,Math.sin(a)*R];if(Math.hypot(p[0]-ox,p[1]-oy)>r)A.push(p);
  const q=[ox+Math.cos(a)*r,oy+Math.sin(a)*r];if(Math.hypot(q[0],q[1])<R)B.push(q)}
  const rot=L=>{let k=0;for(let i=0;i<L.length;i++)if(Math.hypot(L[i][0]-L[(i+L.length-1)%L.length][0],L[i][1]-L[(i+L.length-1)%L.length][1])>R*.2){k=i;break}return L.slice(k).concat(L.slice(0,k))};
  const a=rot(A),b=rot(B),g=(x,y)=>Math.hypot(x[0]-y[0],x[1]-y[1]);return g(a[a.length-1],b[0])<g(a[a.length-1],b[b.length-1])?a.concat(b):a.concat(b.reverse())}
const D={};
D.bed=(el,t,dt)=>{const s=hs(el.id);
  shape(rrect(-280,56,560,32,10),{seed:s+1,w:6,sh:0,mk:'ink',hw:12});
  shape(rrect(-250,88,26,44,6),{seed:s+2,w:6,sh:0,hw:10});shape(rrect(224,88,26,44,6),{seed:s+3,w:6,sh:0,hw:10});
  shape(rrect(262,-34,24,156,9),{seed:s+4,w:7,sh:0,mk:'ink',hw:12});
  shape(rrect(-300,-150,30,272,10),{seed:s+5,w:8,sh:9,mk:'ink',hw:14});
  shape(rrect(-270,0,540,60,16),{seed:s+6,fill:C.koyu,w:8,sh:9,hw:14,mk:'ink'});
  shape(rrect(-258,-34,150,40,18),{seed:s+7,w:7,sh:0,hw:12})};
D.blanket=(el,t)=>{const s=hs(el.id),P=smooth([[-20,6],[-16,-40],[10,-68],[70,-78],[170,-70],[250,-48],[266,6]],6).concat([[266,16],[-20,16]]);
  shape(P,{seed:s,fill:C.koyu,mk:'mavi',w:8,sh:0,hw:20});
  for(const f of[[[24,-64],[44,-32],[34,0]],[[70,-72],[95,-36],[80,0]],[[170,-66],[190,-34],[178,0]]])ink(thru(f[0],f[1],f[2]),{w:5,col:C.ink,seed:s+9,passes:1,alpha:.55,amp:1.2});
  ink([[-18,-8],[268,-8]],{w:4,seed:s+4,passes:1,col:C.ink,alpha:.35,amp:1.5})};
D.moon=(el,t)=>{const s=hs(el.id);shape(crescent(62,52,32,-14),{seed:s,fill:C.kagit,mk:'ink',w:7,sh:8,hw:14});
  for(const[x,y,r]of[[96,-52,13],[-20,-96,10],[100,34,8]]){ink([[x-r,y],[x+r,y]],{w:5,seed:s+x,passes:1,amp:.8});ink([[x,y-r],[x,y+r]],{w:5,seed:s+y,passes:1,amp:.8})}};
D.clock=(el,t,dt)=>{const s=hs(el.id),R=72;shape(circ(0,0,R),{seed:s,fill:C.koyu,w:8,hw:14,mk:'ink'});
  for(let i=0;i<4;i++){const a=i*Math.PI/2,c=Math.cos(a),n=Math.sin(a);ink([[c*(R-18),n*(R-18)],[c*(R-8),n*(R-8)]],{w:5,seed:s+i,passes:1,amp:.5})}
  const h=el.hour*Math.PI/6;ink([[0,0],[Math.sin(h)*38,-Math.cos(h)*38]],{w:8,seed:s+7,passes:1,amp:.8});ink([[0,0],[0,-56]],{w:6,seed:s+8,passes:1,amp:.8});
  ga(1);ctx.fillStyle=C.ink;ctx.beginPath();ctx.arc(0,0,6,0,6.2832);ctx.fill();
  txtIn(el.label,0,R+62,'b',46,C.ink,el.t+.35,t,'center')};
D.brain=(el,t)=>{const s=hs(el.id),rx=135,ry=100,P=Array.from({length:72},(_,i)=>{const a=i/72*6.2832,k=1+.06*Math.cos(8*a+.4);return[Math.cos(a)*rx*k,Math.sin(a)*ry*k*(Math.sin(a)>0?.92:1)]});
  shape(P,{seed:s,fill:C.koyu,mk:'ink',w:8,hw:18});
  ink(smooth([[0,-96],[10,-60],[-8,-30],[8,0],[-4,34],[0,80]],6),{w:6,seed:s+1,passes:1,amp:1.2});
  const L=[[[-100,-45],[-70,-72],[-42,-50],[-20,-70]],[[-112,10],[-82,-12],[-56,16],[-30,-6]],[[-86,52],[-60,30],[-36,52],[-16,36]]];
  L.forEach((f,i)=>{ink(smooth(f,6),{w:5,seed:s+3+i,passes:1,amp:1,alpha:.8});ink(smooth(f.map(p=>[-p[0],p[1]+4]),6),{w:5,seed:s+9+i,passes:1,amp:1,alpha:.8})})};
D.dots=(el,t)=>{const s=hs(el.id);for(const[i,d]of el.items.entries()){const sc=pop(t-d.t);if(sc<.01)continue;ctx.save();ctx.translate(d.x,d.y);ctx.scale(sc,sc);
  const r=d.r||13;shape(circ(0,0,r,24),{seed:s+i*7,fill:C.kagit,mk:d.col&&d.col!=='ink'?d.col:null,w:d.col&&d.col!=='ink'?4:5,sh:d.col&&d.col!=='ink'?0:0,hw:Math.max(6,r*.7),amp:1,mk2:d.col==='hardal'?MK.hardal:null});ctx.restore()}};
D.cup=(el,t)=>{const s=hs(el.id),B=[[-58,-48],[-52,10],[-40,44],[-20,56],[20,56],[40,44],[52,10],[58,-48]];
  ink(smooth([[-96,70],[-60,80],[0,84],[60,80],[96,70]],6),{w:7,seed:s+1,passes:2,amp:1.2});
  ink(smooth([[58,-34],[96,-36],[102,6],[50,26]],6),{w:8,seed:s+2});
  shape(smooth(B,5).concat([[58,-48]]),{seed:s,fill:C.koyu,mk:'ink',w:8,hw:14,sh:8});
  shape(ell(0,-48,58,13),{seed:s+3,fill:C.koyu,mk:C.m3,mk2:C.m3,w:6,sh:0,hw:10,amp:1});
  for(const[i,x]of[-22,22].entries())ink(smooth([[x,-78],[x+12,-98],[x-10,-118],[x+8,-140]],6),{w:5,col:C.soluk,seed:s+5+i,passes:1,amp:.8})};
D.obruk=(el,t,dt)=>{const s=hs(el.id),rx=el.rx||560,ry=el.ry||170,fy=el.fy||60,frx=rx*.66,fry=ry*.5;
  const rim=Array.from({length:72},(_,i)=>{const a=i/72*6.2832,k=1+.035*Math.sin(3*a+1.3)+.02*Math.sin(7*a+.6);return[Math.cos(a)*rx*k,Math.sin(a)*ry*k]});
  const flo=Array.from({length:48},(_,i)=>{const a=i/48*6.2832,k=1+.04*Math.sin(4*a+.7);return[Math.cos(a)*frx*k,fy+Math.sin(a)*fry*k]});
  const arc=(a0,a1,fx,fyy,cy,n=14)=>Array.from({length:n+1},(_,i)=>{const a=lerp(a0,a1,i/n);return[Math.cos(a)*fx,cy+Math.sin(a)*fyy]});
  hatch(shift(rim,10,12),C.m2,{w:18,seed:s+1,edge:false,ang:-.6});
  ga(1);ctx.fillStyle=C.koyu;ctx.fill(path(rim));
  ctx.save();ctx.clip(path(rim));
  hatch(rim,C.m1,{w:16,seed:s+2,ang:1.45,dx:0,dy:0,edge:false});
  hatch(ell(0,fy,frx*1.1,fry*1.2,40),C.m1,{w:14,seed:s+4,ang:1.5,dx:0,dy:0,edge:false});
  ga(1);ctx.fillStyle=C.koyu;ctx.fill(path(flo));
  hatch(flo,C.m2,{w:16,gap:.8,seed:s+5,ang:-.5,dx:0,dy:0,edge:false});
  for(let i=0;i<15;i++){const a=Math.PI*(1.05+.9*i/14),j=(mulberry(s+i)()-.5)*.05;
    const p=[Math.cos(a)*rx*.99,Math.sin(a)*ry*.99],q=[Math.cos(a+j)*frx*1.02,fy+Math.sin(a+j)*fry*1.02],m=[(p[0]+q[0])/2+(i%2?9:-9),(p[1]+q[1])/2];
    ink(quad(p,m,q,8),{w:4,seed:s+20+i,passes:1,alpha:.5,amp:1.2})}
  for(const[k,al]of[[.42,.5],[.72,.4]]){const fx=lerp(rx,frx,k),fyy=lerp(ry,fry,k),cy=lerp(0,fy,k);ink(arc(Math.PI*1.12,Math.PI*1.88,fx*.97,fyy*.97,cy),{w:4,seed:s+60+k*10,passes:1,alpha:al,amp:1.6})}
  ink(flo,{w:5,seed:s+7,closed:true,passes:1,alpha:.7,amp:1.4});
  ctx.restore();
  ink(arc(Math.PI*.08,Math.PI*.92,rx*.98,ry*.98,15),{w:5,seed:s+8,passes:1,alpha:.55,amp:1.5});
  ink(rim,{w:9,seed:s,closed:true,amp:2.6});
  ink(smooth([[-rx*1.75,26],[-rx*1.45,18],[-rx*1.2,4],[-rx*1.02,0]],6),{w:7,seed:s+9,amp:2});
  ink(smooth([[rx*1.02,0],[rx*1.2,6],[rx*1.5,20],[rx*1.75,24]],6),{w:7,seed:s+10,amp:2});
  for(const[x,y,r]of[[-rx*.62,-ry*.93,15],[-rx*.5,-ry*.97,10],[rx*.55,-ry*.97,13],[rx*1.1,-6,12]])
    shape(ell(x,y,r*1.4,r,16).map((p,i)=>[p[0],p[1]+(i%3-1)*1.5]),{seed:s+30+(x|0),fill:C.koyu,mk:'ink',w:5,sh:5,hw:9,amp:1});
  for(const[i,x]of[-rx*.78,rx*.7].entries()){const y=-ry*Math.sqrt(1-Math.pow(x/rx/1.03,2))*1.02-2;
    for(const[j,a]of[-.5,0,.5].entries())ink([[x,y],[x+Math.sin(a)*34,y-Math.cos(a)*34*(j==1?1.2:1)]],{w:5,seed:s+40+i*3+j,passes:1,amp:.8})}
  if(el.warn!=null&&t>=el.warn)ink(rim,{w:10,col:C.mercan,seed:s+50,closed:true,alpha:ss((t-el.warn)/.3),amp:2.6})};
D.ev=(el,t)=>{const s=hs(el.id);
  shape(rrect(-50,-62,100,62,6),{seed:s,fill:C.kagit,mk:'ink',w:6,sh:6,hw:10,amp:1.2});
  shape([[-64,-58],[0,-114],[64,-58]],{seed:s+1,fill:C.koyu,mk:'ink',w:6,sh:0,hw:10,amp:1.2});
  shape(rrect(-14,-36,28,36,4),{seed:s+2,fill:C.koyu,w:5,sh:0,amp:.8});
  ink([[24,-46],[40,-46],[40,-30],[24,-30],[24,-46]],{w:4,seed:s+3,passes:1,amp:.6})};
D.check=(el,t)=>{const s=hs(el.id),z=el.size||60;ink(thru([-z*.6,0],[-z*.15,z*.55],[z*.7,-z*.7],10,1),{w:14,col:C.nane,seed:s,amp:1.4});};
D.cross=(el,t)=>{const s=hs(el.id),z=el.size||50;ink([[-z,-z],[z,z]],{w:14,col:C.mercan,seed:s,amp:1.4});ink([[z,-z],[-z,z]],{w:14,col:C.mercan,seed:s+1,amp:1.4})};
D.arrow=(el,t)=>{const L=el.len,h=el.h||56,P=[[0,-h*.26],[L-h*.8,-h*.26],[L-h*.8,-h*.62],[L,0],[L-h*.8,h*.62],[L-h*.8,h*.26],[0,h*.26]];
  ctx.rotate(el.ang||0);shape(P,{seed:hs(el.id),fill:C.kagit,mk:'mavi',w:7,sh:7,hw:14})};
D.ticks=(el,t)=>{const s=hs(el.id);el.angs.forEach((a,i)=>{const sc=pop(t-el.t-i*.06);if(sc<.01)return;const r0=el.r0*sc,r1=(el.r0+el.len)*sc,c=Math.cos(a),n=Math.sin(a);ink([[c*r0,n*r0],[c*r1,n*r1]],{w:7,seed:s+i,passes:2,amp:1})})};
D.text=(el,t)=>{const lines=Array.isArray(el.text)?el.text:[el.text];lines.forEach((l,i)=>txtIn(l,0,i*(el.lh||(el.size||32)*1.3),el.font||'m',el.size||32,C[el.col]||el.col||C.ink,el.t+i*.22,t,el.align||'left',el.slide||18))};
D.card=(el,t,dt)=>{const w=el._w,h=el._h,P=rrect(-w/2,-h/2,w,h,26,7);shape(P,{seed:hs(el.id),fill:C.koyu,w:8,sh:10,hw:16,mk:null});
  const x=-w/2+36;let y=-h/2+36+40;txtIn(el.title,x,y,'b',46,C.ink,el.t+.25,t);y+=22+34;
  el._lines.forEach((l,i)=>{txtIn(l,x,y+i*46,'m',34,C.ink,el.t+.55+i*.22,t)});
  if(el.note)txtIn(el.note,x,y+el._lines.length*46+8,'r',28,C.soluk,el.t+.55+el._lines.length*.22,t)};
D.meter=(el,t,dt)=>{const w=el.w||460,h=el.h||56,sd=hs(el.id),P=rrect(-w/2,-h/2,w,h,h/2-4,6),f=(w-26)*(el.fill||1)*eo((dt-.3)/1);
  shape(P,{seed:sd,fill:C.koyu,w:7,sh:8,hw:14,mk:null});
  if(f>8){const I=rrect(-w/2+13,-h/2+11,f,h-22,h/2-15,5);hatch(I,MK.hardal,{w:12,seed:sd+4,ang:-.55,dx:0,dy:0})}
  ink(P,{w:7,seed:sd,closed:true});txtIn(el.label,0,h/2+46,'m',32,C.soluk,el.t+.9,t,'center')};
D.ribbon=(el,t)=>{const w=el._w,h=el._h,n=h*.28,P=[[-w/2,-h/2],[w/2,-h/2],[w/2-n,0],[w/2,h/2],[-w/2,h/2],[-w/2+n,0]];
  shape(P,{seed:hs(el.id),fill:C.mavi,mk:C.m1,w:7,sh:9,hw:16});txt(el.text,0,h*.18,'xb',el.size||56,C.kagit,1,'center')};
D.link=(el,t)=>{const A=ELS[el.a],B=ELS[el.b];if(!A._j||!B._j)return;const ra=el.ha==='L'?A._j.aL:A._j.aR,rb=el.hb==='L'?B._j.aL:B._j.aR,sa=A._j.Sh,sb=B._j.Sh;
  const M=[(ra[1][0]+rb[1][0]+A.x+B.x)/2,(ra[1][1]+rb[1][1]+A.y+B.y)/2];const pa=(F,j)=>[F.x+j[0],F.y+j[1]];
  const P=thru(pa(A,sa),pa(A,ra[0]),M).concat(thru(M,pa(B,rb[0]),pa(B,sb)).slice(1));ctx.save();ctx.translate(-el.x,-el.y);
  ink(P,{w:el.w||9,seed:hs(el.id)});const d=t-el.t;if(d<.6){ink(circ(M[0],M[1],10+d*140,24),{w:4,seed:3,passes:1,alpha:1-d/.6})}ctx.restore()};
D.ground=(el,t)=>{const P=[];for(let x=el.x1;x<=el.x2;x+=8){let y=el.y;for(const p of el.pulses||[]){const d=t-p.t0;if(d>0&&d<3){const c=p.x0+p.speed*d;y-=(p.amp||24)*Math.exp(-Math.pow((x-c)/50,2))*(1-d/3)}}P.push([x-el.x,y-el.y])}
  ink(P,{w:7,seed:hs(el.id),amp:2})};
const NOPOP={ticks:1,text:1,card:1,dots:1,link:1,ground:1,figure:0};

// ---------- sahne ----------
let SC=null,ELS={};
window.DUR=10;window.READY=false;
function prepare(sc){SC=sc;window.DUR=sc.dur;ELS={};
  for(const[i,el]of sc.els.entries()){el.id=el.id||('e'+i);ELS[el.id]=el;
    if(el.type==='figure'){const tg=figTarget(el);el.sim=simulate(tg,el.t-.3,sc.dur+.3)}
    if(el.type==='card'){el._w=el.w||600;el._lines=wrap(el.body||'','m',34,el._w-72);el._h=36+40+22+34+(el._lines.length-1)*46+(el.note?40:0)+34;el.ox=el._w/2;el.oy=el._h/2}
    if(el.type==='ribbon'){ctx.font=`56px ${fam('xb')}`;el.size=el.size||56;ctx.font=`${el.size}px ${fam('xb')}`;el._w=ctx.measureText(el.text).width+130;el._h=el.size*1.7;el.ox=el._w/2;el.oy=el._h/2}}}
const camKeys=()=>SC.camera;
function cam(t){const K=camKeys();if(t<=K[0][0])return K[0].slice(1);for(let i=0;i<K.length-1;i++)if(t<=K[i+1][0]){const u=eio(seg(t,K[i][0],K[i+1][0]));
  return[lerp(K[i][1],K[i+1][1],u),lerp(K[i][2],K[i+1][2],u),Math.exp(lerp(Math.log(K[i][3]),Math.log(K[i+1][3]),u))]}return K[K.length-1].slice(1)}
let TEX=null;
function texture(){if(TEX)return TEX;const c=document.createElement('canvas');c.width=c.height=256;const g=c.getContext('2d'),r=mulberry(11);
  for(let i=0;i<1400;i++){g.fillStyle=`rgba(31,42,68,${.012+r()*.02})`;g.fillRect(r()*256,r()*256,1+r()*1.5,1+r()*1.5)}return TEX=ctx.createPattern(c,'repeat')}
window.render=function(t){
  BOIL=Math.floor(Math.round(t*60)/2)%3;ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';FADE=1;ctx.clearRect(0,0,W,H);
  const[cx,cy,z]=cam(t),tx=W/2-cx*z,ty=H/2-cy*z;
  if(!ALPHA){ctx.fillStyle=C.kagit;ctx.fillRect(0,0,W,H);ctx.fillStyle=texture();ctx.fillRect(0,0,W,H);
    ctx.setTransform(z,0,0,z,tx,ty);ctx.fillStyle=C.dot;ctx.beginPath();const g=26,x0=Math.floor((cx-W/2/z)/g)*g,x1=cx+W/2/z,y0=Math.floor((cy-H/2/z)/g)*g,y1=cy+H/2/z;
    for(let x=x0;x<=x1;x+=g)for(let y=y0;y<=y1;y+=g){ctx.moveTo(x+1.3,y);ctx.arc(x,y,1.3,0,6.2832)}ctx.fill()}
  for(const el of SC.els)if(el.type==='figure')el.hide=null;
  for(const el of SC.els)if(el.type==='link'&&t>=el.t){const f=ELS[el.a],g=ELS[el.b];(f.hide=f.hide||{})[el.ha||'R']=true;(g.hide=g.hide||{})[el.hb||'L']=true}
  for(const el of SC.els){const dt=t-el.t;if(dt<0||(el.out!=null&&t>el.out+.35))continue;
    let s=NOPOP[el.type]?1:pop(dt,el.pw||17,el.pz||.46)*(el.scale||1),a=el.type==='card'?ss(dt/.3):Math.min(1,dt/.12);if(NOPOP[el.type]&&!el.slide&&el.type!=='card')a=1;
    if(el.out!=null)a*=1-ss((t-el.out)/.3);if(s<.005||a<=0)continue;
    ctx.setTransform(z,0,0,z,tx,ty);if(el.space==='screen')ctx.setTransform(1,0,0,1,0,0);
    ctx.save();let ex=el.x+(el.ox||0),ey=el.y+(el.oy||0);if(el.type==='card'){const k=1-eo(dt/.5);ex+=k*-70}
    ctx.translate(ex,ey);ctx.scale(s,s);FADE=a;ctx.globalCompositeOperation='source-over';
    if(el.type==='figure')drawFigure(el,t);else D[el.type](el,t,dt);ctx.restore();FADE=1}
  ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over'};
window.loadScene=prepare;
Promise.all(Object.values(FONTS).map(([n,f])=>new FontFace(n,`url(${FD}${f}.ttf)`).load().then(ff=>document.fonts.add(ff))))
 .then(()=>Q.get('sahne')?fetch(Q.get('sahne')).then(r=>r.json()):window.SCENE)
 .then(sc=>{if(sc)prepare(sc);window.READY=true}).catch(e=>{window.ERR=String(e);console.error(e)});
})();
