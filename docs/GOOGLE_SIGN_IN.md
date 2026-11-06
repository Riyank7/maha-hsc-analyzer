# Activate required Google sign-in

This pull request gates the analyzer, data, report, and every PDF at the Cloudflare Pages edge. Every Google account with a verified email can sign in; no email allowlist is configured. The public GitHub repository still contains the public examination PDFs. Website login does not make those repository files private.

The feature is intentionally a separate PR. It is not merged or active on the base production deployment until configured, reviewed, merged, and deployed.

## Google setup (one-time)

1. Create or select your personal project in [Google Cloud Console](https://console.cloud.google.com/).
2. Open Google Auth Platform. Configure branding, audience (External for shareable access), and your support/contact email. Request only `openid`, `email`, and `profile`. Add test users while the consent screen is in Testing; publish the audience when you are ready to allow other Google accounts.
3. Create an OAuth client of type **Web application**. Add this exact authorized redirect URI:

   `https://maha-hsc-analyzer.pages.dev/auth/callback`

   For local testing also add `http://localhost:8788/auth/callback`. This server redirect flow does not require JavaScript origins or Google API scopes for Gmail/Drive.
4. Save the client ID and client secret. Add secrets directly to Cloudflare; do not commit them or paste them into a PR.

Primary references: [Google OpenID Connect server flow](https://developers.google.com/identity/openid-connect/openid-connect), [Google ID-token verification](https://developers.google.com/identity/gsi/web/guides/verify-google-id-token), [Cloudflare Pages secrets](https://developers.cloudflare.com/pages/functions/bindings/).

## Cloudflare configuration

Set the following for the production Pages environment:

| Name | Value / handling |
| --- | --- |
| `APP_ORIGIN` | `https://maha-hsc-analyzer.pages.dev` — exact origin, no path |
| `GOOGLE_CLIENT_ID` | Your Web application client ID ending in `.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Encrypted Cloudflare secret from Google |
| `SESSION_SECRET` | Encrypted Cloudflare secret, randomly generated with at least 32 bytes of entropy (for example, `openssl rand -base64 32`) |

Use Cloudflare Dashboard → Workers & Pages → maha-hsc-analyzer → Settings → Variables and Secrets, or Wrangler's interactive `pages secret put` command for each name. Do not store secret values in `wrangler.jsonc` or GitHub.

Missing settings fail closed: the login screen remains available, while protected data and PDFs return 503. They are never served anonymously as a fallback. A changed host or a custom domain requires updating `APP_ORIGIN` and adding the corresponding Google redirect URI.

For a preview deployment, set all four bindings for that environment and authorize its exact stable preview hostname in Google. Unconfigured preview environments also fail closed. Do not point a preview's `APP_ORIGIN` at production.

## Local development

Requires Node 22+ and Python 3. Install with `npm ci`. Copy `.dev.vars.example` to `.dev.vars` and replace placeholders privately. Then run `npm run dev` and visit `http://localhost:8788/login`. A plain Python static server cannot enforce authentication and is only suitable for inspecting the original static assets.

`.dev.vars` and `.env` files are ignored by Git. The example contains no working credentials. Local HTTP cookies are allowed only for loopback hosts; production requires HTTPS and uses `__Host-` cookies.

## Validation and release

- `npm test`: signed/expired/tampered sessions; issuer/audience checks; PDF/JSON protection; missing config; state/PKCE/nonce; Google signature and verified-email checks; safe redirects; same-origin logout; private caching.
- `npm run build` packages the site and active PDFs. Wrangler bundles `functions/_middleware.js` from the project root.
- `npx wrangler pages functions build functions --outfile /tmp/hsc-auth-worker.js` checks the Workers bundle.
- After configuring Google, test a real login, sign out, try a direct PDF while signed out, and test the return to that PDF after login. The automated provider tests use locally signed JWTs and a mocked code exchange; they do not prove live Google credentials work.
- Merge the PR only when ready, then run `npm run deploy -- --branch main` (or `npm run build` followed by `npx wrangler pages deploy dist --project-name maha-hsc-analyzer --branch main`). A Git push alone does not deploy this Direct Upload project.

Sessions last eight hours. Only the user's Google subject, verified email, and display name are stored inside an HttpOnly signed cookie. No Google access or refresh token is retained. Sign out clears the browser session; rotating `SESSION_SECRET` invalidates all existing sessions. There is no account database, tracking, or server-side session revocation store.

## Implementation

Google authorization-code flow uses PKCE (S256), a signed short-lived state cookie, and an ID-token nonce. `jose` verifies Google RS256 signatures against Google's rotating JWKS, issuer, audience, expiry, authorized party (when present), nonce, and verified email. The app creates its own issuer/audience-bound HMAC session. Logout requires a same-origin POST. Protected responses use `Cache-Control: private, no-store` and `Vary: Cookie`; `_routes.json` deliberately includes every path, including static PDFs and JSON.
