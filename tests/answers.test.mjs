import test from 'node:test';
import assert from 'node:assert/strict';
import {SignJWT,base64url} from 'jose';
import {passwordVerifier} from '../lib/answers.mjs';
import {createAuthHandler} from '../lib/auth.mjs';
const origin='https://answers.example.test', key=crypto.getRandomValues(new Uint8Array(32)), salt=base64url.encode(crypto.getRandomValues(new Uint8Array(16)));
const password='a-test-only-long-random-password';
const hash=base64url.encode(await passwordVerifier(password,salt));
const env={APP_ORIGIN:origin,GOOGLE_CLIENT_ID:'test.apps.googleusercontent.com',GOOGLE_CLIENT_SECRET:'testing',SESSION_SECRET:'test-only-session-secret-with-at-least-32-characters',ANSWERS_PASSWORD_VERIFIER:`pbkdf2-sha256:100000:${salt}:${hash}`,ANSWERS_VAULT_KEY:base64url.encode(key)};
async function session(sub='student-1'){return '__Host-hsc_session='+await new SignJWT({email:'student@example.com',emailVerified:true}).setProtectedHeader({alg:'HS256'}).setSubject(sub).setIssuer(origin).setAudience('hsc-session').setIssuedAt().setExpirationTime('1h').sign(new TextEncoder().encode(env.SESSION_SECRET));}
async function encrypted(file='index.json'){
 const iv=crypto.getRandomValues(new Uint8Array(12)),cryptoKey=await crypto.subtle.importKey('raw',key,'AES-GCM',false,['encrypt']);
 const cipher=await crypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:new TextEncoder().encode('hsc-answers-v1:'+file)},cryptoKey,new TextEncoder().encode(JSON.stringify({secretAnswer:'test answer'})));
 return new Uint8Array([...iv,...new Uint8Array(cipher)]);
}
async function call(path,options={},bindings={}){
 let served=0;const c={request:new Request(origin+path,options),env:{...env,ASSETS:{fetch:async()=>new Response(await encrypted())},...bindings},next:async()=>{served++;return new Response('MUST NOT LEAK');}};
 const response=await createAuthHandler()(c);return {response,served};
}
test('answers need a Google session before password access',async()=>{const {response,served}=await call('/api/answers/index');assert.equal(response.status,401);assert.equal(served,0);});
test('signed-in users cannot fetch answers or ciphertext directly while locked',async()=>{
 for(const path of ['/api/answers/index','/vault/index.json.enc']){const {response,served}=await call(path,{headers:{Cookie:await session()}});assert.equal(response.status,path.startsWith('/vault')?404:403);assert.equal(served,0);assert.ok(!(await response.text()).includes('test answer'));}
});
test('missing vault configuration fails closed',async()=>{const {response}=await call('/api/answers/index',{headers:{Cookie:await session()}},{ANSWERS_VAULT_KEY:''});assert.equal(response.status,503);});
test('unlock rejects cross-origin and wrong-password requests',async()=>{
 const cookie=await session('wrong-test');for(const [supplied,source,expected] of [[password,'https://evil.test',403],['wrong',origin,403]]){const {response}=await call('/api/answers/unlock',{method:'POST',headers:{Cookie:cookie,Origin:source,'Content-Type':'application/json'},body:JSON.stringify({password:supplied})});assert.equal(response.status,expected);assert.equal(response.headers.get('Set-Cookie'),null);}
});
test('password opens encrypted data only for the same Google user, and lock clears it',async()=>{
 const google=await session();const {response:unlock}=await call('/api/answers/unlock',{method:'POST',headers:{Cookie:google,Origin:origin,'Content-Type':'application/json'},body:JSON.stringify({password})});assert.equal(unlock.status,200);
 const grant=unlock.headers.get('Set-Cookie');for(const flag of ['HttpOnly','Secure','SameSite=Strict','Max-Age=7200'])assert.ok(grant.includes(flag));
 const cookie=google+'; '+grant.split(';')[0];const {response}=await call('/api/answers/index',{headers:{Cookie:cookie}});assert.equal(response.status,200);assert.equal((await response.json()).secretAnswer,'test answer');assert.equal(response.headers.get('Cache-Control'),'private, no-store');
 const {response:other}=await call('/api/answers/index',{headers:{Cookie:await session('another-user')+'; '+grant.split(';')[0]}});assert.equal(other.status,403);
 const {response:lock}=await call('/api/answers/lock',{method:'POST',headers:{Cookie:cookie,Origin:origin}});assert.match(lock.headers.get('Set-Cookie'),/Max-Age=0/);
 const {response:tampered}=await call('/api/answers/index',{headers:{Cookie:cookie}},{ASSETS:{fetch:async()=>{const data=await encrypted();data[14]^=1;return new Response(data);}}});assert.equal(tampered.status,503);
 const {response:wrongFile}=await call('/api/answers/abcdef012345',{headers:{Cookie:cookie}});assert.equal(wrongFile.status,503);
 const {response:traversal}=await call('/api/answers/unknown',{headers:{Cookie:cookie}});assert.equal(traversal.status,404);
});
test('repeated wrong passwords are throttled per signed-in user',async()=>{
 const google=await session('rate-test');for(let i=0;i<6;i++){const {response}=await call('/api/answers/unlock',{method:'POST',headers:{Cookie:google,Origin:origin,'Content-Type':'application/json'},body:JSON.stringify({password:'wrong'})});assert.equal(response.status,i<5?403:429);}
});
