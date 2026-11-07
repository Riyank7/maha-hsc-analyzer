// Plaintext drafts and credentials remain in ignored private/. Only ciphertext is published.
import {readFile,writeFile,mkdir,readdir,chmod} from 'node:fs/promises';
import {randomBytes,createCipheriv,pbkdf2Sync} from 'node:crypto';
import {resolve} from 'node:path';

const root = resolve(import.meta.dirname,'..');
const privateDir = resolve(root,'private');
await mkdir(resolve(privateDir,'answers'),{recursive:true});
await chmod(privateDir,0o700);
let secrets;
try {secrets=JSON.parse(await readFile(resolve(privateDir,'answers-secrets.json'),'utf8'));}
catch(error) {
  if (error.code !== 'ENOENT') throw error;
  const password = randomBytes(24).toString('base64url');
  const salt = randomBytes(16);
  secrets={ANSWERS_VAULT_KEY:randomBytes(32).toString('base64url'),ANSWERS_PASSWORD_VERIFIER:`pbkdf2-sha256:100000:${salt.toString('base64url')}:${pbkdf2Sync(password,salt,100000,32,'sha256').toString('base64url')}`};
  await writeFile(resolve(privateDir,'answers-secrets.json'),JSON.stringify(secrets),{mode:0o600});
  await writeFile(resolve(privateDir,'answers-access.txt'),`Maharashtra HSC Answers\nWebsite: https://maha-hsc-analyzer.pages.dev\nSign in with Google, then open Answers.\nShared password: ${password}\n\nKeep this file private. The password is not committed to GitHub.\n`,{mode:0o600});
}
const dest = resolve(root,'vault');
await mkdir(dest,{recursive:true});
const key=Buffer.from(secrets.ANSWERS_VAULT_KEY,'base64url');
const files=(await readdir(resolve(privateDir,'answers'))).filter(x=>/^(index|[a-f0-9]{12})\.(json|pdf)$/.test(x));
if (!files.includes('index.json')) throw Error('Missing answer index');
for (const file of files) {
  const plain=await readFile(resolve(privateDir,'answers',file));
  const iv=randomBytes(12),cipher=createCipheriv('aes-256-gcm',key,iv);
  cipher.setAAD(Buffer.from('hsc-answers-v1:'+file));
  const ciphertext=Buffer.concat([iv,cipher.update(plain),cipher.final(),cipher.getAuthTag()]);
  await writeFile(resolve(dest,file+'.enc'),ciphertext);
}
console.log(`Encrypted ${files.length} answer files. No password or plaintext was printed.`);
