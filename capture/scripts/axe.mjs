import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs';
import fs from 'fs';
const axe=fs.readFileSync('/tmp/claude-0/-home-claude/ba82769c-2614-56c5-a373-51e20a4e55b0/scratchpad/axe/node_modules/axe-core/axe.min.js','utf8');
const urls=['/','/about/','/contact/','/portfolio/','/blog/','/design-and-build/','/clinical-veterinary-fit-outs/','/locations/canterbury/','/project/vet-shack/','/sector/veterinary-fit-outs/','/testimonial/national-trust/','/the-core-principles-of-a-passive-house/'];
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});const all={};
for(const u of urls){await p.goto('https://timdayconstruction.co.uk'+u,{waitUntil:'networkidle'});await p.waitForTimeout(3500);
 await p.addScriptTag({content:axe});const r=await p.evaluate(async()=>(await axe.run(document,{runOnly:['wcag2a','wcag2aa','best-practice']})).violations.map(v=>({id:v.id,impact:v.impact,n:v.nodes.length,help:v.help})));all[u]=r;}
fs.writeFileSync('capture/axe.json',JSON.stringify(all,null,1));
const agg={};for(const [u,vs] of Object.entries(all))for(const v of vs){agg[v.id]??={impact:v.impact,help:v.help,pages:0,nodes:0};agg[v.id].pages++;agg[v.id].nodes+=v.n;}
console.log(Object.entries(agg).sort((a,b)=>b[1].nodes-a[1].nodes).map(([k,v])=>`${k} [${v.impact}] pages:${v.pages} nodes:${v.nodes} – ${v.help}`).join('\n'));await b.close();
