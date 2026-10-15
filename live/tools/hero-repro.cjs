'use strict';
const assert = require('node:assert/strict');
const {read, engine, options, ranking, validateInput, verifyManifest} = require('./hero-contract.cjs');
const manifest = verifyManifest(), input = read('input.json');
validateInput(input);
const E = engine(), first = JSON.stringify(ranking(E.analyze(input, options))), second = JSON.stringify(ranking(E.analyze(input, options)));
assert.equal(first, second, 'Repeated rankings differ');
assert.equal(first, JSON.stringify(read('expected.json')), 'Frozen site order, energy, rank or tier changed');
console.log(`PASS hero-repro: ${manifest.files.length} hashes; byte-identical dry/rainy rankings across two runs and expected.json; offline.`);
