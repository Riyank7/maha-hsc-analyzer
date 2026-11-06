import test from 'node:test';
import assert from 'node:assert/strict';
import { SignJWT, generateKeyPair, exportJWK, createLocalJWKSet } from 'jose';
import { createAuthHandler, configuration, safeNext, validateGoogleToken } from '../lib/auth.mjs';

const origin='https://hsc.example.test';
const env={APP_ORIGIN:origin,GOOGLE_CLIENT_ID:'test.apps.googleusercontent.com',GOOGLE_CLIENT_SECRET:'test-only-secret',SESSION_SECRET:'test-only-session-secret-with-at-least-32-characters'};
function context(path='/',options={},bindings=env){
 let served=0;
 return {request:new Request(origin+path,options),env:{...bindings,ASSETS:{fetch:async()=>new Response('<h1>Sign in</h1>')}},next:async()=>{served++;return new Response('private paper',{headers:{'Cache-Control':'public, max-age=86400'}})},get served(){return served}};
}
const cookiePair=(response,kind)=>response.headers.getSetCookie().find(c=>c.startsWith('__Host-hsc_'+kind+'=')).split(';')[0];
async function start(handler=createAuthHandler()){
 const response=await handler(context('/auth/login?next=%2Fsources%2Fpapers%2Ftest.pdf'));
 return {cookie:cookiePair(response,'oauth'),state:new URL(response.headers.get('Location')).searchParams.get('state'),response};
}
async function sessionToken(claims={},options={}){
 return new SignJWT({email:'student@example.com',emailVerified:true,name:'Student',...claims}).setProtectedHeader({alg:'HS256'}).setSubject('google-user').setIssuer(options.issuer||origin).setAudience(options.audience||'hsc-session').setIssuedAt().setExpirationTime(options.exp||'1h').sign(new TextEncoder().encode(env.SESSION_SECRET));
}
for(const path of ['/', '/sources/papers/test.pdf','/reports/analysis.html'])test('unauthenticated access blocked: '+path,async()=>{
 const c=context(path),r=await createAuthHandler()(c);assert.equal(r.status,303);assert.match(r.headers.get('Location'),/^\/login\?next=/);assert.equal(c.served,0);assert.match(r.headers.get('Cache-Control'),/no-store/);
});
test('raw JSON cannot bypass authentication',async()=>{const c=context('/data/questions.json');const r=await createAuthHandler()(c);assert.equal(r.status,401);assert.equal(c.served,0)});
test('missing OAuth settings fail closed for PDFs',async()=>{const c=context('/sources/papers/test.pdf',{},{});const r=await createAuthHandler()(c);assert.equal(r.status,503);assert.equal(c.served,0)});
test('login screen remains public without OAuth settings',async()=>{const c=context('/login',{},{});c.next=async()=>new Response('<h1>Sign in</h1>');const r=await createAuthHandler()(c);assert.equal(r.status,200);assert.match(await r.text(),/Sign in/)});
test('valid signed session serves a PDF without public caching',async()=>{const token=await sessionToken();const c=context('/sources/papers/test.pdf',{headers:{Cookie:'__Host-hsc_session='+token}});const r=await createAuthHandler()(c);assert.equal(r.status,200);assert.equal(c.served,1);assert.equal(r.headers.get('Cache-Control'),'private, no-store');assert.equal(r.headers.get('Vary'),'Cookie')});
for(const [name,tokenFn] of [['tampered',async()=>{const t=await sessionToken();return t.slice(0,-4)+'abcd'}],['expired',()=>sessionToken({}, {exp:Math.floor(Date.now()/1000)-1})],['wrong audience',()=>sessionToken({}, {audience:'hsc-oauth-state'})],['wrong issuer',()=>sessionToken({}, {issuer:'https://attacker.test'})],['unverified email',()=>sessionToken({emailVerified:false})]])test('rejects '+name+' session',async()=>{const token=await tokenFn();const r=await createAuthHandler()(context('/data/papers.json',{headers:{Cookie:'__Host-hsc_session='+token}}));assert.equal(r.status,401)});
test('OAuth request has state, nonce, PKCE and a secure temporary cookie',async()=>{
 const {response}=await start();const url=new URL(response.headers.get('Location'));
 assert.equal(url.origin,'https://accounts.google.com');assert.equal(url.searchParams.get('scope'),'openid email profile');assert.equal(url.searchParams.get('code_challenge_method'),'S256');assert.equal(url.searchParams.get('redirect_uri'),origin+'/auth/callback');assert.ok(url.searchParams.get('state'));assert.ok(url.searchParams.get('nonce'));assert.match(url.searchParams.get('code_challenge'),/^[A-Za-z0-9_-]{43}$/);
 const c=response.headers.get('Set-Cookie');for(const flag of ['__Host-hsc_oauth=','HttpOnly','Secure','SameSite=Lax','Path=/'])assert.ok(c.includes(flag));assert.equal(url.searchParams.get('access_type'),'online');
});
test('callback rejects forged state before contacting Google',async()=>{let exchanges=0;const handler=createAuthHandler({exchange:async()=>{exchanges++;return 'token'}});const a=await start(handler);const r=await handler(context('/auth/callback?state=wrong&code=code',{headers:{Cookie:a.cookie}}));assert.equal(exchanges,0);assert.equal(r.headers.get('Location'),'/login?error=sign-in');assert.match(r.headers.get('Set-Cookie'),/Max-Age=0/)});
test('successful callback creates a session and returns to the original PDF',async()=>{
 let expectedNonce;const handler=createAuthHandler({exchange:async(code,verifier)=>{assert.equal(code,'test-code');assert.ok(verifier.length>=43);return 'verified-by-test'},validate:async(token,cfg,nonce)=>{assert.equal(token,'verified-by-test');expectedNonce=nonce;return {sub:'g-user',email:'student@example.com',name:'Student'}}});
 const a=await start(handler);const r=await handler(context('/auth/callback?state='+a.state+'&code=test-code',{headers:{Cookie:a.cookie}}));assert.ok(expectedNonce);assert.equal(r.status,303);assert.equal(r.headers.get('Location'),'/sources/papers/test.pdf');const session=cookiePair(r,'session');const status=await handler(context('/auth/session',{headers:{Cookie:session}}));assert.equal(status.status,200);assert.deepEqual((await status.json()).user,{name:'Student',email:'student@example.com'});
});
test('Google exchange failure does not create a session',async()=>{const handler=createAuthHandler({exchange:async()=>{throw Error('provider unavailable')}});const a=await start(handler);const r=await handler(context('/auth/callback?state='+a.state+'&code=test',{headers:{Cookie:a.cookie}}));assert.equal(r.headers.get('Location'),'/login?error=sign-in');assert.ok(!r.headers.get('Set-Cookie').includes('hsc_session='))});
test('logout requires a same-origin POST and clears cookies',async()=>{const handler=createAuthHandler();assert.equal((await handler(context('/auth/logout',{method:'POST',headers:{Origin:'https://attacker.test'}}))).status,403);assert.equal((await handler(context('/auth/logout'))).status,404);const r=await handler(context('/auth/logout',{method:'POST',headers:{Origin:origin}}));assert.equal(r.status,303);assert.equal(r.headers.getSetCookie().length,2);assert.ok(r.headers.getSetCookie().every(c=>c.includes('Max-Age=0')))});
test('return paths cannot become external redirects',()=>{for(const v of ['//attacker.test','https://attacker.test','/\\attacker.test','/\r\nLocation: bad','/auth/login','/login?next=/'])assert.equal(safeNext(v,origin),'/');assert.equal(safeNext('/?tab=papers',origin),'/?tab=papers')});
test('production config rejects insecure origins, URL credentials, and short secrets',()=>{for(const patch of [{APP_ORIGIN:'http://hsc.example.test'},{APP_ORIGIN:'https://user:pass@hsc.example.test'},{SESSION_SECRET:'short'}])assert.throws(()=>configuration({...env,...patch}));assert.equal(configuration({...env,APP_ORIGIN:'http://localhost:8788'}).secure,false)});

test('Google identity verification checks signature, issuer, audience, nonce and verified email',async()=>{
 const {privateKey,publicKey}=await generateKeyPair('RS256');const key=await exportJWK(publicKey);key.kid='test-key';key.alg='RS256';const keys=createLocalJWKSet({keys:[key]});const cfg=configuration(env);
 async function googleToken(claims={},aud=env.GOOGLE_CLIENT_ID,iss='https://accounts.google.com') {return new SignJWT({nonce:'test-nonce',email:'student@example.com',email_verified:true,name:'Student',...claims}).setProtectedHeader({alg:'RS256',kid:'test-key'}).setSubject('google-user').setIssuer(iss).setAudience(aud).setIssuedAt().setExpirationTime('5m').sign(privateKey)}
 assert.equal((await validateGoogleToken(await googleToken(),cfg,'test-nonce',keys)).sub,'google-user');
 for(const [claims,aud,iss] of [[{nonce:'wrong'}],[{email_verified:false}],[{},'attacker-client'],[{},undefined,'https://attacker.test'],[{azp:'attacker-client'}]])await assert.rejects(()=>googleToken(claims,aud,iss).then(t=>validateGoogleToken(t,cfg,'test-nonce',keys)));
 const {privateKey:other}=await generateKeyPair('RS256');const forged=await new SignJWT({nonce:'test-nonce',email:'student@example.com',email_verified:true}).setProtectedHeader({alg:'RS256',kid:'test-key'}).setSubject('google-user').setIssuer('https://accounts.google.com').setAudience(env.GOOGLE_CLIENT_ID).setIssuedAt().setExpirationTime('5m').sign(other);await assert.rejects(()=>validateGoogleToken(forged,cfg,'test-nonce',keys));
});

test('missing OAuth settings still show a login screen at the home URL',async()=>{const c=context('/',{},{});const r=await createAuthHandler()(c);assert.equal(r.status,303);assert.match(r.headers.get('Location'),/^\/login\?next=/);assert.equal(c.served,0)});
test('deployment version is public without OAuth settings',async()=>{const c=context('/version.json',{},{});c.next=async()=>Response.json({version:'release-1'});const r=await createAuthHandler()(c);assert.equal(r.status,200);assert.equal((await r.json()).version,'release-1');assert.equal(r.headers.get('Cache-Control'),'private, no-store')});

test('public privacy notice remains available without sign-in',async()=>{const c=context('/privacy',{},{});c.next=async()=>new Response('Privacy and sign-in');const r=await createAuthHandler()(c);assert.equal(r.status,200);assert.match(await r.text(),/Privacy/)});
