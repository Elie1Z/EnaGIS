/* Verify human CSVs without publishing personal information or changing the snapshot.
 * node live/tools/check-hero-verification.cjs [desk-check.csv] [phone-log.csv]
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {ROOT,DIR,sha}=require('./hero-contract.cjs'),V=require('../js/hero-verification.js');
const protocol=JSON.parse(fs.readFileSync(path.join(DIR,'../verification-protocol.json'),'utf8'));
assert.equal(protocol.sha256,sha(fs.readFileSync(path.join(ROOT,'docs/hero-verification-protocol.md'))),'Protocol changed');
const targets=new Set(JSON.parse(fs.readFileSync(path.join(DIR,'verification-targets.json'),'utf8')).map(t=>t.id));
const all={};
for(const [i,kind,cols] of [[0,'desk',V.DESK],[1,'phone',V.PHONE]]) {
  const file=process.argv[i+2]||path.join(DIR,'../'+(kind==='desk'?'desk-check.csv':'phone-log.csv'));
  const parsed=V.parseCSV(fs.readFileSync(file,'utf8'));assert.deepEqual(parsed.header,cols,'Unexpected '+kind+' schema');
  const seen=new Set();
  for(const r of parsed.rows){assert.ok(targets.has(r.site_id),'Unknown frozen target');
    assert.ok(kind==='desk'?V.validateDesk(r):V.validatePhone(r,protocol),'Incomplete/inconsistent '+kind+' record');
    const key=[r.site_id,r.reviewer,r.checked_at].join('|');assert.ok(!seen.has(key),'Duplicate record');seen.add(key);
  }all[kind]=parsed.rows;
}
const completed=all.phone.filter(r=>r.status==='completed');
console.log(JSON.stringify({status:'PASS',desk_reviews:all.desk.length,desk_sites:new Set(all.desk.map(r=>r.site_id)).size,
  phone_attempts:all.phone.length,completed_calls:completed.length,phone_sites:new Set(completed.map(r=>r.site_id)).size,
  confirmed:completed.filter(r=>r.outcome==='CONFIRMED_ACTIVITY').length,rejected:completed.filter(r=>r.outcome==='REJECTED_ACTIVITY').length,
  inconclusive:completed.filter(r=>r.outcome==='INCONCLUSIVE').length,field_visits:0},null,2));
