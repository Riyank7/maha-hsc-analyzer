# Answer library

Production uses required Google sign-in plus a separate shared Answers password.
The high-entropy password is generated locally by scripts/seal_answers.mjs and
written only to ignored private/answers-access.txt with mode 0600. Never commit
or publish that file.

## Storage and release

1. Keep original worked answer JSON in private/answers/<paper-id>.json. Review
   every question and alternative against the PDF. Label missing source data
   and ambiguous questions. A topic guide is not a complete paper answer set.
2. Published solutions are attributed links, not official marking schemes. Do
   not copy publisher answer prose into the repository. Question numbers link
   directly to the corresponding published answer.
3. Run python3 scripts/assemble_answer_catalog.py for the private catalog with
   explicit coverage statuses. Then run node scripts/seal_answers.mjs.
4. Only encrypted vault/*.enc files are copied by the normal build. Local
   secrets remain in private/answers-secrets.json, mode 0600.
5. Store ANSWERS_VAULT_KEY and ANSWERS_PASSWORD_VERIFIER as Cloudflare production
   secrets, supplementing the four Google/session bindings. GitHub Actions
   needs neither the plaintext password nor the vault key.
6. Run npm test, corpus validation and a build, commit ciphertext, then push to
   main. Existing Actions deploys the update.

Encryption uses a 12-byte random IV followed by AES-256-GCM ciphertext and tag.
The exact plaintext filename is authenticated as additional data: substituting
another encrypted file fails authentication. Back up the private credentials
securely; the public repository cannot decrypt the drafts.

## Access behavior

All /api/answers requests first require the existing Google session. Unlock is
a same-origin JSON POST using PBKDF2-SHA256 (16-byte salt, 100,000 iterations).
The generated password contains 192 random bits. Five failed attempts per minute
are throttled per user per edge isolate. This is best-effort throttling, not a
globally coordinated rate limiter.

Unlock sets a signed, Secure, HttpOnly, SameSite=Strict two-hour cookie tied to
the Google subject and password verifier. Rotating the verifier invalidates old
unlock cookies. The password is not stored in web storage. Lock clears rendered
content and the cookie; Google sign-out clears the unlock cookie too. Protected
responses are private/no-store.

Direct /vault requests are blocked even after unlock. Authorized endpoints read
encrypted assets through the internal Pages ASSETS binding and decrypt them at
the edge. Test anonymous access, wrong passwords, valid unlock, another user,
expiration, lock, sign-out and direct paths before authentication changes.

Public publisher sites remain public. The password protects this site's answer
catalog, original answers and downloads; external source pages retain their
own access rules.
