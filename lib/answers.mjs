import { SignJWT, jwtVerify, base64url } from 'jose';

const utf8 = new TextEncoder();
const HOURS = 2 * 60 * 60;
const attempts = new Map();
const b64 = value => base64url.decode(value);
const cookieName = cfg => (cfg.secure ? '__Host-' : '') + 'hsc_answers';
const cookie = (cfg, token, age) => `${cookieName(cfg)}=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${age}${cfg.secure ? '; Secure' : ''}`;
const json = (body, status = 200, headers = {}) => Response.json(body, {status, headers});

export async function passwordVerifier(password, salt, iterations = 100000) {
  const material = await crypto.subtle.importKey('raw', utf8.encode(password), 'PBKDF2', false, ['deriveBits']);
  return new Uint8Array(await crypto.subtle.deriveBits({name:'PBKDF2', hash:'SHA-256', salt:b64(salt), iterations}, material, 256));
}
export function answersConfiguration(env) {
  const [scheme, rounds, salt, hash] = (env.ANSWERS_PASSWORD_VERIFIER || '').split(':');
  const key = b64(env.ANSWERS_VAULT_KEY || '');
  if (scheme !== 'pbkdf2-sha256' || rounds !== '100000' || b64(salt || '').length !== 16 || b64(hash || '').length !== 32 || key.length !== 32) throw Error('Answers unavailable');
  return {salt, hash, key, version:hash, iterations:Number(rounds)};
}
async function unlocked(request, cfg, vault, user) {
  try {
    const token = (request.headers.get('Cookie') || '').split(';').map(x=>x.trim()).find(x=>x.startsWith(cookieName(cfg)+'='))?.slice(cookieName(cfg).length + 1);
    const {payload} = await jwtVerify(token, cfg.key, {algorithms:['HS256'], issuer:cfg.origin, audience:'hsc-answers', requiredClaims:['exp','iat','sub'], maxTokenAge:HOURS});
    return payload.sub === user.sub && payload.vault === vault.version;
  } catch { return false; }
}
export async function decryptVault(bytes, keyBytes, file) {
  if (bytes.byteLength < 29) throw Error('Invalid encrypted answer');
  const key = await crypto.subtle.importKey('raw', keyBytes, 'AES-GCM', false, ['decrypt']);
  return crypto.subtle.decrypt({name:'AES-GCM', iv:bytes.slice(0,12), additionalData:utf8.encode('hsc-answers-v1:'+file)}, key, bytes.slice(12));
}

// Called only after the main middleware has verified Google sign-in.
export async function handleAnswers(context, cfg, user) {
  const {request, env} = context;
  const path = new URL(request.url).pathname;
  let vault;
  try { vault = answersConfiguration(env); }
  catch { return json({error:'The answer library is being configured.', configured:false}, 503); }
  const open = await unlocked(request, cfg, vault, user);
  if (path === '/api/answers/status' && request.method === 'GET') return json({configured:true, unlocked:open});
  if (path === '/api/answers/unlock' || path === '/api/answers/lock') {
    if (request.method !== 'POST') return json({error:'Method not allowed'}, 405, {Allow:'POST'});
    if (request.headers.get('Origin') !== cfg.origin) return json({error:'Invalid request origin'}, 403);
    if (path.endsWith('/lock')) return json({unlocked:false},200,{'Set-Cookie':cookie(cfg,'',0)});
    if (!request.headers.get('Content-Type')?.startsWith('application/json')) return json({error:'JSON required'},415);
    const now = Date.now();
    // Best-effort per-isolate throttling supplements a high-entropy shared password.
    for (const [id, value] of attempts) if (value.until < now) attempts.delete(id);
    const attempt = attempts.get(user.sub) || {count:0, until:now+60000};
    if (attempt.count >= 5) return json({error:'Too many attempts. Wait a minute and try again.'},429,{'Retry-After':'60'});
    if (attempts.size > 10000) return json({error:'Please try again shortly.'},429,{'Retry-After':'60'});
    const raw = await request.text();
    if (raw.length > 2048) return json({error:'Request too large'},413);
    let password;
    try { password = JSON.parse(raw).password; } catch { return json({error:'Invalid request'},400); }
    if (typeof password !== 'string' || password.length > 200) return json({error:'Invalid password'},400);
    const actual = await passwordVerifier(password, vault.salt, vault.iterations);
    const expected = b64(vault.hash);
    let mismatch = 0;
    for (let i=0;i<expected.length;i++) mismatch |= actual[i] ^ expected[i];
    if (mismatch) { attempt.count++; attempts.set(user.sub,attempt); return json({error:'Incorrect password.'},403); }
    attempts.delete(user.sub);
    const token = await new SignJWT({vault:vault.version}).setProtectedHeader({alg:'HS256',typ:'JWT'}).setSubject(user.sub).setIssuer(cfg.origin).setAudience('hsc-answers').setIssuedAt().setExpirationTime(Math.floor(now/1000)+HOURS).sign(cfg.key);
    return json({unlocked:true},200,{'Set-Cookie':cookie(cfg,token,HOURS)});
  }
  if (!open) return json({error:'Unlock Answers with the shared password.', locked:true},403);
  if (!['GET','HEAD'].includes(request.method)) return json({error:'Method not allowed'},405,{Allow:'GET, HEAD'});
  const match = path.match(/^\/api\/answers\/(index|[a-f0-9]{12})(?:\.(json|pdf))?$/);
  if (!match) return json({error:'Not found'},404);
  const file = match[1] + (match[2] === 'pdf' ? '.pdf' : '.json');
  try {
    const response = await env.ASSETS.fetch(new Request(cfg.origin+'/vault/'+file+'.enc'));
    if (!response.ok) return json({error:'Answer set not found'},404);
    const plain = await decryptVault(new Uint8Array(await response.arrayBuffer()),vault.key,file);
    return new Response(request.method==='HEAD'?null:plain,{headers:{'Content-Type':file.endsWith('.pdf')?'application/pdf':'application/json; charset=utf-8','Content-Disposition':`${file.endsWith('.pdf')?'inline':'inline'}; filename="${file}"`}});
  } catch { return json({error:'This answer set could not be loaded.'},503); }
}

export const clearAnswersCookie = cfg => cookie(cfg,'',0);
