/* Presentation contracts only. This module never fits, allocates, ranks or estimates. */
(function (root) {
  "use strict";
  const labels = new Set(["OBSERVED", "PREDICTED", "ESTIMATED", "INFERRED", "UNKNOWN"]);
  const unknown = (reason) => ({value: null, evidence: {label: "UNKNOWN", as_of: null,
    licence: "Not supplied", source_ids: [], method: "Not supplied", missing_reason: reason}});
  const normalize = (text) => String(text ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  function point(lon, lat) {
    return typeof lon === "number" && typeof lat === "number" && Number.isFinite(lon)
      && Number.isFinite(lat) && lon >= -180 && lon <= 180 && lat >= -90 && lat <= 90;
  }
  function parseCoordinates(text) {
    const match = text.trim().match(/^(-?\d+(?:\.\d+)?)\s*[,;]\s*(-?\d+(?:\.\d+)?)$/);
    if (!match) return null;
    const lat = Number(match[1]), lon = Number(match[2]);
    return point(lon, lat) ? {name: `${lat}, ${lon}`, lat, lon, kind: "coordinates", country: ""} : null;
  }
  function fromNode(n) {
    const p = n.node.location.point.value;
    const power = n.requirement.electrical_kw;
    const val = power.value;
    const range = val && val.lower !== val.upper ? [val.lower, val.upper] : null;
    return {id: n.node_id, name: n.facility.name.value, operator: n.facility.operator.value,
      rank: n.rank, province: n.province, lon: p.longitude, lat: p.latitude,
      precision: n.node.location.precision, kind: n.node.node_type, location: n.node.location.point,
      need: {value: val?.central ?? null, range, unit: "kW", evidence: power.evidence},
      cycle: {...n.requirement.electricity_kwh, unit: "kWh / cooling cycle"},
      storage: {...n.storage_capacity.original.amount, unit: "t · all crops"},
      throughput: {...n.assigned_tonnes_per_reporting_period, unit: "t / reporting year"},
      supply: n.supply.state, supply_evidence: n.supply.evidence,
      margin: {...n.gap.capacity_minus_requirement_kw, unit: "kW"},
      bucket: n.gap.bucket, question: n.verification_question,
      tier: null, confidence: "Unknown", verification: "Not collected",
      travel: unknown("No approved route or seasonal travel result in this package"),
      visit_window: unknown("No sourced visit window"), energy_context: unknown("No consumed grid or tariff layer"),
      trace: n};
  }
  function evidence(field, name, sources) {
    if (!field || !Object.hasOwn(field, "value") || !field.evidence || !labels.has(field.evidence.label))
      throw Error(`${name}: a value and valid evidence label are required`);
    const e = field.evidence;
    if (e.label === "UNKNOWN" && field.value !== null) throw Error(`${name}: UNKNOWN must be null`);
    if (field.value === null && (!e.missing_reason || e.label !== "UNKNOWN"))
      throw Error(`${name}: missing values need an UNKNOWN reason`);
    if (field.value !== null && (!/^\d{4}-\d{2}-\d{2}$/.test(e.as_of || "") || !e.licence || !e.method || !e.source_ids?.length))
      throw Error(`${name}: source, date, licence and method are required`);
    if (field.value !== null && e.source_ids.some(id => !sources.has(id)))
      throw Error(`${name}: source reference not included`);
  }
  function validatePackage(data) {
    if (!data || data.schema_version !== "enagis-region-view-v1") throw Error("Unsupported regional package version");
    if (!data.region_id || !data.title || !data.run_id || data.crs !== "EPSG:4326"
      || !["real", "synthetic"].includes(data.purpose) || !data.limitations?.length)
      throw Error("Region, run, purpose, CRS and limitations are required");
    if (![data.region_id,data.title,data.run_id].every(v => typeof v === "string")
      || !Array.isArray(data.limitations) || !data.limitations.every(v => typeof v === "string" && v.trim()))
      throw Error("Package identity and limitations must be text");
    if (!data.commodity_id || !data.service_id || !/^\d{4}-\d{2}-\d{2}$/.test(data.period_start || "")
      || !/^\d{4}-\d{2}-\d{2}$/.test(data.period_end || "") || data.period_start > data.period_end)
      throw Error("Commodity, service and valid analysis period are required");
    if (!Array.isArray(data.sites) || data.sites.length > 5000 || !Array.isArray(data.sources))
      throw Error("A package must contain up to 5,000 sites and its source list");
    const sourceIds = new Set();
    data.sources.forEach(s => {
      if (!s.snapshot_id || sourceIds.has(s.snapshot_id) || !s.publisher || !s.licence || !s.effective_on
        || s.redistribution !== "permitted") throw Error("Every source must be unique, dated and permitted for redistribution");
      sourceIds.add(s.snapshot_id);
    });
    if (!data.coverage || data.coverage.type !== "FeatureCollection") throw Error("Explicit geographic coverage is required");
    function geometry(g) {
      if (!g || !["Polygon", "MultiPolygon"].includes(g.type)) throw Error("Coverage requires polygon geometry");
      const rings = g.type === "Polygon" ? g.coordinates : g.coordinates.flat();
      if (!rings.length) throw Error("Empty coverage polygon");
      rings.forEach(r => {
        if (r.length < 4 || r.some(c => !Array.isArray(c) || !point(c[0], c[1]))
          || r[0][0] !== r.at(-1)[0] || r[0][1] !== r.at(-1)[1]) throw Error("Invalid coverage coordinates");
      });
    }
    data.coverage.features.forEach(f => geometry(f.geometry));
    if (data.sites.length && !data.coverage.features.length) throw Error("Sites require a coverage polygon");
    const ids = new Set(), ranks = new Set();
    data.sites.forEach(s => {
      if (!s.id || ids.has(s.id) || !s.name || !point(s.lon, s.lat)) throw Error("Site identity or coordinates invalid");
      if (![s.id,s.name,s.operator,s.kind,s.precision,s.question].every(v => typeof v === "string" && v.trim()))
        throw Error("Site names, kind, precision and question must be text");
      ids.add(s.id);
      if (s.rank !== null && (!Number.isInteger(s.rank) || s.rank < 1 || ranks.has(s.rank))) throw Error("Ranks must be unique positive integers or null");
      if (s.rank !== null) ranks.add(s.rank);
      if (!s.question || !s.precision || s.need?.unit !== "kW" || s.margin?.unit !== "kW") throw Error("Site question, precision and explicit kW units are required");
      ["need", "margin", "location", "storage", "throughput", "travel", "visit_window", "energy_context"].forEach(k => evidence(s[k], k, sourceIds));
      evidence({value:s.supply,evidence:s.supply_evidence},"supply",sourceIds);
      for (const key of ["need","margin","storage","throughput"]) {
        if (!s[key].unit || (s[key].value !== null && (typeof s[key].value !== "number" || !Number.isFinite(s[key].value)))) throw Error(`${key}: numeric value and explicit units required`);
      }
      if (s.need.value !== null && (typeof s.need.value !== "number" || !Number.isFinite(s.need.value) || s.need.value < 0)) throw Error("Invalid requirement");
      if (s.need.value === null && s.need.range !== null) throw Error("Unknown requirement cannot have a numeric range");
      if (s.need.range !== null && (!Array.isArray(s.need.range) || s.need.range.length !== 2
        || s.need.range.some(v => !Number.isFinite(v) || v < 0) || s.need.range[0] > s.need.value
        || s.need.range[1] < s.need.value || s.need.range[0] >= s.need.range[1])) throw Error("Invalid requirement range");
      if (!s.location.value || s.location.value.longitude !== s.lon || s.location.value.latitude !== s.lat
        || s.location.value.crs !== "EPSG:4326") throw Error("Location coordinates must agree with EPSG:4326 evidence");
      if (!["no_documented_asset", "documented_known_capacity", "documented_unknown_capacity"].includes(s.supply)) throw Error("Invalid supply state");
      if (![null, "Robust", "Contested", "Verify first"].includes(s.tier)) throw Error("Invalid tier");
      if (!contains(data.coverage, [s.lon, s.lat])) throw Error("Site outside declared package coverage");
    });
    return data;
  }
  function inRing(ring, [x, y]) {
    let inside = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const [xi, yi] = ring[i], [xj, yj] = ring[j];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
    }
    return inside;
  }
  function contains(collection, p) {
    return collection.features.some(f => {
      const polygons = f.geometry.type === "MultiPolygon" ? f.geometry.coordinates : [f.geometry.coordinates];
      return polygons.some(rings => inRing(rings[0], p) && !rings.slice(1).some(r => inRing(r, p)));
    });
  }
  function search(text, world, sites) {
    const coordinates = parseCoordinates(text);
    if (coordinates) return [coordinates];
    const term = normalize(text.trim());
    if (term.length < 2) return [];
    const found = sites.filter(s => normalize(`${s.name} ${s.operator} ${s.province} ${s.id}`).includes(term))
      .map(s => ({name: s.name, country: `${s.operator} · ${s.province}`, kind: "site", id: s.id, lat: s.lat, lon: s.lon}));
    const places = world.places.filter(p => normalize([p.name, p.country, ...(p.aliases || [])].join(" ")).includes(term))
      .sort((a, b) => Number(normalize(b.name) === term) - Number(normalize(a.name) === term)
        || Number(Boolean(b.capital)) - Number(Boolean(a.capital)) || a.name.localeCompare(b.name));
    const exact = p => normalize(p.name) === term;
    return [...found.filter(exact), ...places.filter(exact),
      ...found.filter(p => !exact(p)), ...places.filter(p => !exact(p))].slice(0, 12);
  }
  const api = {fromNode, validatePackage, parseCoordinates, search, contains, point, unknown, normalize};
  root.EnaView = api;
  if (typeof module !== "undefined") module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
