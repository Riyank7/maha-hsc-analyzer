(async()=>{
  const target=document.querySelector('#account');
  try{
    const response=await fetch('/auth/session',{cache:'no-store'});
    if(!response.ok){location.replace('/login?next='+encodeURIComponent(location.pathname+location.search));return;}
    const {user}=await response.json();
    const label=document.createElement('span');label.textContent=user.name;label.title=user.email;
    const form=document.createElement('form');form.method='post';form.action='/auth/logout';
    const button=document.createElement('button');button.type='submit';button.textContent='Sign out';form.append(button);target.replaceChildren(label,form);
  }catch{target.textContent='Unable to check your sign-in. Reload to try again.';}
})();
