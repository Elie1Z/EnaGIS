/* A local evidence viewer. Analysis comes from recorded packages. */
"use strict";
const D = JSON.parse(document.getElementById("demo-data").textContent);
let W, C;
const world = () => W ||= JSON.parse(document.getElementById("world-data").textContent);
const context = () => C ||= JSON.parse(document.getElementById("map-context").textContent);
const V = window.EnaView;
const $ = id => document.getElementById(id);
const esc = value => String(value ?? "Unknown").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeURL = value => /^https:\/\//i.test(value || "") ? esc(value) : "#";
const dictionaries = {
  en: {skip:"Skip to locations",search:"Search a place or latitude, longitude",first:"Where first",sure:"How sure",travel:"How to get there",works:"How it works",title:"Where to investigate first",start:"Start here: the 10 places to look first.",world:"World",fit:"Fit sites",locate:"My location",roads:"Roads",reporting:"Reporting region",haze:"Thin data",readMap:"How to read this map",markerKey:"Marker size shows scenario fan kW. Numbers are recorded ranks.",ringKey:"Double rings: confidence unknown. Location precision does not establish a confident energy estimate.",hatchKey:"Hatching means no compatible analysis here yet. It does not mean no facilities or energy need.",screening:"INVESTIGATION LIST",firstVisits:"The first visits",filter:"Filter sites",export:"Export shortlist",tieNote:"Equal estimates use stable IDs. Ties do not establish urgency.",screeningLine:"Screening tool, not a feasibility study",helpTitle:"Read the evidence",helpCopy:"Search a place, choose a site, and inspect its next question. Enter coordinates as latitude, longitude. The local place index is incomplete; select smaller places on the map.",limits:"Sources and limitations",import:"Open regional analysis",restore:"Restore built-in analysis",why:"Why it is here",howSure:"How sure",check:"Check first",unknown:"Unknown",rangeUnknown:"Range unknown · one scenario",need:"Scenario fan requirement",notAssessed:"Rank uncertainty has not been assessed.",reported:"Reported location",capacity:"Aeration capacity",sources:"Evidence, sources and dates",copy:"Copy coordinates",brief:"Site brief",phone:"Open phone map",trace:"Download source trace",noData:"No analysis package for this area yet",noDataCopy:"This location is selectable. Local production, facilities and operating evidence are needed before a numerical shortlist can be supported.",knownHere:"Analysis coverage is available here",knownCopy:"Choose a documented site from the list to inspect its recorded assessment.",needs:"Evidence needed",needsCopy:"Facility records · production and season · roads and access · service parameters · supply documentation",unknownNeed:"Requirement unknown",checkPlace:"Find a local source for facilities, production and the service to assess.",noMatch:"No place found. Enter latitude, longitude or select a point on the map.",searchPlaceholder:"Search anywhere · place or lat, lon",filterPlaceholder:"Filter sites or operators",simple:"Simple",expert:"Expert",locations:"Locations",copied:"Coordinates copied",copyFail:"Clipboard unavailable. Coordinates:",notLocated:"Location unavailable. Search or enter coordinates instead.",notCollected:"Not collected",supplyUnknown:"Supply documentation is missing",supplyUnknownCapacity:"Asset documented; capacity unknown",supplyKnown:"Comparable capacity documented",storage:"Reported storage",throughput:"Assigned throughput",margin:"Supply − requirement",window:"Best visit window",access:"Access status",energy:"Energy context",season:"Seasonal access",dry:"Dry",rainy:"Rainy",seasonUnknown:"No approved seasonal route results in this package.",checklist:"Before a visit",checklistCopy:"Confirm the facility is operating. Ask about current crop inventory, fan duty, electrical supply, access and consent to visit.",baseline:"Simpler choices",validation:"Validation",needUnvalidated:"Energy estimates are temporary and unvalidated.",tiersUnknown:"Robust / Contested tiers: not assessed",fieldNone:"Field verification: 0 observations",imported:"Regional analysis opened",originalLanguage:"Source excerpts and scientific reports retain their original language.",story:"The evidence chain",back:"Previous",next:"Next",story0:"1 · Harvest and production",story1:"2 · Collection points and assignment",story2:"3 · Technical requirement",story3:"4 · What remains unknown",story4:"5 · Compare and verify",storyCopy0:"Published production retains its reporting area and period. Finer allocation is estimated; unknown production stays unknown.",storyCopy1:"Documented locations are candidates for investigation. Production is assigned once with explicit capacity and unserved totals. Shaded areas here are reporting regions, not road catchments.",storyCopy2:"Stored mass, airflow and electrical power are different quantities. This package presents one hypothetical inventory and fan-duty scenario.",storyCopy3:"Documentation does not establish current operation or installed electrical supply. Unknown confidence remains visible in every lens.",storyCopy4:"Compare with simpler baselines, freeze the ranking, then collect consented verification. The real sample is still uncollected.",selected:"Selected location",synthetic:"Synthetic data",rank:"Recorded rank",areaExport:"Download evidence needs",noRows:"No listed site matches this filter.",frame:"Recorded scenario · wheat storage / aeration"},
  fr: {skip:"Aller aux lieux",search:"Rechercher un lieu ou latitude, longitude",first:"Où commencer",sure:"Quelle confiance",travel:"Comment y aller",works:"La méthode",title:"Où enquêter en premier",start:"Commencez par ces 10 lieux à examiner.",world:"Monde",fit:"Voir les sites",locate:"Ma position",roads:"Routes",reporting:"Zone statistique",haze:"Données limitées",readMap:"Lire cette carte",markerKey:"La taille indique la puissance du scénario en kW. Les nombres sont les rangs enregistrés.",ringKey:"Double anneau : confiance inconnue. La précision du lieu ne valide pas l'estimation énergétique.",hatchKey:"Les hachures indiquent l'absence d'analyse compatible, pas l'absence de besoin.",screening:"LIEUX À EXAMINER",firstVisits:"Premières visites",filter:"Filtrer les sites",export:"Exporter la liste",tieNote:"Les estimations égales sont ordonnées par identifiant. Aucun degré d'urgence n'est établi.",screeningLine:"Outil de présélection, pas une étude de faisabilité",helpTitle:"Lire les éléments",helpCopy:"Recherchez un lieu ou des coordonnées latitude, longitude. L'index local est incomplet ; sélectionnez les petits lieux sur la carte.",limits:"Sources et limites",import:"Ouvrir une analyse régionale",restore:"Rétablir l'analyse intégrée",why:"Pourquoi ce lieu",howSure:"Quelle confiance",check:"Vérifier d'abord",unknown:"Inconnu",rangeUnknown:"Intervalle inconnu · un scénario",need:"Puissance des ventilateurs du scénario",notAssessed:"L'incertitude du classement n'a pas été évaluée.",reported:"Localisation rapportée",capacity:"Capacité d'aération",sources:"Éléments, sources et dates",copy:"Copier les coordonnées",brief:"Fiche du site",phone:"Carte sur téléphone",trace:"Télécharger les sources",noData:"Aucune analyse disponible pour cette zone",noDataCopy:"Ce lieu peut être sélectionné. Des données locales sur la production, les installations et leur fonctionnement sont nécessaires.",knownHere:"Cette zone dispose d'une analyse",knownCopy:"Choisissez un site dans la liste pour examiner son évaluation enregistrée.",needs:"Données nécessaires",needsCopy:"Installations · production et saison · routes et accès · paramètres du service · offre documentée",unknownNeed:"Besoin inconnu",checkPlace:"Chercher des sources locales sur les installations, la production et le service.",noMatch:"Aucun lieu trouvé. Entrez latitude, longitude ou sélectionnez la carte.",searchPlaceholder:"Rechercher un lieu · lat, lon",filterPlaceholder:"Filtrer sites ou exploitants",simple:"Simple",expert:"Expert",locations:"Lieux",copied:"Coordonnées copiées",copyFail:"Presse-papiers indisponible. Coordonnées :",notLocated:"Position indisponible. Recherchez un lieu ou entrez les coordonnées.",notCollected:"Non recueillie",supplyUnknown:"Offre non documentée",supplyUnknownCapacity:"Équipement documenté ; capacité inconnue",supplyKnown:"Capacité comparable documentée",storage:"Stockage rapporté",throughput:"Volume annuel attribué",margin:"Offre − besoin",window:"Période de visite",access:"Accès",energy:"Contexte énergétique",season:"Accès saisonnier",dry:"Sèche",rainy:"Pluvieuse",seasonUnknown:"Aucun résultat approuvé de trajet saisonnier dans ce fichier.",checklist:"Avant la visite",checklistCopy:"Confirmer le fonctionnement. Demander les stocks, les ventilateurs, l'électricité, l'accès et le consentement à une visite.",baseline:"Choix plus simples",validation:"Validation",needUnvalidated:"Estimations énergétiques provisoires et non validées.",tiersUnknown:"Niveaux Robuste / Contesté : non évalués",fieldNone:"Vérification terrain : 0 observations",imported:"Analyse régionale ouverte",originalLanguage:"Les extraits et rapports scientifiques conservent leur langue d'origine.",story:"La chaîne des éléments",back:"Précédent",next:"Suivant",story0:"1 · Récolte et production",story1:"2 · Collecte et allocation",story2:"3 · Besoin technique",story3:"4 · Ce qui reste inconnu",story4:"5 · Comparer et vérifier",storyCopy0:"La production publiée garde sa zone et sa période. L'allocation fine est estimée ; les valeurs inconnues restent inconnues.",storyCopy1:"Les lieux documentés sont des candidats. La production est comptée une fois. Les zones affichées sont statistiques, pas des bassins routiers.",storyCopy2:"Masse stockée, débit d'air et puissance sont distincts. Ce fichier montre un scénario hypothétique.",storyCopy3:"Les documents ne prouvent ni le fonctionnement actuel ni l'offre électrique. L'incertitude reste visible.",storyCopy4:"Comparer les références, figer le classement, puis vérifier avec consentement. L'échantillon réel reste absent.",selected:"Lieu sélectionné",synthetic:"Données synthétiques",rank:"Rang enregistré",areaExport:"Télécharger les besoins de données",noRows:"Aucun site ne correspond au filtre.",frame:"Scénario enregistré · stockage / aération du blé"},
  rw: {skip:"Jya ku hantu",search:"Shaka ahantu cyangwa latitude, longitude",first:"Aho gutangirira",sure:"Icyizere",travel:"Uko wagerayo",works:"Uko bikora",title:"Aho kubanza gusuzuma",start:"Tangirira kuri aha hantu 10 ho gusuzuma.",world:"Isi",fit:"Reba ahantu",locate:"Aho ndi",roads:"Imihanda",reporting:"Agace k'ibarurishamibare",haze:"Amakuru make",readMap:"Uko usoma ikarita",markerKey:"Ingano y'ikimenyetso yerekana kW z'icyerekezo. Imibare ni imyanya yanditswe.",ringKey:"Impeta ebyiri: icyizere ntikizwi. Ahantu handitswe ntihamya ukuri kw'ingufu zagereranyijwe.",hatchKey:"Imirongo yerekana ko nta sesengura rihari, ntivuga ko nta bikoresho cyangwa ingufu bikenewe.",screening:"AHANTU HO GUSUZUMA",firstVisits:"Aho kubanza gusura",filter:"Shungura ahantu",export:"Kuramo urutonde",tieNote:"Ibigereranyo bingana bitondekwa hakurikijwe indangamuntu. Ntibihamya ibyihutirwa.",screeningLine:"Igikoresho cyo guhitamo aho gusuzuma; si inyigo yuzuye",helpTitle:"Soma amakuru",helpCopy:"Shaka ahantu cyangwa wandike latitude, longitude. Urutonde rw'ahantu ntirwuzuye; hitamo ahandi ku ikarita.",limits:"Inkomoko n'imbogamizi",import:"Fungura isesengura ry'akarere",restore:"Subizaho isesengura ribitse",why:"Impamvu hatoranyijwe",howSure:"Icyizere",check:"Banza ugenzure",unknown:"Ntibizwi",rangeUnknown:"Urugero ntiruzwi · icyerekezo kimwe",need:"Ingufu z'abafana muri iki cyerekezo",notAssessed:"Icyizere cy'urutonde ntikirasuzumwa.",reported:"Ahantu handitswe",capacity:"Ubushobozi bwo guhumeka",sources:"Amakuru, inkomoko n'amatariki",copy:"Koporora coordinates",brief:"Incamake y'ahantu",phone:"Ikarita kuri telefone",trace:"Kuramo inkomoko",noData:"Nta sesengura ry'aha rirahari",noDataCopy:"Aha hantu wahahitamo. Hakenewe amakuru y'umusaruro, ibikoresho n'uko bikora kugira ngo urutonde rushoboke.",knownHere:"Isesengura ry'aha rirahari",knownCopy:"Hitamo ahantu ku rutonde usome amakuru yabwo.",needs:"Amakuru akenewe",needsCopy:"Ibigo · umusaruro n'igihe · imihanda · ibipimo by'umurimo · ingufu zihari",unknownNeed:"Ingufu zikenewe ntizizwi",checkPlace:"Shaka inkomoko y'amakuru y'ibigo, umusaruro n'umurimo ukeneye gusuzuma.",noMatch:"Nta hantu habonetse. Andika latitude, longitude cyangwa hitamo ku ikarita.",searchPlaceholder:"Shaka ahantu hose · lat, lon",filterPlaceholder:"Shungura ahantu cyangwa ibigo",simple:"Byoroshye",expert:"Birambuye",locations:"Ahantu",copied:"Coordinates zakoporowe",copyFail:"Gukoporora ntibishobotse. Coordinates:",notLocated:"Aho uri ntihabonetse. Shaka ahantu cyangwa wandike coordinates.",notCollected:"Ntarakusanywa",supplyUnknown:"Ingufu zihari ntizanditswe",supplyUnknownCapacity:"Igikoresho cyanditswe; ubushobozi ntibuzwi",supplyKnown:"Ubushobozi bugereranywa bwaranditswe",storage:"Ububiko bwanditswe",throughput:"Umusaruro wagenewe ahantu",margin:"Ingufu zihari − izikenewe",window:"Igihe cyo gusura",access:"Uko wagerayo",energy:"Amakuru y'ingufu",season:"Kugera aho mu bihe",dry:"Izuba",rainy:"Imvura",seasonUnknown:"Nta makuru yemejwe y'ingendo muri ibi bihe.",checklist:"Mbere yo gusura",checklistCopy:"Emeza ko ikigo gikora. Baza ububiko, abafana, amashanyarazi, uko wahagera n'uruhushya rwo gusura.",baseline:"Amahitamo yoroshye",validation:"Igenzura",needUnvalidated:"Ibigereranyo by'ingufu ntibiragenzurwa.",tiersUnknown:"Ibyiciro by'icyizere ntibiragenwa",fieldNone:"Igenzura ry'ahantu: amakuru 0",imported:"Isesengura ry'akarere ryafunguwe",originalLanguage:"Inkomoko na raporo za siyansi zigumana ururimi zanditswemo.",story:"Inzira y'amakuru",back:"Ibanje",next:"Ikurikira",story0:"1 · Isarura n'umusaruro",story1:"2 · Gukusanya no kugabanya",story2:"3 · Ingufu zikenewe",story3:"4 · Ibitazwi",story4:"5 · Kugereranya no kugenzura",storyCopy0:"Umusaruro wanditswe ugumana agace n'igihe cyawo. Ibitazwi ntibihinduka zeru.",storyCopy1:"Ahantu handitswe ni aho gusuzuma. Umusaruro ntubarwa kabiri. Uturere tw'ikarita si ibice by'imihanda.",storyCopy2:"Ububiko, umwuka n'amashanyarazi ni ibipimo bitandukanye. Aha hari icyerekezo kimwe kigereranyijwe.",storyCopy3:"Inyandiko ntizihamya ko ikigo gikora cyangwa ko gifite amashanyarazi. Ibitazwi biguma bigaragara.",storyCopy4:"Gereranya n'ibipimo byoroshye, funga urutonde, ukore igenzura rifite uruhushya. Amakuru nyayo ntarakusanywa.",selected:"Ahantu hatoranyijwe",synthetic:"Amakuru y'igerageza",rank:"Umwanya wanditswe",areaExport:"Kuramo amakuru akenewe",noRows:"Nta hantu bihuye n'ibishungurwa.",frame:"Icyerekezo kibitse · ububiko / guhumeka ingano"}
};
let lang = "en", expert = false;
try {lang = localStorage.getItem("enagis-language") || "en";expert = localStorage.getItem("enagis-detail") === "expert";} catch (_) {}
if (!dictionaries[lang]) lang = "en";
const t = key => dictionaries[lang][key] || dictionaries.en[key] || key;
const num = value => typeof value === "number" && Number.isFinite(value) ? new Intl.NumberFormat(lang === "rw" ? "en" : lang, {maximumSignificantDigits:2}).format(value) : t("unknown");
const pct = value => `${new Intl.NumberFormat(lang === "rw" ? "en" : lang, {maximumFractionDigits:1}).format(value * 100)}%`;
const chip = (label, prefix="") => `<span class="status ${esc(label.toLowerCase())}">${esc(prefix)}${esc(label)}</span>`;
let allBuiltIn = D.nodes.map(V.fromNode);
const builtIn = {title:"Alberta / Saskatchewan",region_id:D.metadata.region_id,run_id:D.metadata.run_id,
  commodity_id:D.metadata.commodity_id,service_id:D.metadata.service_id,period_start:D.metadata.period_start,period_end:D.metadata.period_end,
  purpose:"real",sites:allBuiltIn,get coverage(){return context().provinces;},sources:D.sources,comparison:D.comparison,
  limitations:[D.scenario.disclaimer]};
let pack = builtIn, lens = "first", selected = allBuiltIn.find(s => s.rank === 1), area = null;
let map = null, mapReady = false, markers = [], areaMarker = null, storyStep = 0;
let searchMatches = [], searchIndex = -1, toastTimer;
let fallbackCamera = {lon:selected.lon,lat:selected.lat,width:7}, fallbackActive = false;
function covered() {return !area || V.contains(pack.coverage,[area.lon,area.lat]);}
function topSites() {return pack.sites.filter(s => s.rank !== null && s.rank <= 10).sort((a,b) => a.rank-b.rank);}
function flash(message) {clearTimeout(toastTimer);$("toast").textContent=message;$("toast").hidden=false;toastTimer=setTimeout(()=>{$("toast").hidden=true;},4500);}
function closeSearch() {$("search-results").hidden=true;$("place-search").setAttribute("aria-expanded","false");$("place-search").removeAttribute("aria-activedescendant");}
function renderSearch() {
  if(pack===builtIn)loadCandidates();
  searchMatches=V.search($("place-search").value,world(),pack.sites);searchIndex=-1;
  const typed=$("place-search").value.trim().length>=2;
  $("search-results").hidden=!typed;$("place-search").setAttribute("aria-expanded",String(typed));
  $("search-results").innerHTML=searchMatches.length?searchMatches.map((p,i)=>`<button class="search-option" id="result-${i}" role="option" aria-selected="false" data-result="${i}"><strong>${esc(p.name)}</strong><small>${esc(p.country || `${p.lat}, ${p.lon}`)} · ${esc(p.kind)}</small></button>`).join(""):`<p class="empty">${esc(t("noMatch"))}</p>`;
  $("search-results").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>chooseResult(Number(b.dataset.result))));
}
function chooseResult(index) {
  const p=searchMatches[index];if(!p)return;
  $("place-search").value=p.name;closeSearch();
  if(p.kind==="site")selectSite(p.id,true);else selectArea(p);
}
function selectArea(p) {
  if(!V.point(p.lon,p.lat))return;
  area={...p};selected=null;document.body.classList.remove("list-open");
  camera(p.lon,p.lat,p.kind==="country"?4:8);render();setAreaMarker();
  if(Math.abs(p.lat)>85)flash("Polar coordinates retained. The Mercator map stops near 85°; use the flat map for polar navigation.");
}
function selectSite(id, move=false) {
  const site=pack.sites.find(s=>s.id===id);if(!site)return;
  selected=site;area=null;document.body.classList.remove("list-open");$("detail-sheet").dataset.snap="mid";
  if(areaMarker){areaMarker.remove();areaMarker=null;}
  if(move)camera(site.lon,site.lat,8);
  render();
}
function camera(lon,lat,zoom) {
  if(mapReady)map.jumpTo({center:[lon,Math.max(-85,Math.min(85,lat))],zoom});
  fallbackCamera={lon,lat,width:360/Math.pow(2,zoom-1)};if(fallbackActive)renderFallback();
}
function fitSites() {
  const sites=topSites();if(!sites.length){camera(0,15,1);return;}
  const xs=sites.map(s=>s.lon),ys=sites.map(s=>s.lat);
  if(mapReady){const mobile=innerWidth<=760;map.fitBounds([[Math.min(...xs),Math.min(...ys)],[Math.max(...xs),Math.max(...ys)]],{padding:mobile?{top:190,bottom:240,left:60,right:60}:{top:210,bottom:100,left:350,right:360},maxZoom:9,duration:0});}
  fallbackCamera={lon:(Math.min(...xs)+Math.max(...xs))/2,lat:(Math.min(...ys)+Math.max(...ys))/2,width:Math.max(3,(Math.max(...xs)-Math.min(...xs))*3)};
  if(fallbackActive)renderFallback();
}
function renderList() {
  const filtered=topSites().filter(s=>V.normalize(`${s.name} ${s.operator} ${s.province}`).includes(V.normalize($("site-filter").value)));
  $("list-count").textContent=covered()?filtered.length:"—";
  $("site-list").hidden=lens!=="first";
  document.querySelector(".filter-wrap").hidden=lens!=="first" || !covered();
  document.querySelector(".drawer-footer").hidden=lens!=="first" || !covered();
  $("site-list").innerHTML=!covered()?`<div class="empty"><h3>${esc(t("noData"))}</h3><p>${esc(t("noDataCopy"))}</p></div>`:filtered.map(s=>`<button class="site-row" data-site="${esc(s.id)}" aria-pressed="${selected?.id===s.id}"><span class="row-rank">${s.rank}</span><span class="row-title"><strong>${esc(s.name)}</strong><small>${esc(s.operator)}</small></span><span class="row-power">${num(s.need.value)}<small>${s.need.value===null?esc(t("unknownNeed")):"kW · ESTIMATED"}</small></span></button>`).join("") || `<p class="empty">${esc(t("noRows"))}</p>`;
  $("site-list").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>selectSite(b.dataset.site,true)));
  $("list-title").textContent=t(lens==="first"?"firstVisits":lens);
  $("list-context").textContent=pack===builtIn?t("frame"):`${pack.title} · ${pack.service_id} · ${pack.period_start} / ${pack.period_end}`;
}
function fact(name,value){return `<div class="fact"><span>${esc(t(name))}</span><strong>${esc(value)}</strong></div>`;}
function sourcesHTML(s) {
  return [s.need,s.location,{evidence:s.supply_evidence}].map((f,i)=>`<p>${chip(f.evidence.label,[t("need"),t("reported"),t("capacity")][i]+": ")}<br>${esc(f.evidence.as_of || t("unknown"))} · ${esc(f.evidence.licence)}<br>${esc(f.evidence.method)}<br>${(f.evidence.source_ids || []).map(id=>{const source=pack.sources.find(x=>x.snapshot_id===id);return source?`<a href="${safeURL(source.original_url)}" target="_blank" rel="noopener">${esc(source.publisher)} · ${esc(id)}</a>`:esc(id);}).join("<br>")}</p>`).join("");
}
function rangeText(s) {return s.need.range?`${num(s.need.range[0])}–${num(s.need.range[1])} kW`:t("rangeUnknown");}
function cardHTML(s) {
  const supply=t({no_documented_asset:"supplyUnknown",documented_unknown_capacity:"supplyUnknownCapacity",documented_known_capacity:"supplyKnown"}[s.supply]);
  const tier=s.tier || t("unknown");
  return `<div class="site-heading"><p class="eyebrow">${esc(t("rank"))} ${s.rank ?? "—"} · ${esc(s.kind.replaceAll("_"," "))}</p><h2>${esc(s.name)}</h2><p class="meta">${esc(s.operator)} · ${esc(s.province || pack.title)}</p></div>
    <section class="card-block"><h3>${esc(t("why"))}</h3><p>${esc(s.rank===null?t("unknownNeed"):pack===builtIn?t("need"):pack.service_id.replaceAll("_"," "))}</p><div class="need-number">${num(s.need.value)} ${s.need.value===null?"":"<small>kW</small>"}</div><p class="range-note">${esc(s.need.value===null?s.need.evidence.missing_reason:rangeText(s))}</p><p class="meta" style="margin-top:8px">${esc(supply)}</p></section>
    <section class="card-block"><h3>${esc(t("howSure"))}</h3><p class="certainty-word">${esc(tier)}</p><p>${esc(s.tier ? s.confidence : t("notAssessed"))}</p><p class="meta" style="margin-top:8px">${esc(t("reported"))}: ${esc(s.precision)} · ${s.lat.toFixed(3)}, ${s.lon.toFixed(3)} · EPSG:4326</p></section>
    <section class="card-block check-first"><h3>${esc(t("check"))}</h3><p>${esc(s.question)}</p></section>
    <div class="evidence-chips">${chip(s.need.evidence.label,t("need")+": ")}${chip(s.supply_evidence.label,t("capacity")+": ")}${chip(s.location.evidence.label,t("reported")+": ")}</div>
    <div class="expert-only facts">${fact("storage",`${num(s.storage.value)} ${s.storage.value===null?"":s.storage.unit}`)}${fact("throughput",`${num(s.throughput.value)} ${s.throughput.value===null?"":s.throughput.unit}`)}${fact("margin",`${num(s.margin.value)} ${s.margin.value===null?"":"kW"}`)}${fact("window",s.visit_window.value || t("unknown"))}${fact("energy",s.energy_context.value || t("unknown"))}</div>
    <details class="source-details"><summary>${esc(t("sources"))}</summary><div>${sourcesHTML(s)}<p>${esc(t("originalLanguage"))}</p><p>${esc(pack.limitations.join(" "))}</p></div></details>
    <div class="actions"><button class="quiet" id="copy-coordinates">${esc(t("copy"))}</button><button class="primary" id="site-brief">${esc(t("brief"))}</button></div>
    <div class="expert-only"><button class="quiet" id="download-trace">${esc(t("trace"))}</button></div>`;
}
function areaCard() {
  const has=covered();
  return `<div class="site-heading"><p class="eyebrow">${esc(t("selected"))}</p><h2>${esc(area.name)}</h2><p class="meta">${esc(area.country || "EPSG:4326")} · ${area.lat.toFixed(5)}, ${area.lon.toFixed(5)}</p></div><section class="card-block"><h3>${esc(t("why"))}</h3><p>${esc(t(has?"knownHere":"noData"))}</p><p style="margin-top:12px">${esc(t(has?"knownCopy":"noDataCopy"))}</p></section><section class="card-block"><h3>${esc(t("howSure"))}</h3><p class="certainty-word">${esc(t("unknown"))}</p>${chip("UNKNOWN")}<p style="margin-top:12px">${esc(t("unknownNeed"))}</p></section><section class="card-block check-first"><h3>${esc(t("check"))}</h3><p>${esc(t("checkPlace"))}</p></section><section class="card-block"><h3>${esc(t("needs"))}</h3><p>${esc(t("needsCopy"))}</p></section><div class="actions"><button id="copy-coordinates" class="quiet">${esc(t("copy"))}</button><button id="area-export" class="quiet">${esc(t("areaExport"))}</button></div><p class="meta">Natural Earth names are navigation context. Unlisted places can be chosen by coordinates or on the map.</p>`;
}
function download(name,value,type="application/json") {
  const url=URL.createObjectURL(new Blob([typeof value==="string"?value:JSON.stringify(value,null,2)],{type}));
  const a=document.createElement("a");a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
async function copyCoordinates() {
  const p=selected||area;if(!p)return;const text=`${p.lat.toFixed(5)}, ${p.lon.toFixed(5)}`;
  try{if(!navigator.clipboard)throw Error();await navigator.clipboard.writeText(text);flash(t("copied"));}catch(_){flash(`${t("copyFail")} ${text}`);}
}
function renderCard() {
  $("site-card").innerHTML=selected?cardHTML(selected):area?areaCard():`<p>${esc(t("noData"))}</p>`;
  $("copy-coordinates")?.addEventListener("click",copyCoordinates);
  $("site-brief")?.addEventListener("click",printBrief);
  $("download-trace")?.addEventListener("click",()=>download(`site-${selected.rank ?? selected.id}-trace.json`,{run_id:pack.run_id,site:selected.trace || selected,sources:pack.sources,limitations:pack.limitations}));
  $("area-export")?.addEventListener("click",()=>download("location-evidence-needs.json",{schema_version:"enagis-location-request-v1",location:area,crs:"EPSG:4326",analysis_status:covered()?"package_available":"insufficient_evidence",requirement:null,evidence:"UNKNOWN",required:["registry","production","road_access","service_parameters","documented_supply","local_evaluation"],generated_on:new Date().toISOString()}));
}
function printBrief() {
  if(!selected)return;const s=selected;
  const brief=`<p class="eyebrow">EnaGIS · ${esc(t("rank"))} ${s.rank ?? "—"}</p><h1>${esc(s.name)}</h1><p>${esc(s.operator)} · ${esc(pack.title)}</p><p>${s.lat.toFixed(5)}, ${s.lon.toFixed(5)} · EPSG:4326 · ${esc(s.precision)}</p><h2>${esc(t("why"))}</h2><p>${esc(t("need"))}: ${num(s.need.value)} ${s.need.value===null?"":"kW"} · ${esc(rangeText(s))}</p><p>${esc(t("capacity"))}: ${esc(t({no_documented_asset:"supplyUnknown",documented_unknown_capacity:"supplyUnknownCapacity",documented_known_capacity:"supplyKnown"}[s.supply]))}</p><h2>${esc(t("howSure"))}</h2><p>${esc(s.tier || t("notAssessed"))}</p><div class="check-first"><h2>${esc(t("check"))}</h2><p>${esc(s.question)}</p></div><h2>${esc(t("checklist"))}</h2><p>${esc(t("checklistCopy"))}</p><div class="brief-footer"><p>${esc(t("screeningLine"))}</p><p>${esc(pack.run_id)} · ${esc(s.id)}</p><p>Location: ${esc(s.location.evidence.label)} / ${esc(s.location.evidence.as_of)}. Need: ${esc(s.need.evidence.label)} / ${esc(s.need.evidence.as_of)}. Supply: ${esc(s.supply_evidence.label)}.</p><p>${esc(pack.limitations[0])}</p></div>`;
  $("print-brief").innerHTML=brief;window.print();
}
function renderLens() {
  let html="";
  if(lens==="sure") {
    const comparison=covered()?pack.comparison:null;
    html=`<div class="lens-copy"><h3>${esc(t("howSure"))}</h3><p>${esc(selected?.tier || t("tiersUnknown"))}</p><p>${esc(selected?.need.range?rangeText(selected):t("needUnvalidated"))}</p><h3>${esc(t("validation"))}</h3><p>${esc(pack===builtIn && covered()?t("fieldNone"):t("unknown"))}</p>`;
    if(comparison){const p=comparison.siting.primary;const names={full_model:"Full model",base_model:"Base model",B0:"Production only",B1:"Euclidean production",B2:"Road production",population:"Population only",nearest_presence:"Nearest presence",area_only:"Area only"};
      html+=`<h3>${esc(t("baseline"))}</h3><p class="meta">Documented presence · mean CAR recall · top 20% of CCS per block</p>${Object.entries(p.arms).sort((a,b)=>b[1].mean-a[1].mean).map(([key,r])=>`<div class="bar-row ${key==="full_model"?"full":key==="B0"?"best":""}"><div class="bar-caption"><span>${esc(names[key])}</span><strong>${pct(r.mean)}</strong></div><div class="bar-track"><div class="bar-fill" style="width:${r.mean*100}%"></div></div><p class="meta">95% interval ${r.interval.map(pct).join("–")}</p></div>`).join("")}<p><strong>KILL</strong> · full − best baseline: ${(p.margin_over_best_baseline.estimate*100).toFixed(2)} pp</p><p class="meta">95% margin interval ${p.margin_over_best_baseline.interval.map(v=>(v*100).toFixed(2)).join(" to ")} pp</p><p>${esc(comparison.siting.interpretation)}</p><p class="meta">${comparison.siting.cohort_units} complete CCS · ${comparison.siting.documented_positive_units} positives · ${comparison.siting.positive_blocks} CAR blocks. ${esc(comparison.siting.power)}</p><details><summary>Shipping-point hindcast</summary><div><p>${comparison.hindcast.common_comparison_groups} groups · ${comparison.hindcast.blocks} blocks</p>${Object.entries(comparison.hindcast.arms).map(([key,r])=>`<p>${esc(key)}: Spearman ${r.spearman.toFixed(3)} · 95% ${r.interval.map(v=>v.toFixed(3)).join("–")}</p>`).join("")}<p>Retrospective diagnostic; facility energy and absolute volumes are unvalidated.</p></div></details>`;
    }else html+=`<p>${esc(t("noData"))}</p>`;
    html+=`<p class="meta">${esc(t("originalLanguage"))}</p><a href="limitations.html">${esc(t("limits"))}</a></div>`;
  }
  if(lens==="travel") {
    const s=selected,p=s||area;
    html=`<div class="lens-copy"><h3>${esc(t("access"))}</h3><p>${esc(s?.travel.value || t("unknown"))}</p><p class="meta">${esc(s?.travel.evidence.missing_reason || t("seasonUnknown"))}</p><h3>${esc(t("season"))}</h3><div class="season-controls"><button disabled>${esc(t("dry"))}</button><button disabled>${esc(t("rainy"))}</button></div><input class="season-slider" type="range" min="0" max="100" disabled aria-label="Seasonal access results unavailable"><p class="meta">${esc(t("seasonUnknown"))}</p><h3>${esc(t("window"))}</h3><p>${esc(s?.visit_window.value || t("unknown"))}</p><h3>${esc(t("checklist"))}</h3><p>${esc(t("checklistCopy"))}</p>${p?`<div class="actions"><button id="route-copy" class="quiet">${esc(t("copy"))}</button><a href="https://www.openstreetmap.org/?mlat=${p.lat}&mlon=${p.lon}#map=14/${p.lat}/${p.lon}" target="_blank" rel="noopener">${esc(t("phone"))}</a></div><p class="meta">External maps require internet. Named-place coordinates are approximate.</p>`:""}</div>`;
  }
  if(lens==="works")html=`<div class="lens-copy"><h3>${esc(t("story"))}</h3><div class="story-steps">${[0,1,2,3,4].map(i=>`<button data-story="${i}" aria-label="${esc(t(`story${i}`))}" aria-pressed="${i===storyStep}">${i+1}</button>`).join("")}</div><h3>${esc(t(`story${storyStep}`))}</h3><p>${esc(t(`storyCopy${storyStep}`))}</p><div class="story-controls"><button id="story-back" class="quiet" ${storyStep===0?"disabled":""}>${esc(t("back"))}</button><button id="story-next" class="quiet" ${storyStep===4?"disabled":""}>${esc(t("next"))}</button></div><p class="meta">${esc(t("originalLanguage"))}</p></div>`;
  $("lens-panel").innerHTML=html;
  $("route-copy")?.addEventListener("click",copyCoordinates);
  document.querySelectorAll("[data-story]").forEach(b=>b.addEventListener("click",()=>story(Number(b.dataset.story))));
  $("story-back")?.addEventListener("click",()=>story(storyStep-1));$("story-next")?.addEventListener("click",()=>story(storyStep+1));
}
function story(index) {
  storyStep=Math.max(0,Math.min(4,index));renderLens();
  if(mapReady){map.setPaintProperty("roads","line-opacity",storyStep===1?.85:.35);map.setLayoutProperty("selected-region","visibility",storyStep===0 || storyStep===1?"visible":"none");}
  if(selected)camera(selected.lon,selected.lat,[6,7,8,8,7][storyStep]);
}
function render() {
  renderList();renderCard();renderLens();
  $("area-label").textContent=area?`${area.name}${area.country && area.country!==area.name?" / "+area.country:""}`:pack.title;
  $("map-subtitle").textContent=area?t(covered()?"knownHere":"noData"):t("start");
  $("dataset-status").textContent=pack===builtIn?`${D.verified.phase3.nodes} ${t("locations")} · 2024 · ${pack.region_id}`:`${pack.title} · ${pack.run_id}`;
  $("synthetic-ribbon").hidden=pack.purpose!=="synthetic";$("synthetic-ribbon").textContent=t("synthetic");
  $("thin-haze").hidden=covered() || !$("haze-layer").checked;
  markers.forEach(m=>m.button.setAttribute("aria-pressed",String(selected?.id===m.site.id)));
  if(mapReady){map.setFilter("selected-region",["==",["get","id"],selected?.trace?.reporting_region || ""]);}
  if(fallbackActive)renderFallback();
}
function switchLens(next) {
  lens=next;document.querySelectorAll("[data-lens]").forEach(b=>{if(b.dataset.lens===lens)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current");});
  if(innerWidth<=760){document.body.classList.add("list-open");$("list-drawer").dataset.snap="high";}render();
  if(mapReady){map.setPaintProperty("roads","line-width",lens==="travel"?2:1);map.resize();}
}
function applyLanguage() {
  document.documentElement.lang=lang;$("language").value=lang;
  document.querySelectorAll("[data-i18n]").forEach(e=>{e.textContent=t(e.dataset.i18n);});
  $("place-search").placeholder=t("searchPlaceholder");$("site-filter").placeholder=t("filterPlaceholder");
  $("detail-toggle").textContent=`${t("simple")} / ${t("expert")}`;
  $("detail-toggle").setAttribute("aria-pressed",String(expert));document.body.classList.toggle("expert",expert);render();
}
function layers() {
  if(mapReady){map.setLayoutProperty("roads","visibility",$("roads-layer").checked?"visible":"none");map.setLayoutProperty("selected-region","visibility",$("region-layer").checked?"visible":"none");}
  $("thin-haze").hidden=covered() || !$("haze-layer").checked;if(fallbackActive)renderFallback();
}
function setAreaMarker() {
  if(!mapReady || !area)return;if(areaMarker)areaMarker.remove();
  const el=document.createElement("div");el.className="area-pin";el.setAttribute("aria-label",area.name);
  areaMarker=new maplibregl.Marker({element:el}).setLngLat([area.lon,Math.max(-85,Math.min(85,area.lat))]).addTo(map);
}
function drawMarkers() {
  markers.forEach(m=>m.marker.remove());markers=[];if(!mapReady)return;
  const sites=topSites(),max=Math.max(1,...sites.map(s=>s.need.value || 0));
  map.getSource("sites").setData({type:"FeatureCollection",features:pack.sites.map(s=>({type:"Feature",geometry:{type:"Point",coordinates:[s.lon,s.lat]},properties:{rank:s.rank}}))});
  sites.forEach(s=>{const button=document.createElement("button");button.className="map-pin";button.textContent=s.rank;button.style.width=button.style.height=`${44+14*Math.sqrt((s.need.value || 0)/max)}px`;button.setAttribute("aria-label",`${t("rank")} ${s.rank}: ${s.name}, ${s.operator}`);button.setAttribute("aria-pressed",String(selected?.id===s.id));button.addEventListener("click",e=>{e.stopPropagation();selectSite(s.id);});const marker=new maplibregl.Marker({element:button}).setLngLat([s.lon,s.lat]).addTo(map);markers.push({marker,button,site:s});});
  separateMarkers();
}
function separateMarkers() {
  if(!mapReady)return;const used=[];
  markers.forEach(m=>{const p=map.project([m.site.lon,m.site.lat]);let y=p.y;while(used.some(q=>Math.abs(q.x-p.x)<46 && Math.abs(q.y-y)<46))y+=48;m.marker.setOffset([0,y-p.y]);used.push({x:p.x,y});});
}
function initMap() {
  if(new URLSearchParams(location.search).get("map")==="flat" || !window.maplibregl)return fallback();
  try{
    const initial=selected || area || topSites()[0] || {lon:0,lat:15};
    map=new maplibregl.Map({container:"map",style:{version:8,sources:{},layers:[{id:"background",type:"background",paint:{"background-color":"#DCE6EA"}}]},center:[initial.lon,Math.max(-85,Math.min(85,initial.lat))],zoom:7,attributionControl:false,dragRotate:false,pitchWithRotate:false,renderWorldCopies:false,fadeDuration:0});
    map.touchZoomRotate.disableRotation();map.addControl(new maplibregl.NavigationControl({showCompass:false}),"bottom-right");map.addControl(new maplibregl.ScaleControl({maxWidth:100,unit:"metric"}),"bottom-left");
    map.on("load",()=>{
      map.addSource("world",{type:"geojson",data:world().countries});map.addLayer({id:"world-land",type:"fill",source:"world",paint:{"fill-color":"#EFEBE2"}});map.addLayer({id:"country-lines",type:"line",source:"world",paint:{"line-color":"#B8B2A7","line-width":.6}});
      const empty={type:"FeatureCollection",features:[]};
      for(const id of ["provinces","regions","roads"])map.addSource(id,{type:"geojson",data:pack===builtIn?context()[id]:id==="provinces"?pack.coverage:empty});
      map.addLayer({id:"local-land",type:"fill",source:"provinces",paint:{"fill-color":"#EFEBE2"}});
      map.addLayer({id:"selected-region",type:"fill",source:"regions",filter:["==",["get","id"],selected?.trace?.reporting_region || ""],layout:{visibility:"none"},paint:{"fill-color":"#C7BFAE","fill-opacity":.32}});
      map.addLayer({id:"roads",type:"line",source:"roads",paint:{"line-color":"#AAA297","line-width":1,"line-opacity":.5}});
      map.addLayer({id:"coverage-line",type:"line",source:"provinces",paint:{"line-color":"#6C7777","line-width":.8,"line-dasharray":[4,3]}});
      map.addSource("sites",{type:"geojson",data:{type:"FeatureCollection",features:[]}});map.addLayer({id:"other-sites",type:"circle",source:"sites",paint:{"circle-color":"#718078","circle-radius":3,"circle-opacity":.45}});
      mapReady=true;drawMarkers();if(area){camera(area.lon,area.lat,8);setAreaMarker();}else fitSites();render();$("map-status").textContent="Local world map ready. Pan, zoom and select locations.";
    });
    map.on("moveend",separateMarkers);map.on("click",e=>selectArea({name:`${e.lngLat.lat.toFixed(4)}, ${e.lngLat.lng.toFixed(4)}`,lat:e.lngLat.lat,lon:e.lngLat.lng,kind:"map_point",country:""}));
    map.on("mousemove",e=>{$("coordinate-readout").textContent=`${e.lngLat.lat.toFixed(3)}, ${e.lngLat.lng.toFixed(3)} · EPSG:4326`;});
    map.on("error",()=>{if(!mapReady)fallback();});
  }catch(_){fallback();}
}
function fallback() {
  if(map){map.remove();map=null;}mapReady=false;fallbackActive=true;$("map").hidden=true;$("fallback-map").hidden=false;fitSites();renderFallback();$("map-status").textContent="Flat geographic map loaded. Pan and zoom controls are available.";
}
function renderFallback() {
  const host=$("fallback-map"),width=host.clientWidth || 1200,height=host.clientHeight || 700;
  const span=fallbackCamera.width,ys=span*height/width;
  const project=([x,y])=>[(x-fallbackCamera.lon)/span*width+width/2,(fallbackCamera.lat-y)/ys*height+height/2];
  const paths=(features,cls)=>features.map(f=>{const g=f.geometry;const lines=g.type==="MultiPolygon"?g.coordinates.flat():g.type==="Polygon"?g.coordinates:g.type==="MultiLineString"?g.coordinates:[g.coordinates];return lines.map(line=>`<path class="${cls}" d="M${line.map(c=>project(c).map(v=>v.toFixed(2)).join(",")).join("L")}${g.type.includes("Polygon")?"Z":""}"/>`).join("");}).join("");
  const taken=[];const pins=topSites().map(s=>{let [x,y]=project([s.lon,s.lat]);const sourceY=y;while(taken.some(p=>Math.abs(p[0]-x)<46 && Math.abs(p[1]-y)<46))y+=48;taken.push([x,y]);return `<g><line x1="${x}" y1="${sourceY}" x2="${x}" y2="${y}" stroke="#B9B4A9"/><circle cx="${x}" cy="${sourceY}" r="2" fill="#0F766E"/><circle class="fallback-pin ${selected?.id===s.id?"active":""}" data-site="${esc(s.id)}" tabindex="0" role="button" aria-label="${esc(s.name)} rank ${s.rank}" cx="${x}" cy="${y}" r="22"/><text class="${selected?.id===s.id?"active":""}" x="${x}" y="${y}">${s.rank}</text></g>`;}).join("");
  const areaPoint=area?project([area.lon,area.lat]):null;
  const roads=pack===builtIn?context().roads.features:[];
  host.innerHTML=`<svg class="fallback-svg" viewBox="0 0 ${width} ${height}" aria-label="Flat geographic world map">${paths(world().countries.features,"fallback-land")}${$("roads-layer").checked?paths(roads,"fallback-road"):""}${pins}${areaPoint?`<circle cx="${areaPoint[0]}" cy="${areaPoint[1]}" r="8" fill="#0F766E" stroke="white" stroke-width="3"/>`:""}</svg><p class="fallback-message">Flat geographic map · drag to pan</p><div class="fallback-controls"><button id="flat-minus" class="quiet" aria-label="Zoom out">−</button><button id="flat-plus" class="quiet" aria-label="Zoom in">+</button></div>`;
  host.querySelectorAll("[data-site]").forEach(el=>{el.addEventListener("click",e=>{e.stopPropagation();selectSite(el.dataset.site);});el.addEventListener("keydown",e=>{if(e.key==="Enter" || e.key===" "){e.preventDefault();selectSite(el.dataset.site);}});});
  $("flat-minus").addEventListener("click",()=>{fallbackCamera.width=Math.min(360,span*1.5);renderFallback();});$("flat-plus").addEventListener("click",()=>{fallbackCamera.width=Math.max(.05,span/1.5);renderFallback();});
  const svg=host.querySelector("svg");let start;
  svg.addEventListener("pointerdown",e=>{if(e.target.hasAttribute("data-site"))return;start={x:e.clientX,y:e.clientY};svg.setPointerCapture(e.pointerId);});
  svg.addEventListener("pointerup",e=>{if(!start)return;const dx=e.clientX-start.x,dy=e.clientY-start.y;if(Math.abs(dx)+Math.abs(dy)>8){fallbackCamera.lon=Math.max(-180,Math.min(180,fallbackCamera.lon-dx/width*span));fallbackCamera.lat=Math.max(-90,Math.min(90,fallbackCamera.lat+dy/height*ys));renderFallback();}else{const r=svg.getBoundingClientRect();const lon=fallbackCamera.lon+((e.clientX-r.left)/r.width-.5)*span,lat=fallbackCamera.lat-( (e.clientY-r.top)/r.height-.5)*ys;if(V.point(lon,lat))selectArea({name:`${lat.toFixed(4)}, ${lon.toFixed(4)}`,lon,lat,kind:"map_point",country:""});}start=null;});
}
async function importPackage(file) {
  if(!file)return;try{
    if(file.size>30*1024*1024)throw Error("Regional package exceeds 30 MB");
    const next=V.validatePackage(JSON.parse(await file.text()));
    pack={...next,comparison:null};selected=topSites()[0] || pack.sites[0] || null;area=null;
    $("import-status").textContent=t("imported");$("site-filter").value="";drawMarkers();fitSites();render();
    // A regional package replaces the active data; it does not mix with benchmark results.
    if(mapReady){map.getSource("provinces").setData(pack.coverage);map.getSource("regions").setData({type:"FeatureCollection",features:[]});map.getSource("roads").setData({type:"FeatureCollection",features:[]});}
    document.querySelector(".help").open=false;flash(t("imported"));
  }catch(error){$("import-status").textContent=error.message;flash(error.message);}
}
function restore() {
  pack=builtIn;area=null;selected=allBuiltIn.find(s=>s.rank===1);$("site-filter").value="";
  if(mapReady){for(const id of ["provinces","regions","roads"])map.getSource(id).setData(context()[id]);}
  drawMarkers();fitSites();render();document.querySelector(".help").open=false;
}
function sheets() {
  ["list","detail"].forEach(name=>{const sheet=$(`${name}-${name==="list"?"drawer":"sheet"}`),handle=$(`${name}-handle`);sheet.dataset.snap="mid";let y;
    handle.addEventListener("pointerdown",e=>{y=e.clientY;handle.setPointerCapture(e.pointerId);});
    handle.addEventListener("pointerup",e=>{if(y===undefined)return;const delta=e.clientY-y;if(Math.abs(delta)>12)sheet.dataset.snap=delta<0?"high":"low";y=undefined;});
    handle.addEventListener("click",()=>{const order=["low","mid","high"];sheet.dataset.snap=order[(order.indexOf(sheet.dataset.snap)+1)%3];});
  });
}
$("place-search").addEventListener("input",renderSearch);
$("place-search").addEventListener("keydown",e=>{if(e.key==="Escape"){closeSearch();return;}if(["ArrowDown","ArrowUp"].includes(e.key) && searchMatches.length){e.preventDefault();searchIndex=(searchIndex+(e.key==="ArrowDown"?1:-1)+searchMatches.length)%searchMatches.length;$("search-results").querySelectorAll("button").forEach((b,i)=>b.setAttribute("aria-selected",String(i===searchIndex)));$("place-search").setAttribute("aria-activedescendant",`result-${searchIndex}`);$(`result-${searchIndex}`).scrollIntoView({block:"nearest"});}if(e.key==="Enter" && searchMatches.length){e.preventDefault();chooseResult(searchIndex<0?0:searchIndex);}});
document.addEventListener("click",e=>{if(!e.target.closest(".search-wrap"))closeSearch();});
document.querySelectorAll("[data-lens]").forEach(b=>b.addEventListener("click",()=>switchLens(b.dataset.lens)));
$("site-filter").addEventListener("input",renderList);
$("world-map").addEventListener("click",()=>camera(0,15,1));$("fit-sites").addEventListener("click",fitSites);
$("locate").addEventListener("click",()=>{if(!navigator.geolocation)return flash(t("notLocated"));navigator.geolocation.getCurrentPosition(p=>selectArea({name:t("locate"),lat:p.coords.latitude,lon:p.coords.longitude,kind:"device",country:""}),()=>flash(t("notLocated")),{timeout:10000,maximumAge:0});});
["roads-layer","region-layer","haze-layer"].forEach(id=>$(id).addEventListener("change",layers));
$("language").addEventListener("change",()=>{lang=$("language").value;try{localStorage.setItem("enagis-language",lang);}catch(_){}applyLanguage();});
$("detail-toggle").addEventListener("click",()=>{expert=!expert;try{localStorage.setItem("enagis-detail",expert?"expert":"simple");}catch(_){}applyLanguage();});
$("region-file").addEventListener("change",e=>importPackage(e.target.files[0]));$("restore").addEventListener("click",restore);
$("export-shortlist").addEventListener("click",e=>{
  if(pack===builtIn)return;e.preventDefault();
  const quote=value=>`"${String(value ?? "UNKNOWN").replaceAll('"','""')}"`;
  const rows=[["run_id","node_id","rank","name","latitude","longitude","requirement_kw","lower_kw","upper_kw","evidence","supply_state","question"],...topSites().map(s=>[pack.run_id,s.id,s.rank,s.name,s.lat,s.lon,s.need.value,s.need.range?.[0]??null,s.need.range?.[1]??null,s.need.evidence.label,s.supply,s.question])];
  download("regional-shortlist.csv",rows.map(row=>row.map(quote).join(",")).join("\n"),"text/csv");
});
$("home").addEventListener("click",e=>{e.preventDefault();restore();switchLens("first");});
const mobileToggle=document.createElement("button");mobileToggle.className="mobile-list-toggle";mobileToggle.id="mobile-list-toggle";mobileToggle.textContent=t("locations");mobileToggle.addEventListener("click",()=>document.body.classList.toggle("list-open"));$("workspace").appendChild(mobileToggle);
window.addEventListener("resize",()=>{if(mapReady)map.resize();if(fallbackActive)renderFallback();});
window.EnaApp={state:()=>({lens,selected:selected?.id || null,area,region:pack.region_id,expert,lang,camera:mapReady?{center:map.getCenter().toArray(),zoom:map.getZoom()}:fallbackCamera}),importPackage,restore,selectArea};
function loadCandidates() {
  if(builtIn.sites.length===D.verified.phase3.nodes)return;
  allBuiltIn=JSON.parse($("candidate-data").textContent).map(V.fromNode);builtIn.sites=allBuiltIn;
  if(pack===builtIn && mapReady)drawMarkers();
}
sheets();if(innerWidth<=760){document.body.classList.add("list-open");$("list-drawer").dataset.snap="high";}applyLanguage();window.addEventListener("load",()=>{initMap();requestAnimationFrame(()=>setTimeout(loadCandidates,0));},{once:true});
performance.mark("enagis-first-list");
