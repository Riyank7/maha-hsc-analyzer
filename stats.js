/* A joint block contributes once to a selected chapter group, only when every
   chapter in the block is included. Individual ranges are allocation bounds. */
function chapterStatistics(ps,qs){
  const paperById=new Map(ps.map(p=>[p.id,p]));
  const yearTotals=new Map();
  for(const q of qs){const y=paperById.get(q.paperId).year;yearTotals.set(y,(yearTotals.get(y)||0)+q.marks)}
  const years=yearTotals.size,rows=new Map();
  const blocks=qs.map(q=>({...q,chapters:q.chapter.startsWith('Mixed: ')?q.chapter.slice(7).split(' / '):[q.chapter],weight:q.marks/yearTotals.get(paperById.get(q.paperId).year)/years}));
  for(const q of blocks)for(const name of q.chapters){
    const r=rows.get(name)||{chapter:name,known:0,shared:0,lower:0,upper:0,years:new Set()};
    if(q.chapters.length===1){r.known+=q.marks;r.lower+=q.weight}
    else r.shared+=q.marks;
    r.upper+=q.weight;r.years.add(paperById.get(q.paperId).year);rows.set(name,r);
  }
  const ranked=[...rows.values()].sort((a,b)=>b.lower-a.lower||a.chapter.localeCompare(b.chapter));
  const selected=new Set();let covered=0;
  while(covered<=.5&&selected.size<ranked.length){
    let best=null,bestCoverage=-1;
    for(const r of ranked){if(selected.has(r.chapter))continue;const trial=new Set([...selected,r.chapter]);const score=blocks.reduce((n,q)=>n+(q.chapters.every(c=>trial.has(c))?q.weight:0),0);if(score>bestCoverage+1e-12){best=r;bestCoverage=score}}
    if(!best)break;selected.add(best.chapter);covered=bestCoverage;
  }
  return {ranked,selected:[...selected],covered,years,total:qs.reduce((n,q)=>n+q.marks,0),joint:blocks.filter(q=>q.chapters.length>1).reduce((n,q)=>n+q.marks,0)};
}
if(typeof module!=='undefined')module.exports={chapterStatistics};
