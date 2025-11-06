#!/usr/bin/env python3
# binary-safe scan for PEM/EVP markers
import os, sys
PATS=[b'EVP_DigestVerifyFinal', b'-----BEGIN PUBLIC KEY-----', b'Data.db', b'sqlite3']
root=sys.argv[1] if len(sys.argv)>1 else '.'
for dp,_,fs in os.walk(root):
for fn in fs:
p=os.path.join(dp,fn)
try:
with open(p,'rb') as f: b=f.read(2*1024*1024)
except: continue
for pat in PATS:
if pat in b:
print(p,'->',pat.decode('ascii','ignore'))
break
