(async()=>{
  const status=document.querySelector('#loginStatus'),button=document.querySelector('#googleSignIn'),params=new URLSearchParams(location.search);
  const next=params.get('next')||'/';
  button.href='/auth/login?next='+encodeURIComponent(next);
  button.addEventListener('click',e=>{if(button.getAttribute('aria-disabled')==='true')e.preventDefault()});
  try{
    const response=await fetch('/auth/config',{cache:'no-store'});
    if(!response.ok)throw Error('unavailable');
    button.removeAttribute('aria-disabled');
    status.textContent=params.has('error')?'Sign-in could not be completed. Please try again.':'Sign in to open the papers and chapter analysis.';
  }catch{status.textContent='Sign-in is being set up. Please try again later.';}
})();

const loginVersion=document.querySelector('meta[name="app-version"]')?.content;
setInterval(async()=>{if(!loginVersion)return;try{const r=await fetch('/version.json',{cache:'no-store'});if(!r.ok)return;const v=await r.json();if(v.version&&v.version!==loginVersion)location.reload()}catch{}},15000);
