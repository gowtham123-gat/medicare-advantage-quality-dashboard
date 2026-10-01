// Runs the dashboard's real JavaScript with a minimal DOM fixture.
// Verifies calculations and filter/event handlers; does not verify browser layout.
import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const html=await fs.readFile(path.join(root,'portfolio/dashboard_preview.html'),'utf8');
const code=html.split('<script>')[1].split('</script>')[0];
class Element{constructor(id){this.id=id;this.value='';this.innerHTML='';this.hidden=false;this.events={};this.classList={toggle(){}};}addEventListener(name,fn){this.events[name]=fn;}setAttribute(){} trigger(event='change'){this.events[event]();}}
const nodes=new Map(['month','region','provider','measure','channel','channelBox','reset','content'].map(id=>[id,new Element(id)]));
const tabs=['executive','measures','outreach','quality'].map(p=>{const e=new Element(p);e.dataset={page:p};return e;});
const context={document:{getElementById:id=>nodes.get(id),querySelectorAll:()=>tabs},window:{},console};
vm.createContext(context);vm.runInContext(code,context,{timeout:10000});
const api=context.window.projectTest;
function assert(value,message){if(!value)throw Error(message)}
function has(text){return nodes.get('content').innerHTML.includes(text)}
assert(api.stats(api.DATA).n===5884,'Eligible denominator mismatch');
assert(api.stats(api.DATA).c===4173,'Compliant numerator mismatch');
assert(api.stats(api.DATA).open===1711,'Open gaps mismatch');
assert(api.stats(api.DATA).members===3075,'Distinct members mismatch');
for(const tab of tabs){tab.trigger('click');assert(nodes.get('content').innerHTML.length>1000,'Page render failed: '+tab.id);}
assert(has('8,020')&&has('66')&&has('99.2%'),'Staging dashboard mismatch');
nodes.get('measure').value='Colorectal Cancer Screening';nodes.get('measure').trigger();tabs[0].trigger('click');
assert(has('57.5%')&&has('924')&&has('393'),'Measure filter mismatch');
nodes.get('month').value='2026-06-01';nodes.get('month').trigger();
const expected=api.stats(api.DATA.filter(r=>r.Measure_Name==='Colorectal Cancer Screening'&&r.Measurement_Month==='2026-06-01'));
assert(has(expected.n.toLocaleString('en-US')),'Combined filters mismatch');
nodes.get('reset').trigger('click');tabs[2].trigger('click');nodes.get('channel').value='Care Coordinator';nodes.get('channel').trigger();
assert(has('66.3%')&&has('193')&&has('128'),'Channel filter mismatch');
nodes.get('reset').trigger('click');tabs[3].trigger('click');nodes.get('provider').value='Provider Group C';nodes.get('provider').trigger();
const auditCount=api.AUDIT.filter(r=>r.Provider_Group==='Provider Group C').length;
assert(has(auditCount.toLocaleString('en-US')),'Audit provider filter mismatch');
nodes.get('reset').trigger('click');tabs[0].trigger('click');
nodes.get('region').value='Unknown region';nodes.get('region').trigger();
assert(has('No records match')&&has('—'),'Empty context handling mismatch');
const report='PASS: JavaScript source executes with zero exceptions.\nPASS: all four page render handlers.\nPASS: baseline metrics agree with SQL.\nPASS: measure, month, combined, outreach and audit filters.\nPASS: reset and empty-context behavior.\nLIMIT: no browser binary was available, so browser visual rendering was not executed.\n';
await fs.writeFile(path.join(root,'analysis/dashboard_validation.txt'),report);
console.log(report);
