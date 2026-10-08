/* The presentation consumes recorded artifacts only. No ranking or scientific model runs here. */
"use strict";
const D = JSON.parse(document.getElementById("demo-data").textContent);
const $ = (id) => document.getElementById(id);
const esc = (v) => String(v ?? "Unknown").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const number = (v, digits = 0) => v === null || v === undefined || !Number.isFinite(v) ? "Unknown" : new Intl.NumberFormat("en", {maximumFractionDigits:digits, minimumFractionDigits:digits}).format(v);
const kilotonnes = v => v === null || v === undefined ? null : v / 1000;
const percent = (v) => v === null || v === undefined ? "Unknown" : `${number(v * 100, 1)}%`;
const status = (label) => `<span class="status ${esc(label.toLowerCase())}">${esc(label)}</span>`;
const human = (v) => String(v ?? "Unknown").replaceAll("_", " ");
const interval = (values, pct = false) => values ? values.map(v => pct ? percent(v) : number(v, 3)).join(" – ") : "Unavailable";
const coordinates = (n) => {const p = n.node.location.point.value; return [p.longitude, p.latitude];};
const evidenceTitle = (value) => esc(`${value.evidence.label} · ${value.evidence.as_of} · ${value.evidence.licence} · ${value.evidence.source_ids.join(", ")} · ${value.evidence.method}`);
const armNames = {full_model:"Full model", base_model:"Base model", B0:"Production only · B0", B1:"Euclidean buffer · B1", B2:"Road production · B2", population:"Population only", nearest_presence:"Nearest presence", area_only:"Area only", EnaGIS_phase3:"Phase 3 allocation"};
let selected = D.nodes[0], map, markers = [], guideStep = 0;
$("candidate-count").textContent = D.verified.phase3.nodes;
$("ranked-count").textContent = D.verified.phase3.ranked_nodes;
$("short-count").textContent = D.nodes.length;
$("list-count").textContent = `TOP ${D.nodes.length}`;

function renderList() {
  const term = $("search").value.trim().toLowerCase();
  const nodes = D.nodes.filter(n => [n.facility.name.value, n.facility.operator.value, n.province, n.node_id].join(" ").toLowerCase().includes(term));
  $("shortlist").innerHTML = nodes.map(n => `<button class="site-row ${n.node_id === selected.node_id ? "active" : ""}" data-node="${esc(n.node_id)}" aria-pressed="${n.node_id === selected.node_id}"><span class="rank">${String(n.rank).padStart(2,"0")}</span><span><strong>${esc(n.facility.name.value)}</strong><small>${esc(n.facility.operator.value)}</small></span><span class="site-power">${number(n.requirement.electrical_kw.value?.central,1)}<small>kW · ${esc(n.province)}</small></span></button>`).join("") || '<p class="muted small">No shortlisted site matches. Try its town or operator.</p>';
  $("shortlist").querySelectorAll("button").forEach(b => b.addEventListener("click", () => select(b.dataset.node, true)));
}

function fact(title, value, unit, label, evidence) {
  return `<div class="fact" title="${evidence ? evidenceTitle(evidence) : ""}"><span>${esc(title)}</span><strong>${esc(value)} <small>${esc(unit)}</small></strong>${status(label)}</div>`;
}

function renderCard() {
  const n = selected, power = n.requirement.electrical_kw, storage = n.storage_capacity.original.amount;
  const supply = {no_documented_asset:"Undocumented", documented_known_capacity:"Known capacity", documented_unknown_capacity:"Capacity unknown"}[n.supply.state] || human(n.supply.state);
  const margin = n.gap.capacity_minus_requirement_kw;
  $("node-card").innerHTML = `<p class="eyebrow">SITE ${String(n.rank).padStart(2,"0")} / ${esc(n.node.node_type.toUpperCase())} NODE</p><h2>${esc(n.facility.name.value)}</h2><p class="node-location">${esc(n.facility.operator.value)}<br>${esc(n.province)} · Primary elevator · ${esc(n.node.location.precision)} named-place precision</p>
    <div class="question"><h3>THE NEXT SITE QUESTION</h3><p>${esc(n.verification_question)}</p></div>
    <div class="power-box" title="${evidenceTitle(power)}"><div><span>Scenario fan requirement</span>${status(power.evidence.label)}</div><strong class="power-value">${number(power.value?.central,1)} <small>kW</small></strong><p>Concurrent fan duty under temporary assumptions.<br>Not measured demand. Rank stability not assessed.</p></div>
    <div class="facts">${fact("Aeration supply",supply,"",n.supply.evidence.label,{evidence:n.supply.evidence})}${fact("Supply − requirement",number(margin.value),"kW",margin.evidence.label,margin)}${fact("Assigned 2024 throughput", number(kilotonnes(n.assigned_tonnes_per_reporting_period.value),1),"kt / reporting year",n.assigned_tonnes_per_reporting_period.evidence.label,n.assigned_tonnes_per_reporting_period)}${fact("Reported storage",number(storage.value),"t · all crops",storage.evidence.label,storage)}</div>
    <details><summary>Why this site appears · evidence and uncertainty</summary><div><p>It is a documented storage candidate with a positive calculable requirement under ${esc(n.scenario_id)}. The pipeline orders scenario kW, then stable node ID. Ties do not establish a meaningful priority difference.</p><p>Gap bucket: <strong>${esc(human(n.gap.bucket))}</strong>. Undocumented supply does not establish that a fan is absent.</p><p>Uncertainty: not assessed. No Robust / Contested tier or probability is assigned. Grid access, economics, best visit window and actual operating status are unknown.</p><dl><dt>Inventory · ${esc(n.inventory.stored_tonnes.evidence.label)}</dt><dd>${number(n.inventory.stored_tonnes.value)} t (hypothetical residence)</dd><dt>Airflow · ${esc(n.airflow_m3_s.evidence.label)}</dt><dd>${number(n.airflow_m3_s.value,1)} m³/s</dd><dt>One hypothetical cooling cycle · ${esc(n.requirement.electricity_kwh.evidence.label)}</dt><dd>${number(n.requirement.electricity_kwh.value?.central)} kWh · not annual electricity use</dd><dt>Supply documentation scope</dt><dd>${esc(n.supply.documentation_scope)}</dd><dt>Coordinate / CRS / precision</dt><dd>${coordinates(n).map(v=>number(v,3)).join(", ")} · EPSG:4326 · ${esc(n.node.location.precision)}. Extra stored digits do not imply surveyed precision.</dd><dt>Identity / status as stated</dt><dd>${esc(n.node_id)}<br>${esc(n.facility.status_as_stated.value)}</dd><dt>Sources / dates / licences</dt><dd>${n.assigned_tonnes_per_reporting_period.evidence.source_ids.map(id=>{const s=D.sources.find(x=>x.snapshot_id===id);return s ? `${esc(id)} · ${esc(s.effective_on)} · ${esc(s.licence)}` : `${esc(id)} · temporary local scenario`;}).join("<br>")}</dd></dl></div></details>
    <button id="download-trace" class="quiet trace-download">Download this site's full trace ↓</button>`;
  $("download-trace").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify({metadata:D.metadata,trace:selected,scenario:D.scenario,source_snapshots:D.sources},null,2)],{type:"application/json"});
    const a = document.createElement("a"), url = URL.createObjectURL(blob);
    a.href=url; a.download=`site-${selected.rank}-trace.json`; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
}

function select(id, focusMap = false) {
  selected = D.nodes.find(n=>n.node_id===id) || selected;
  renderList(); renderCard();
  markers.forEach(m=>{const active=m.node.node_id===selected.node_id;m.button.classList.toggle("active",active);m.button.setAttribute("aria-pressed",String(active));});
  if (map?.isStyleLoaded()) {
    map.setFilter("selected-region",["==",["get","id"],selected.reporting_region || ""]);
    if (focusMap) map.easeTo({center:coordinates(selected),zoom:Math.max(map.getZoom(),7),duration:0});
  }
  document.querySelectorAll(".fallback-pin").forEach(p=>p.classList.toggle("active",p.dataset.node===selected.node_id));
  document.querySelectorAll(".fallback-svg .region").forEach(p=>p.classList.toggle("selected-region",p.dataset.region===selected.reporting_region));
}

function view(name) {
  document.querySelectorAll(".view").forEach(v=>v.hidden=v.id!==`view-${name}`);
  document.querySelectorAll("[data-view]").forEach(b=>{const active=b.dataset.view===name;b.classList.toggle("active",active);if(active)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current");});
  if(name==="shortlist") map?.resize();
}

const chain = [
  ["01","Pinned open inputs","AAFC reports locations and storage. Published wheat categories yield ESTIMATED non-durum totals; source flags are retained.",["OBSERVED","ESTIMATED"]],
  ["02","Conserved assignment","Bounded equal shares inside each reporting region. Known mass conserved; unknown production stays unknown.","ESTIMATED"],
  ["03","Inventory → fan duty","Residence and wheat storage share give inventory. Airflow, pressure and efficiency give concurrent kW.","ESTIMATED"],
  ["04","Evidence → shortlist","Order positive scenario kW, then stable node ID. Electrical supply is undocumented in the consumed registry.","INFERRED"],
  ["05","A verification question","Resolve location, licensing, actual inventory and fan duty. A field visit is still required; sample n = 0.","UNKNOWN"],
];
$("chain").innerHTML=chain.map(c=>`<article><span>${c[0]} →</span><h3>${c[1]}</h3><p>${c[2]}</p>${(Array.isArray(c[3])?c[3]:[c[3]]).map(status).join(" ")}</article>`).join("");
const audit = D.audit;
$("coverage").innerHTML = [["Development candidates",D.verified.phase3.nodes],["Ranked with scenario estimates",D.verified.phase3.ranked_nodes],...Object.entries(audit.assignment_statuses).filter(([k])=>k!=="assigned_within_reporting_region").map(([k,v])=>[human(k),v]),["Known production origins",audit.known_production_origins],["Unknown production origins",audit.unknown_production_origins],["Known input / assigned mass",`${number(audit.known_input_tonnes)} / ${number(audit.assigned_tonnes)} t`],["Explicit unserved (known subset)",`${number(audit.explicit_unserved_tonnes)} t`]].map(([k,v])=>`<div class="coverage-row"><span>${esc(k)}</span><strong>${esc(v ?? "Unknown")}</strong></div>`).join("");
$("parameters").innerHTML=D.scenario.parameters.map(p=>`<div class="parameter-row"><span>${esc(human(p.parameter_id))}</span><strong>${number(p.value.value, p.value.value < 1 ? 3 : 0)} ${esc(p.unit)}</strong></div>`).join("")+`<p class="small">All parameter and method approvals remain null. ${esc(D.scenario.disclaimer)}</p>`;
const sourceURL = url => /^https:\/\//i.test(url) ? esc(url) : "#";
$("sources").innerHTML=D.sources.map(s=>`<article class="source-card"><h4>${esc(s.snapshot_id)}</h4><p>${esc(s.publisher)}<br>Effective: ${esc(s.effective_on)} · retrieved ${esc(s.retrieved_on)}<br>${esc(s.licence)}</p><a href="${sourceURL(s.original_url)}" target="_blank" rel="noopener noreferrer">Original source ↗</a> · <a href="${sourceURL(s.licence_url)}" target="_blank" rel="noopener noreferrer">Licence ↗</a><details><summary>Method and source checksum</summary><p>${esc(s.processing_step)}</p>${esc(s.sha256)}</details></article>`).join("");

const siting = D.comparison.siting, primary = siting.primary, hindcast = D.comparison.hindcast;
$("verdict").textContent=primary.decision==="keep" ? "KEEP" : primary.status==="evaluated" ? "KILL" : "NOT TESTABLE";
$("cohort-description").textContent=`${siting.cohort_units} complete CCS · ${siting.documented_positive_units} documented positive CCS · ${siting.positive_blocks} positive CAR blocks. Leave one CAR out. Background is not confirmed absence.`;
const arms = Object.entries(primary.arms || {}).sort((a,b)=>b[1].mean-a[1].mean);
const best = arms.filter(([id])=>id!=="full_model")[0]?.[0];
$("primary-chart").innerHTML=arms.map(([id,r])=>`<div class="bar-row ${id==="full_model"?"full":id===best?"best":""}"><span>${esc(armNames[id]||id)}<small>95%: ${interval(r.interval,true)}</small></span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(0,Math.min(100,r.mean*100))}%"></div></div><span class="bar-value">${percent(r.mean)}</span></div>`).join("");
const margin=primary.margin_over_best_baseline;
$("margin").textContent=margin ? `Full − best baseline: ${number(margin.estimate*100,2)} percentage points. Paired 95% margin interval: ${margin.interval.map(v=>number(v*100,2)).join(" to ")} pp.` : "Margin unavailable: primary rule not testable.";
$("interpretation").textContent=siting.interpretation;
$("power").textContent=`${siting.power} ${primary.draws} paired block-bootstrap draws; seed ${primary.seed}. Intervals and counts are descriptive.`;
$("hindcast-description").textContent=`${hindcast.common_comparison_groups} common shipping-point groups · ${hindcast.blocks} CAR blocks · ${hindcast.excluded_groups} excluded groups. Status: ${human(hindcast.status)}.`;
$("hindcast-table").innerHTML=`<table><thead><tr><th>Arm</th><th>Spearman<br>95% interval</th><th>Top-volume<br>hits / selected</th></tr></thead><tbody>${Object.entries(hindcast.arms||{}).sort((a,b)=>b[1].spearman-a[1].spearman).map(([id,r])=>`<tr><td>${esc(armNames[id]||id)}</td><td>${number(r.spearman,3)}<br><span class="muted small">${interval(r.interval)}</span></td><td>${r.top_volume_group_recall.hits} / ${r.top_volume_group_recall.selected_units}</td></tr>`).join("")}</tbody></table>`;
const reg = D.comparison.preregistration, cohort = D.comparison.cohorts;
$("comparison-details").innerHTML=`<p>Protocol: ${esc(siting.protocol_id)}<br>Commit: <code>${esc(reg.git_commit)}</code><br>Tag: ${esc(reg.git_tag)}<br>Remote: ${esc(reg.remote_url)}</p><table class="cohort-table"><thead><tr><th>Cohort</th><th>Complete CCS</th><th>Positive CCS</th><th>Positive CARs</th><th>Excluded CCS</th></tr></thead><tbody>${["primary","sensitivity"].map(k=>`<tr><td>${esc(human(k))}</td><td>${number(cohort[k].complete_ccs)}</td><td>${number(cohort[k].positive_ccs)}</td><td>${number(cohort[k].positive_cars)}</td><td>${number(cohort[k].excluded_ccs)}</td></tr>`).join("")}</tbody></table><p>Sensitivity drops production-dependent features. It is diagnostic only and cannot override the primary rule. Exclusion reasons overlap:</p><table class="cohort-table"><thead><tr><th>Reason</th><th>Primary</th><th>Sensitivity</th></tr></thead><tbody>${Object.entries(cohort.primary.exclusions_by_reason).map(([k,v])=>`<tr><td>${esc(human(k))}</td><td>${number(v)}</td><td>${number(cohort.sensitivity.exclusions_by_reason[k])}</td></tr>`).join("")}</tbody></table><ul>${D.comparison.limitations.map(l=>`<li>${esc(l)}</li>`).join("")}</ul><p>Historical artifacts verified: Phase 3 (${D.verified.phase3.verified_artifacts}); Phase 4 (${D.verified.phase4.verified_artifacts}). Full files and checksums are included in this bundle.</p>`;

function bounds() {return D.nodes.reduce((b,n)=>{const [x,y]=coordinates(n);return [[Math.min(b[0][0],x),Math.min(b[0][1],y)],[Math.max(b[1][0],x),Math.max(b[1][1],y)]];},[[180,90],[-180,-90]]);}
function fit() {if(map)map.fitBounds(bounds(),{padding:{top:70,bottom:130,left:60,right:60},maxZoom:8,duration:0});}
function initMap() {
  if (new URLSearchParams(location.search).get("map") === "schematic") return fallback();
  if (!window.maplibregl) return fallback();
  try {
    map = new maplibregl.Map({container:"map",style:{version:8,sources:{},layers:[{id:"background",type:"background",paint:{"background-color":"#0d1c22"}}]},center:coordinates(selected),zoom:6,attributionControl:false,fadeDuration:0});
    map.addControl(new maplibregl.AttributionControl({compact:false,customAttribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> · Statistics Canada / AAFC · pinned 2024 context'}));
    map.addControl(new maplibregl.NavigationControl({showCompass:false}),"bottom-right");
    map.on("load",()=>{
      ["provinces","regions","roads"].forEach(id=>map.addSource(id,{type:"geojson",data:D.context[id]}));
      map.addLayer({id:"land",type:"fill",source:"provinces",paint:{"fill-color":"#172b31","fill-opacity":.8}});
      map.addLayer({id:"region-lines",type:"line",source:"regions",paint:{"line-color":"#3d555b","line-width":.6,"line-opacity":.6}});
      map.addLayer({id:"selected-region",type:"fill",source:"regions",filter:["==",["get","id"],selected.reporting_region||""],paint:{"fill-color":"#749979","fill-opacity":.16}});
      map.addLayer({id:"roads",type:"line",source:"roads",paint:{"line-color":"#516b70","line-width":1,"line-opacity":.7}});
      map.addLayer({id:"province-lines",type:"line",source:"provinces",paint:{"line-color":"#65828a","line-width":1.2}});
      map.addSource("sites",{type:"geojson",data:{type:"FeatureCollection",features:D.nodes.map(n=>({type:"Feature",geometry:{type:"Point",coordinates:coordinates(n)},properties:{}}))}});
      map.addLayer({id:"true-locations",type:"circle",source:"sites",paint:{"circle-radius":3,"circle-color":"#b5e3bd"}});
      D.nodes.forEach(n=>{const button=document.createElement("button");button.className="map-pin";button.textContent=n.rank;button.setAttribute("aria-label",`Select rank ${n.rank}: ${n.facility.name.value}, ${n.facility.operator.value}`);button.addEventListener("click",()=>select(n.node_id));const marker=new maplibregl.Marker({element:button}).setLngLat(coordinates(n)).addTo(map);markers.push({marker,button,node:n});});
      map.on("moveend",separateMarkers);fit();separateMarkers();select(selected.node_id);
      $("map-status").textContent="Offline interactive map loaded.";
    });
    map.on("error",()=>{if(!map.isStyleLoaded())fallback();});
  } catch (_) {fallback();}
}
function separateMarkers() {
  const taken=[];
  markers.forEach(m=>{const p=map.project(coordinates(m.node));let y=p.y;while(taken.some(q=>Math.abs(q.x-p.x)<28&&Math.abs(q.y-y)<28))y+=29;m.marker.setOffset([0,y-p.y]);taken.push({x:p.x,y});});
}
function fallback() {
  if(map){map.remove();map=null;}$("map").hidden=true;$("fallback-map").hidden=false;
  document.querySelector(".map-topline > span").textContent="SCHEMATIC DEVELOPMENT FOOTPRINT";
  $("reset-map").hidden=true;
  $("fallback-map").setAttribute("role","region");
  $("fallback-map").setAttribute("aria-label","Interactive schematic map of the ten shortlisted elevators");
  const b=bounds(),pad=.5,x0=b[0][0]-pad,x1=b[1][0]+pad,y0=b[0][1]-pad,y1=b[1][1]+pad;
  const project=([x,y])=>[(x-x0)/(x1-x0)*800,500-(y-y0)/(y1-y0)*500];
  const paths=(features,cls)=>features.map(f=>{const g=f.geometry;const lines=g.type==="MultiPolygon"?g.coordinates.flat():g.type==="Polygon"?g.coordinates:g.type==="MultiLineString"?g.coordinates:g.type==="LineString"?[g.coordinates]:[];return lines.map(line=>`<path class="${cls} ${f.properties.id===selected.reporting_region?"selected-region":""}" data-region="${esc(f.properties.id)}" d="M${line.map(c=>project(c).join(",")).join("L")}"/>`).join("");}).join("");
  const taken=[];
  const pins=D.nodes.map(n=>{const [x,initialY]=project(coordinates(n));let y=initialY;while(taken.some(q=>Math.abs(q[0]-x)<28&&Math.abs(q[1]-y)<28))y+=29;taken.push([x,y]);return `<g><line x1="${x}" y1="${initialY}" x2="${x}" y2="${y}" stroke="#779f89"/><circle cx="${x}" cy="${initialY}" r="3" fill="#83d6df"/><circle tabindex="0" role="button" aria-label="Select ${esc(n.facility.name.value)} rank ${n.rank}" data-node="${esc(n.node_id)}" class="fallback-pin ${n===selected?"active":""}" cx="${x}" cy="${y}" r="13"/><text x="${x}" y="${y}">${n.rank}</text></g>`;}).join("");
  $("fallback-map").innerHTML=`<svg class="fallback-svg" viewBox="0 0 800 500" aria-label="Schematic map; WebGL unavailable"><defs><clipPath id="map-clip"><rect width="800" height="500"/></clipPath></defs><g clip-path="url(#map-clip)">${paths(D.context.regions.features,"region")}${paths(D.context.roads.features,"road")}${pins}</g></svg>`;
  document.querySelectorAll(".fallback-pin").forEach(p=>{p.addEventListener("click",()=>select(p.dataset.node));p.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();select(p.dataset.node);}});});
  $("map-status").textContent="WebGL unavailable. Interactive schematic map shown; site coordinates and traces remain available.";
}

const steps=[
  ["shortlist","Start with a decision.","A site-assessment team needs a focused first visit. These are ten places from the real pipeline, ordered by a temporary engineering scenario—not a claim of investment readiness."],
  ["shortlist","One site. One next question.",`${D.nodes[0].facility.name.value} is the first site in this recorded order; equally sized estimates use stable IDs. Its fan requirement is estimated. Supply is undocumented. The question in the card tells the team what to verify.`],
  ["evidence","Follow the number back.","Locations, reported storage and regional production retain their sources. Assignment and fan duty are explicit assumptions. Missing production stays unknown; known mass is conserved. No source label is promoted to field truth."],
  ["comparison","Let simpler choices compete.","The full siting model did not beat the best baseline under the frozen rule. Read the margin interval and counts. The shipping-point hindcast is a separate retrospective diagnostic, not evidence that this energy shortlist is validated."],
  ["shortlist","Leave with a useful next action.","Export the shortlist or a complete site trace. Verify current location/licensing, wheat inventory, fan airflow and motor duty, then supply. The product makes that next investigation clear; validation and deployment decisions follow evidence."],
];
function showGuide() {const s=steps[guideStep];document.body.classList.add("guiding");view(s[0]);if(guideStep===1)select(D.nodes[0].node_id);$("guide-step").textContent=`GUIDED DEMO / ${guideStep+1} OF ${steps.length}`;$("guide-title").textContent=s[1];$("guide-copy").textContent=s[2];$("guide-back").disabled=guideStep===0;$("guide-next").textContent=guideStep===steps.length-1?"Finish ✓":"Next →";if(!$("guide").open)$("guide").show();map?.resize();if(s[0]==="shortlist")fit();}
function closeGuide() {$("guide").close();document.body.classList.remove("guiding");map?.resize();}
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>view(b.dataset.view)));
$("search").addEventListener("input",renderList);$("reset-map").addEventListener("click",fit);
$("show-assumptions").addEventListener("click",()=>view("evidence"));
$("present").addEventListener("click",()=>{guideStep=0;showGuide();});
$("close-guide").addEventListener("click",closeGuide);
$("guide-back").addEventListener("click",()=>{guideStep=Math.max(0,guideStep-1);showGuide();});
$("guide-next").addEventListener("click",()=>{if(guideStep===steps.length-1)closeGuide();else{guideStep++;showGuide();}});
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeGuide();});
renderList();renderCard();initMap();
