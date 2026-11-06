/* One geographic camera, from satellite Earth to the analysis workspace. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const shell = $('landing'), map = EnaApp.map();
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = reduced.matches, focused = false, dragging = false;
  let frame = 0, last = 0, request = 0, flight = null;

  function motion() {
    $('orbit-motion').textContent = paused ? 'Resume rotation' : 'Pause rotation';
    $('orbit-motion').setAttribute('aria-pressed', String(paused));
  }
  function rotate(now) {
    if (shell.hidden) return;
    const dt = Math.min((now - last) / 1000, .05); last = now;
    if (!paused && !focused && !dragging && !document.hidden && !map.isMoving()) {
      const c = map.getCenter(); map.jumpTo({center: [c.lng + dt * 1.3, c.lat]});
    }
    frame = requestAnimationFrame(rotate);
  }
  function homeCamera() {
    map.resize();
    map.jumpTo({center: [20, 12], zoom: innerWidth < 800 ? .2 : 1.45,
      padding: {left: innerWidth < 800 ? 0 : Math.round(innerWidth * .48), right: 0,
        top: 0, bottom: innerWidth < 800 ? Math.round(innerHeight * .38) : 0}, bearing: 0, pitch: 0});
  }
  function imageryLabel() {
    $('orbit-imagery').textContent = EnaApp.state().base === 'paper'
      ? 'Imagery unavailable · geographic outline' : 'Satellite Earth · drag to explore';
  }
  map.on('style.load', imageryLabel);
  map.on('dragstart', () => { dragging = true; });
  map.on('dragend', () => { dragging = false; });
  map.on('zoomstart', e => { if (e.originalEvent) { paused = true; motion(); } });
  $('orbit-motion').onclick = () => { paused = !paused; focused = false; motion(); };
  reduced.addEventListener('change', () => { paused = reduced.matches; motion(); if (reduced.matches && flight) finishFlight(true); });
  $('orbit-query').addEventListener('focus', () => { focused = true; });
  $('orbit-query').addEventListener('blur', () => { focused = false; });
  $('orbit-start').onclick = () => $('orbit-query').focus();

  function revealWorkspace() {
    document.body.classList.remove('landing-open', 'earth-flight');
    $('orbit-flight').hidden = true;
    $('model').focus({preventScroll: true});
  }
  function finishFlight(jump = false) {
    if (!flight) return;
    const current = flight; flight = null;
    map.off('moveend', current.done);
    if (jump) { map.stop(); map.jumpTo(current.camera); }
    revealWorkspace();
  }
  function select(area) {
    request++; cancelAnimationFrame(frame); map.stop();
    if (flight) { map.off('moveend', flight.done); flight = null; }
    EnaApp.previewArea(area, {keepCamera: true});
    shell.hidden = true;
    document.body.classList.add('earth-flight');
    $('orbit-flight').hidden = false;
    $('flight-place').textContent = area.name;
    $('flight-status').textContent = 'Bringing your area into view…';
    const mobile = innerWidth < 800, b = area.bbox;
    const padding = mobile ? {left: 28, right: 28, top: 150, bottom: 260}
      : {left: 450, right: 100, top: 110, bottom: 90};
    const camera = map.cameraForBounds([[b[0], b[1]], [b[2], b[3]]], {padding, maxZoom: 13});
    camera.padding = padding;
    const done = () => finishFlight();
    flight = {camera, done};
    map.once('moveend', done);
    map.flyTo({...camera, duration: reduced.matches ? 0 : 4200, curve: 1.2, essential: false});
    if (!map.isMoving()) finishFlight();
  }
  $('flight-skip').onclick = () => finishFlight(true);
  window.addEventListener('keydown', e => { if (e.key === 'Escape' && flight) finishFlight(true); });
  window.addEventListener('enagis:exploration-progress', e => {
    if (flight) $('flight-status').textContent = e.detail;
  });
  $('orbit-query').addEventListener('input', () => { request++; $('orbit-results').replaceChildren(); });
  $('orbit-search').addEventListener('submit', async e => {
    e.preventDefault(); const q = $('orbit-query').value.trim(); if (!q) return;
    const id = ++request; focused = true;
    $('orbit-results').replaceChildren(); $('orbit-status').textContent = 'Finding your place…';
    try {
      const coords = q.match(/^\s*(-?\d+(?:\.\d+)?)\s*[,;]\s*(-?\d+(?:\.\d+)?)\s*$/);
      let results;
      if (coords) {
        const lat = +coords[1], lon = +coords[2];
        if (Math.abs(lat) > 85 || Math.abs(lon) > 180) throw Error('Use latitude between −85 and 85 and longitude between −180 and 180');
        const d = .025;
        results = [{...EnaSources.areaFromView([Math.max(-180, lon-d), lat-d, Math.min(180, lon+d), lat+d], `Around ${lat}, ${lon}`),
          lat, lon, display_name: 'Selected coordinates · 0.05° study window'}];
      } else results = await EnaSources.geocode(q);
      if (id !== request) return;
      if (!results.length) { $('orbit-status').textContent = 'No matching place yet. Try adding its country or enter coordinates.'; return; }
      if (coords) { select(results[0]); return; }
      $('orbit-status').textContent = 'Choose your place to begin exploring.';
      results.forEach(area => {
        const b = document.createElement('button'); b.type = 'button'; b.textContent = area.name;
        const small = document.createElement('small'); small.textContent = area.display_name;
        b.append(small); b.onclick = () => select(area); $('orbit-results').append(b);
      });
    } catch (err) {
      if (id === request) $('orbit-status').textContent = `${err.message || 'Search unavailable'}. Try coordinates or open a saved analysis.`;
    }
  });
  function dismiss() {
    request++; cancelAnimationFrame(frame);
    if (flight) finishFlight(true);
    shell.hidden = true; map.stop();
    document.body.classList.remove('landing-open', 'earth-flight');
    $('orbit-flight').hidden = true;
    map.setPadding({top: 0, bottom: 0, left: 0, right: 0}); map.resize();
  }
  $('orbit-open').onclick = () => $('open-file').click();
  function show(query = '') {
    dismiss(); EnaApp.cancelExploration();
    shell.hidden = false; document.body.classList.add('landing-open');
    $('orbit-status').textContent = "Find your place. We'll take you there.";
    $('orbit-results').replaceChildren(); $('orbit-query').value = query;
    EnaApp.showEarth(); homeCamera(); imageryLabel();
    last = performance.now(); frame = requestAnimationFrame(rotate);
    if (query) { $('orbit-query').focus(); $('orbit-search').requestSubmit(); }
  }
  window.EnaLanding = {select, dismiss, show};
  const params = new URLSearchParams(location.search);
  if (params.has('q') || params.has('demo')) dismiss();
  else { homeCamera(); motion(); imageryLabel(); last = performance.now(); frame = requestAnimationFrame(rotate); }
  window.addEventListener('resize', () => { if (!shell.hidden) homeCamera(); });
})();

