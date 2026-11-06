const assert=require('node:assert/strict');
(async()=>{
 const base='https://maha-hsc-analyzer.pages.dev',commit=process.env.GITHUB_SHA;
 const get=p=>fetch(base+p,{redirect:'manual',headers:{'User-Agent':'Mozilla/5.0'},signal:AbortSignal.timeout(15000)});
 let current;
 for(let i=0;i<12;i++){
  try{const r=await get('/version.json');if(r.ok){current=await r.json();if(!commit||current.commit===commit)break}}catch{}
  await new Promise(resolve=>setTimeout(resolve,5000));
 }
 assert.ok(current?.version,'No published version metadata');
 if(commit)assert.equal(current.commit,commit,'Published revision has not updated');
 const login=await get('/login');assert.equal(login.status,200);assert.match(await login.text(),/Continue with Google/);
 const data=await get('/data/papers.json');assert.ok([401,503].includes(data.status),'Anonymous JSON was not blocked');
 const pdf=await get('/sources/papers/b553884a3537e6d8.pdf');assert.ok([303,503].includes(pdf.status),'Anonymous PDF was not blocked');
 console.log('Deployment verified:',current.version,'— login available; anonymous PDF/JSON blocked');
})().catch(error=>{console.error(error.message);process.exit(1)});
