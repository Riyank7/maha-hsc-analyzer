import { SignJWT, jwtVerify, createRemoteJWKSet, base64url } from 'jose';

const googleKeys = createRemoteJWKSet(new URL('https://www.googleapis.com/oauth2/v3/certs'));
const encoder = new TextEncoder();
const SESSION_SECONDS = 8 * 60 * 60;
const STATE_SECONDS = 10 * 60;
const PUBLIC_PATHS = new Set(['/login', '/login.html', '/auth.css', '/login.js', '/favicon.ico', '/version.json']);

export function configuration(env) {
  const origin = new URL(env.APP_ORIGIN || '');
  const local = ['localhost', '127.0.0.1', '[::1]'].includes(origin.hostname);
  if ((!local && origin.protocol !== 'https:') || !['http:', 'https:'].includes(origin.protocol) || origin.username || origin.password || origin.pathname !== '/' || origin.search || origin.hash) throw Error('Invalid app origin');
  if (!env.GOOGLE_CLIENT_ID?.endsWith('.apps.googleusercontent.com') || !env.GOOGLE_CLIENT_SECRET || (env.SESSION_SECRET || '').length < 32) throw Error('Missing sign-in configuration');
  return { origin: origin.origin, secure: origin.protocol === 'https:', clientId: env.GOOGLE_CLIENT_ID, clientSecret: env.GOOGLE_CLIENT_SECRET, key: encoder.encode(env.SESSION_SECRET) };
}
export function safeNext(value, origin) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//') || /[\\\u0000-\u0020\u007f]/.test(value)) return '/';
  try { const url = new URL(value, origin); return url.origin === origin && !url.pathname.startsWith('/auth/') && !url.pathname.startsWith('/login') ? url.pathname + url.search + url.hash : '/'; } catch { return '/'; }
}
function name(cfg, kind) { return (cfg.secure ? '__Host-' : '') + 'hsc_' + kind; }
function cookie(cfg, kind, value, seconds) { return `${name(cfg, kind)}=${value}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${seconds}${cfg.secure ? '; Secure' : ''}`; }
function cookies(request) {
  const result = new Map();
  for (const part of (request.headers.get('Cookie') || '').split(';')) { const i = part.indexOf('='); if (i > 0) result.set(part.slice(0, i).trim(), part.slice(i + 1).trim()); }
  return result;
}
function random() { return base64url.encode(crypto.getRandomValues(new Uint8Array(32))); }
async function sign(cfg, audience, payload, seconds) {
  return new SignJWT(payload).setProtectedHeader({ alg: 'HS256', typ: 'JWT' }).setIssuer(cfg.origin).setAudience(audience).setIssuedAt().setExpirationTime(Math.floor(Date.now() / 1000) + seconds).sign(cfg.key);
}
async function verify(cfg, audience, token) {
  if (!token || token.length > 6000) throw Error('Missing token');
  return (await jwtVerify(token, cfg.key, { algorithms: ['HS256'], issuer: cfg.origin, audience, requiredClaims: ['iat', 'exp'], maxTokenAge: audience === 'hsc-session' ? SESSION_SECONDS : STATE_SECONDS })).payload;
}
export async function readSession(request, cfg) {
  try { const payload = await verify(cfg, 'hsc-session', cookies(request).get(name(cfg, 'session'))); if (!payload.sub || !payload.email || payload.emailVerified !== true) return null; return { sub: payload.sub, email: payload.email, name: payload.name || payload.email }; } catch { return null; }
}
export async function validateGoogleToken(token, cfg, nonce, keys = googleKeys) {
  const { payload } = await jwtVerify(token, keys, { algorithms: ['RS256'], issuer: ['https://accounts.google.com', 'accounts.google.com'], audience: cfg.clientId, requiredClaims: ['exp', 'iat', 'sub', 'nonce'], clockTolerance: 5, maxTokenAge: 10 * 60 });
  if (payload.nonce !== nonce || payload.email_verified !== true || typeof payload.email !== 'string' || !payload.email || typeof payload.sub !== 'string' || (payload.azp && payload.azp !== cfg.clientId)) throw Error('Invalid Google identity');
  return { sub: payload.sub, email: payload.email.slice(0, 320), name: typeof payload.name === 'string' ? payload.name.slice(0, 150) : payload.email.slice(0, 150) };
}
function privateResponse(response) {
  const out = new Response(response.body, response);
  out.headers.set('Cache-Control', 'private, no-store');
  out.headers.set('Vary', 'Cookie');
  out.headers.set('X-Content-Type-Options', 'nosniff');
  out.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  return out;
}
function json(data, status = 200, headers = {}) { return privateResponse(Response.json(data, { status, headers })); }
function redirect(location, setCookies = []) {
  const headers = new Headers({ Location: location });
  for (const item of setCookies) headers.append('Set-Cookie', item);
  return privateResponse(new Response(null, { status: 303, headers }));
}
async function exchangeCode(code, verifier, cfg) {
  const response = await fetch('https://oauth2.googleapis.com/token', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams({ code, client_id: cfg.clientId, client_secret: cfg.clientSecret, redirect_uri: cfg.origin + '/auth/callback', grant_type: 'authorization_code', code_verifier: verifier }), signal: AbortSignal.timeout(10000) });
  if (!response.ok) throw Error('Google token exchange failed');
  const body = await response.json();
  if (typeof body.id_token !== 'string') throw Error('No ID token');
  return body.id_token;
}

// Dependencies are injected only by server-side tests, never through request or env data.
export function createAuthHandler({ exchange = exchangeCode, validate = validateGoogleToken } = {}) {
  return async function onRequest(context) {
    const { request, env } = context, url = new URL(request.url), pathname = url.pathname;
    if (PUBLIC_PATHS.has(pathname)) {
      if (!['GET', 'HEAD'].includes(request.method)) return json({ error: 'Method not allowed' }, 405, { Allow: 'GET, HEAD' });
      const response = await context.next();
      return privateResponse(response);
    }
    let cfg;
    try { cfg = configuration(env); if (url.origin !== cfg.origin) throw Error('Origin mismatch'); }
    catch {
      if (pathname==='/' || pathname.endsWith('.html')) return redirect('/login?next='+encodeURIComponent(safeNext(pathname+url.search,url.origin)));
      return json({ error: 'Sign-in is being set up. Please try again later.', configured: false }, 503);
    }
    if (pathname === '/auth/config' && request.method === 'GET') return json({ configured: true });
    if (pathname === '/auth/session' && request.method === 'GET') {
      const session = await readSession(request, cfg);
      return session ? json({ user: { name: session.name, email: session.email } }) : json({ error: 'Sign-in required' }, 401);
    }
    if (pathname === '/auth/login' && request.method === 'GET') {
      const state = random(), nonce = random(), verifier = random(), next = safeNext(url.searchParams.get('next'), cfg.origin);
      const challenge = base64url.encode(new Uint8Array(await crypto.subtle.digest('SHA-256', encoder.encode(verifier))));
      const signedState = await sign(cfg, 'hsc-oauth-state', { state, nonce, verifier, next }, STATE_SECONDS);
      const target = new URL('https://accounts.google.com/o/oauth2/v2/auth');
      target.search = new URLSearchParams({ client_id: cfg.clientId, redirect_uri: cfg.origin + '/auth/callback', response_type: 'code', scope: 'openid email profile', state, nonce, code_challenge: challenge, code_challenge_method: 'S256', access_type: 'online', prompt: 'select_account' }).toString();
      return redirect(target.href, [cookie(cfg, 'oauth', signedState, STATE_SECONDS)]);
    }
    if (pathname === '/auth/callback' && request.method === 'GET') {
      const clearState = cookie(cfg, 'oauth', '', 0);
      try {
        const pending = await verify(cfg, 'hsc-oauth-state', cookies(request).get(name(cfg, 'oauth')));
        if (typeof pending.state !== 'string' || pending.state !== url.searchParams.get('state') || typeof pending.nonce !== 'string' || typeof pending.verifier !== 'string' || url.searchParams.has('error')) throw Error('Invalid OAuth state');
        const code = url.searchParams.get('code'); if (!code || code.length > 4096) throw Error('Missing code');
        const token = await exchange(code, pending.verifier, cfg);
        const user = await validate(token, cfg, pending.nonce);
        const session = await sign(cfg, 'hsc-session', { sub: user.sub, email: user.email, name: user.name, emailVerified: true }, SESSION_SECONDS);
        return redirect(safeNext(pending.next, cfg.origin), [clearState, cookie(cfg, 'session', session, SESSION_SECONDS)]);
      } catch {
        // Do not log authorization codes, ID tokens, or provider error responses.
        return redirect('/login?error=sign-in', [clearState]);
      }
    }
    if (pathname === '/auth/logout' && request.method === 'POST') {
      if (request.headers.get('Origin') !== cfg.origin) return json({ error: 'Invalid request origin' }, 403);
      return redirect('/login', [cookie(cfg, 'session', '', 0), cookie(cfg, 'oauth', '', 0)]);
    }
    if (pathname.startsWith('/auth/')) return json({ error: 'Not found' }, 404);
    const session = await readSession(request, cfg);
    if (!session) {
      if (pathname.startsWith('/data/') || request.headers.get('Accept')?.includes('application/json')) return json({ error: 'Sign-in required' }, 401);
      return redirect('/login?next=' + encodeURIComponent(safeNext(pathname + url.search, cfg.origin)));
    }
    return privateResponse(await context.next());
  };
}
export const onRequest = createAuthHandler();
