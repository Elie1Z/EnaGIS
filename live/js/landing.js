/* Local geographic globe; no imagery or inferred opportunity data is fabricated. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id), shell = $('landing'), canvas = $('earth'), ctx = canvas.getContext('2d');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const rad = Math.PI / 180;
  const rings = window.ENA_WORLD.countries.features.flatMap(f => (f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates).map(p => p[0].filter((_, i) => i % 2 === 0).map(([lon, lat]) => [lon * rad, lat * rad])));
  let width=0,height=0,lon=18,lat=12,paused=reduced.matches,focused=false,drag=null,selection=null,flight=null,frame=0,last=0,request=0,transitioning=false;
  const stars = Array.from({length:140},(_,i)=>({x:((i*7919)%1009)/1009,y:((i*3571)%1013)/1013,a:.12+(i%5)*.07}));
  function size(){width=innerWidth;height=innerHeight;const d=Math.min(devicePixelRatio||1,2);canvas.width=width*d;canvas.height=height*d;ctx.setTransform(d,0,0,d,0,0);}
  function project(a,b){const dl=a-lon*rad, p=lat*rad;return [Math.cos(b)*Math.sin(dl),Math.cos(p)*Math.sin(b)-Math.sin(p)*Math.cos(b)*Math.cos(dl),Math.sin(p)*Math.sin(b)+Math.cos(p)*Math.cos(b)*Math.cos(dl)];}
  function draw(now){
    if(shell.hidden)return;
    const dt=Math.min((now-last)/1000,.05);last=now;
    if(flight){const t=Math.min(1,(now-flight.time)/1400),e=1-Math.pow(1-t,3);lon=flight.lon+flight.dx*e;lat=flight.lat+(flight.toLat-flight.lat)*e;if(t===1)flight=null;}
    else if(!paused&&!focused&&!drag&&!selection&&!document.hidden)lon+=dt*2.3;
    ctx.clearRect(0,0,width,height);
    const mobile=width<800,cx=width*(mobile?.78:.77),cy=height*(mobile?.29:.51),radius=Math.min(width*(mobile?.59:.32),height*.43);
    stars.forEach(s=>{ctx.fillStyle=`rgba(177,210,230,${s.a})`;ctx.fillRect(s.x*width,s.y*height,1,1);});
    let halo=ctx.createRadialGradient(cx,cy,radius*.8,cx,cy,radius*1.22);halo.addColorStop(0,'#195e5e18');halo.addColorStop(.68,'#23869032');halo.addColorStop(1,'#0c252500');ctx.fillStyle=halo;ctx.fillRect(cx-radius*1.3,cy-radius*1.3,radius*2.6,radius*2.6);
    ctx.save();ctx.beginPath();ctx.arc(cx,cy,radius,0,Math.PI*2);ctx.clip();
    const ocean=ctx.createRadialGradient(cx-radius*.4,cy-radius*.4,0,cx,cy,radius*1.5);ocean.addColorStop(0,'#184654');ocean.addColorStop(.6,'#0a2637');ocean.addColorStop(1,'#020911');ctx.fillStyle=ocean;ctx.fillRect(cx-radius,cy-radius,2*radius,2*radius);
    function path(points,fill){ctx.beginPath();let pen=false;points.forEach(([a,b])=>{const [x,y,z]=project(a,b);if(z<0){pen=false;return;}if(!pen){ctx.moveTo(cx+x*radius,cy-y*radius);pen=true;}else ctx.lineTo(cx+x*radius,cy-y*radius);});if(fill){ctx.fillStyle='#285b5d';ctx.fill();}ctx.stroke();}
    ctx.lineWidth=.45;ctx.strokeStyle='#85c9c51c';for(let y=-60;y<=60;y+=30)path(Array.from({length:181},(_,i)=>[(i*2-180)*rad,y*rad]),false);for(let x=-180;x<180;x+=30)path(Array.from({length:91},(_,i)=>[x*rad,(i*2-90)*rad]),false);
    ctx.strokeStyle='#83b5a978';ctx.lineWidth=.65;rings.forEach(p=>path(p,true));
    const shade=ctx.createLinearGradient(cx-radius,cy-radius,cx+radius,cy+radius*.4);shade.addColorStop(0,'#73eedb0a');shade.addColorStop(.5,'#030d1910');shade.addColorStop(1,'#000710ee');ctx.fillStyle=shade;ctx.fillRect(cx-radius,cy-radius,2*radius,2*radius);
    if(selection){const a=selection.lon??(selection.bbox[0]+selection.bbox[2])/2,b=selection.lat??(selection.bbox[1]+selection.bbox[3])/2;const [x,y,z]=project(a*rad,b*rad);if(z>0){ctx.strokeStyle='#76f2bd';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(cx+x*radius,cy-y*radius,13,0,7);ctx.stroke();ctx.fillStyle='#c0ffe3';ctx.beginPath();ctx.arc(cx+x*radius,cy-y*radius,4,0,7);ctx.fill();}}
    ctx.restore();ctx.strokeStyle='#92e4d52b';ctx.lineWidth=1;ctx.beginPath();ctx.arc(cx,cy,radius,0,7);ctx.stroke();
    if(mobile){const fade=ctx.createLinearGradient(0,height*.15,0,height*.7);fade.addColorStop(0,'#030b1520');fade.addColorStop(1,'#030b15ff');ctx.fillStyle=fade;ctx.fillRect(0,0,width,height);}
    frame=requestAnimationFrame(draw);
  }
  function motion(){ $('orbit-motion').textContent=paused?'Resume rotation':'Pause rotation';$('orbit-motion').setAttribute('aria-pressed',String(paused));}
  $('orbit-motion').onclick=()=>{paused=!paused;selection=null;flight=null;$('orbit-selection').hidden=true;motion();};
  reduced.addEventListener('change',()=>{paused=reduced.matches;motion();});
  canvas.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,lon,lat};flight=null;canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;lon=drag.lon-(e.clientX-drag.x)*.22;lat=Math.max(-70,Math.min(70,drag.lat+(e.clientY-drag.y)*.15));});
  canvas.addEventListener('pointerup',()=>{drag=null;});canvas.addEventListener('pointercancel',()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();paused=true;flight=null;lon+=e.key==='ArrowRight'?8:e.key==='ArrowLeft'?-8:0;lat=Math.max(-70,Math.min(70,lat+(e.key==='ArrowUp'?5:e.key==='ArrowDown'?-5:0)));motion();});
  $('orbit-query').addEventListener('focus',()=>{focused=true;});$('orbit-query').addEventListener('blur',()=>{focused=false;});
  function select(area){selection=area;const target=area.lon??(area.bbox[0]+area.bbox[2])/2;flight=reduced.matches?null:{time:performance.now(),lon,lat,dx:((target-lon)%360+540)%360-180,toLat:area.lat??(area.bbox[1]+area.bbox[3])/2};if(reduced.matches){lon=target;lat=area.lat??(area.bbox[1]+area.bbox[3])/2;}$('orbit-results').replaceChildren();$('orbit-selection').hidden=false;$('orbit-place').textContent=area.display_name||area.name;$('orbit-status').textContent='Your place is in view. Explore the map, then choose an activity.';}
  $('orbit-reset').onclick=()=>{selection=null;flight=null;$('orbit-selection').hidden=true;$('orbit-query').focus();};
  $('orbit-query').addEventListener('input',()=>{request++;selection=null;flight=null;$('orbit-selection').hidden=true;$('orbit-results').replaceChildren();});
  $('orbit-search').addEventListener('submit',async e=>{e.preventDefault();const q=$('orbit-query').value.trim();if(!q)return;const id=++request;focused=true;$('orbit-results').replaceChildren();$('orbit-selection').hidden=true;$('orbit-status').textContent='Finding your place…';try{const coords=q.match(/^\s*(-?\d+(?:\.\d+)?)\s*[,;]\s*(-?\d+(?:\.\d+)?)\s*$/);let results;if(coords){const a=+coords[1],b=+coords[2];if(Math.abs(a)>85||Math.abs(b)>180)throw Error('Use latitude between −85 and 85 and longitude between −180 and 180.');const d=.025;results=[{...EnaSources.areaFromView([Math.max(-180,b-d),a-d,Math.min(180,b+d),a+d],`Around ${a}, ${b}`),lat:a,lon:b,display_name:`Selected coordinates · approximately 5 km study window`}];}else results=await EnaSources.geocode(q);if(id!==request)return;if(!results.length){$('orbit-status').textContent='No matching place yet. Try adding its country or enter coordinates.';return;}$('orbit-status').textContent='Choose the place you mean.';results.forEach(area=>{const b=document.createElement('button');b.type='button';b.textContent=area.name;const small=document.createElement('small');small.textContent=area.display_name;b.append(small);b.onclick=()=>select(area);$('orbit-results').append(b);});}catch(err){if(id===request)$('orbit-status').textContent=`${err.message||'Search unavailable'}. You can also open a saved analysis.`;}});
  function dismiss(){shell.hidden=true;document.body.classList.remove('landing-open');cancelAnimationFrame(frame);EnaApp.map().resize();}
  $('orbit-enter').onclick=()=>{if(!selection||transitioning)return;transitioning=true;EnaApp.previewArea(selection);document.body.classList.remove('landing-open');EnaApp.map().resize();shell.classList.add('departing');setTimeout(()=>{dismiss();$('q').focus();},reduced.matches?0:650);};
  $('orbit-open').onclick=()=>{dismiss();$('open-file').click();};
  function show(query='') {transitioning=false;shell.hidden=false;shell.classList.remove('departing');document.body.classList.add('landing-open');selection=null;flight=null;$('orbit-selection').hidden=true;$('orbit-results').replaceChildren();$('orbit-query').value=query;size();last=performance.now();cancelAnimationFrame(frame);frame=requestAnimationFrame(draw);$('orbit-query').focus();if(query)$('orbit-search').requestSubmit();}
  window.EnaLanding={select,dismiss,show};
  const params=new URLSearchParams(location.search);if(params.has('q')||params.has('demo'))dismiss();else {size();motion();frame=requestAnimationFrame(draw);}
  window.addEventListener('resize',size);
})();
