'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
require('../../live/js/config-v2.js');
const E = require('../../live/js/engine-v2.js');
const {makeFixture} = require('./fixture.cjs');
const baseline = require('./legacy-scenario-hashes.json');

for (const [model, expected] of Object.entries(baseline.hashes)) {
  test(`legacy ${model}: full result equals the pre-refactor baseline`, () => {
    const result = E.analyze(makeFixture(), {model, seed: baseline.seed, draws: baseline.draws});
    result.meta.elapsed_ms = 0;
    const digest = crypto.createHash('sha256').update(JSON.stringify(result)).digest('hex');
    assert.equal(digest, expected);
  });
}
