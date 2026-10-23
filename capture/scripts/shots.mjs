import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs';
import fs from 'fs';
const B='https://timdayconstruction.co.uk';
const pages={home:'/',about:'/about/',contact:'/contact/',portfolio:'/portfolio/',blog:'/blog/','design-and-build':'/design-and-build/',
 service:'/clinical-veterinary-fit-outs/',location:'/locations/canterbury/',project:'/project/vet-shack/',sector:'/sector/veterinary-fit-outs/',
 testimonial:'/testimonial/national-trust/',post:'/the-core-principles-of-a-passive-house/',category:'/category/extensions/'};
const browser=await chromium.launch();
for (const [w,h] of [[1440,900],[390,844]]) {
  const ctx=await browser.newContext({viewport:{width:w,height:h},deviceScaleFactor:1,userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130 Safari/537.36'});
  for (const [name,path] of Object.entries(pages)) {
    const p=await ctx.newPage();
    await p.goto(B+path,{waitUntil:'networkidle',timeout:90000});
    await p.waitForTimeout(3500); // entrance animation
    // scroll through to trigger AOS + lazysizes
    await p.evaluate(async()=>{const s=ms=>new Promise(r=>setTimeout(r,ms));for(let y=0;y<document.body.scrollHeight;y+=400){window.scrollTo(0,y);await s(120);}window.scrollTo(0,0);});
    await p.evaluate(()=>{document.querySelectorAll('img').forEach(i=>{i.loading='eager';if(i.dataset.src)i.src=i.dataset.src;if(i.dataset.srcset)i.srcset=i.dataset.srcset;});
      document.querySelectorAll('[data-aos]').forEach(e=>e.classList.add('aos-animate'));});
    await p.waitForLoadState('networkidle');
    await p.evaluate(async()=>{await Promise.all([...document.images].map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r;})));});
    await p.waitForTimeout(800);
    await p.screenshot({path:`capture/screenshots/${name}-${w}.png`,fullPage:true});
    if (w===1440 || name==='home') {
      const data=await p.evaluate(()=>{
        const props=['color','backgroundColor','borderTopColor','fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','textTransform','paddingTop','paddingBottom','paddingLeft','paddingRight','marginBottom','borderRadius','maxWidth','gap','boxShadow'];
        const out=[];
        const sel=e=>e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+(typeof e.className==='string'&&e.className.trim()?'.'+e.className.trim().split(/\s+/).join('.'):'');
        document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(!r.width||!r.height)return;const cs=getComputedStyle(e);
          const o={sel:sel(e),path:(e.parentElement?sel(e.parentElement)+' > ':'')+sel(e),w:Math.round(r.width),h:Math.round(r.height),text:(e.childNodes[0]&&e.childNodes[0].nodeType===3?e.childNodes[0].textContent.trim().slice(0,40):'')};
          props.forEach(k=>o[k]=cs[k]);out.push(o);});
        return out;});
      fs.writeFileSync(`capture/computed/${name}-${w}.json`,JSON.stringify(data));
    }
    console.log(name,w); await p.close();
  }
  await ctx.close();
}
await browser.close();
