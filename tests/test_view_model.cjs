const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const V=require("../web/view-model.js");
const world=JSON.parse(fs.readFileSync("web/assets/world.json"));
const source={snapshot_id:"fixture-source",publisher:"Synthetic fixture",licence:"MIT",effective_on:"2026-10-09",redistribution:"permitted"};
const evidence={label:"ESTIMATED",as_of:"2026-10-09",licence:"MIT",method:"Synthetic fixture",source_ids:["fixture-source"],missing_reason:null};
const unknown=V.unknown("Fixture intentionally missing");
function fixture(){return {schema_version:"enagis-region-view-v1",crs:"EPSG:4326",region_id:"fixture:rwanda",title:"Synthetic Rwanda fixture",run_id:"fixture:regional-v1",purpose:"synthetic",commodity_id:"wheat_non_durum",service_id:"ambient_air_aeration",period_start:"2024-01-01",period_end:"2024-12-31",limitations:["Synthetic only; no local accuracy claim"],sources:[source],coverage:{type:"FeatureCollection",features:[{type:"Feature",geometry:{type:"Polygon",coordinates:[[[29,-3],[31,-3],[31,0],[29,0],[29,-3]]]},properties:{}}]},sites:[{id:"fixture:node",name:"Synthetic collection point",operator:"Fixture",rank:1,province:"Test",lon:30.06,lat:-1.95,kind:"storage",precision:"P2",question:"Does this fixture node exist?",need:{value:12,range:[8,16],unit:"kW",evidence},margin:{...unknown,unit:"kW"},location:{value:{crs:"EPSG:4326",longitude:30.06,latitude:-1.95},evidence:{...evidence,label:"OBSERVED"}},storage:{...unknown,unit:"t"},throughput:{...unknown,unit:"t/year"},travel:unknown,visit_window:unknown,energy_context:unknown,supply:"no_documented_asset",supply_evidence:{...evidence,label:"INFERRED"},tier:null,confidence:"Unknown",verification:"Not collected"}]};}
test("offline search resolves accents, capitals, countries and coordinate zero",()=>{
  for(const term of ["Kigali","Sydney","Reykjavik","Manaus","Longyearbyen"]){assert.equal(V.normalize(V.search(term,world,[])[0].name),V.normalize(term));}
  assert.equal(V.search("Rwanda",world,[])[0].kind,"country");
  const sites=Array.from({length:20},(_,i)=>({name:`Facility ${i}`,operator:"Viterra Canada",province:"SK",id:`site:${i}`,lat:52,lon:-105}));
  assert.equal(V.search("Canada",world,sites)[0].kind,"country");
  assert.deepEqual(V.parseCoordinates("0, 0"),{name:"0, 0",lat:0,lon:0,kind:"coordinates",country:""});
  assert.equal(V.parseCoordinates("90.1, 30"),null);assert.equal(V.parseCoordinates("1, 181"),null);
  assert.equal(V.parseCoordinates("89.5, 120").lat,89.5);
});
test("compatible new region works without Canada-specific site logic",()=>{assert.equal(V.validatePackage(fixture()).region_id,"fixture:rwanda");});
test("unknown is not zero and false precision is rejected",()=>{
  const p=fixture();p.sites[0].margin.value=0;assert.throws(()=>V.validatePackage(p),/UNKNOWN must be null/);
  const q=fixture();q.sites[0].need.range=[12,12];assert.throws(()=>V.validatePackage(q),/Invalid requirement range/);
});
test("package identity, evidence source and coverage mismatches are rejected",()=>{
  const a=fixture();a.sites.push(structuredClone(a.sites[0]));assert.throws(()=>V.validatePackage(a),/identity/);
  const b=fixture();b.sites[0].need.evidence={...evidence,source_ids:["missing"]};assert.throws(()=>V.validatePackage(b),/source reference/);
  const c=fixture();c.sites[0].lon=35;c.sites[0].location.value.longitude=35;assert.throws(()=>V.validatePackage(c),/outside/);
  const d=fixture();d.sites[0].location.value.longitude=35;assert.throws(()=>V.validatePackage(d),/must agree/);
});
test("coverage respects holes and never silently labels a gap as no need",()=>{
  const g=fixture().coverage;g.features[0].geometry.coordinates.push([[29.5,-2.5],[30.5,-2.5],[30.5,-1],[29.5,-1],[29.5,-2.5]]);
  assert.equal(V.contains(g,[30,-2]),false);assert.equal(V.contains(g,[29.2,-2]),true);
});
test("invalid display fields cannot enter a partially broken application state",()=>{
  const a=fixture();a.sites[0].kind=null;assert.throws(()=>V.validatePackage(a),/must be text/);
  const b=fixture();b.limitations="not an array";assert.throws(()=>V.validatePackage(b),/must be text/);
  const c=fixture();c.sites[0].need={...V.unknown("Not supplied"),unit:"kW",range:[0,12]};assert.throws(()=>V.validatePackage(c),/numeric range/);
});
