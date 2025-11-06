# Project Nebula — Redacted Case Study

## Executive Summary
Project Nebula (redacted subscription/credits platform) was assessed under explicit authorization. We combined web/API testing and client/binary analysis to understand how licenses/credits are validated and where server-side weaknesses might manifest.

### 🔍 Key Highlights
- **Edge exhibited Host header-driven behavior** on benign paths - used for fingerprinting only
- **SSTI-like indicators** on JSON endpoints (HTML error pages instead of JSON; stable length deltas)
- **Supabase backend** observed with contrasting REST/GraphQL behavior
- **Windows client** performs OpenSSL EVP signature verification with embedded public key
- **Frida proved unstable** - used x64dbg + IDA + ProcMon for verification flow mapping

## ⚖️ Legal & Ethics
- All testing conducted with written permission
- **No secrets, service keys, or vendor binaries** published
- PoCs default to `SAFE_MODE=1` and target dummy lab endpoints
- **Never run against systems you do not own or control**

## 🎯 Scope & Targets (Redacted)
- **Primary API (Edge):** JSON endpoints (`/api/v6/{check-license, insertkey, auth, users, profiles, transactions, licenses}`)
- **Secondary host:** Pivot/smuggling experiment path (excluded from public repo)
- **Supabase project:** REST vs GraphQL behavior contrasts
- **Desktop client:** Windows executable (PyInstaller/pyarmor) with Python stdlib + crypto modules

## 🚨 Key Findings — Web/API

### Host Header Behavior on Safe Path
```
Deterministic 400 with nearly fixed body length for crafted Host values
Used for edge fingerprinting only
```

### SSTI Indicators on API Endpoints
```
Specific encodings (raw → %7B%7B → %257B) returned HTML error pages instead of JSON
Consistent length deltas enabled stable diffing
Egress was blocked - only timing/error-based inference applicable
```

### Supabase Behavior
```
REST gateway: Frequently responded with stub JSON { "msg": "Hello World" }
GraphQL endpoint: Strictly rejected invalid keys with "Invalid API key"
```

### Metadata SSRF Attempts
```
Benign probes toward cloud metadata IP (169.254.169.254) blocked at edge
Returned provider-style block page
```

## 🔬 Key Findings — Client/Binary (Windows)

### Packaging & Analysis
- **Packaging:** PyInstaller + pyarmor
- **Crypto path:** Python layer → native OpenSSL via `EVP_DigestVerify*`
- **Embedded public key:** PEM markers present in binary
- **Persistence:** SQLite DB (`Data.db / Data_backup_*.db`)
- **Registry:** UI/telemetry keys under `HKCU\Software\<VendorAlias>\`

### Debugging Constraints
```
MITM: cacert.pem required for startup; tampering caused immediate abort
Frida: Unstable on target
Solution: x64dbg for mapping EVP_DigestVerifyFinal (EAX=1 valid, 0=invalid)
```

## 📋 Evidence & MITM/Proxy Reports (Sanitized)

### Edge Fingerprinting (Safe)
```bash
# scripts/rest_probe.sh (SAFE_MODE)
HTTP/2 400
content-type: text/html
<redacted body> # ~155 bytes (example)
```

### API SSTI Indicator (Safe)
```
Encodings: raw → %7B%7B → %257B
Expected: switch from JSON to HTML error document
HTTP/2 403
content-type: text/html; charset=UTF-8
```

### REST Gateway Stub (Safe)
```json
GET /rest/v1/<table>?select=*
HTTP/2 200
{ "msg": "Hello World" }
```

### GraphQL Strictness (Safe)
```json
POST /graphql/v1 {"query":"{ __typename }"}
HTTP/2 401
{ "message": "Invalid API key", "hint": "Double check your Supabase key." }
```

## ⏱️ Timing-Oracle Research (Sanitized)
**Concept:** Use error/timing deltas for character-by-character prefix extension testing

**Observations:** 
- Jitter requires averaging and heavier loop workload
- Consistent but weak signals observed
- Work halted for public release

**Note:** Repo provides research notes, not exploit code.

## 🛡️ Defensive Recommendations

### Immediate Actions
- Enforce strict Host header handling (normalize/validate via trusted proxy headers)
- Ensure templating layers for API responses cannot be reached by untrusted input
- Prefer strict JSON serializers over template rendering for API endpoints

### Long-term Strategies
- Continue blocking egress from API tiers
- Consider canary outbound endpoints to audit attempted exfil
- For desktop clients: prefer short-lived tokens or server-side session checks
- Monitor and rate-limit unusual sequences that could build timing oracles

## 📚 Methodology & Playbooks

### Web/API Assessment
1. **Recon:** Enumerate endpoints; capture baseline response shapes/lengths
2. **Probe:** Inject harmless encodings; compare JSON vs HTML response transitions  
3. **Egress test:** DNS/HTTP callbacks (expect blocks; record results)
4. **Logging:** Save headers/bodies per probe; compute size diffs

### Client/Binary Analysis (Windows)
1. **Unpack** PyInstaller bundle; catalog Python modules and crypto libs
2. **Search markers:** `EVP_DigestVerifyFinal`, `-----BEGIN`, `sqlite3`, `Data.db`
3. **ProcMon filters:** Process Name = app; include `RegCreateKey`, `RegSetValue`, `WriteFile`
4. **x64dbg:** Identify indirect call to `EVP_DigestVerifyFinal`; watch EAX; confirm UI dependency

## 🛠️ Tools & Environment
- **HTTP tooling:** curl, jq, Burp/mitmproxy (observation only)
- **Recon:** ffuf, dirsearch, wayback tools (optional)
- **Debuggers:** x64dbg, IDA, ProcMon; Frida explored but unstable
- **Scripts:** Custom scanners (PEM/EVP markers), safe REST/GraphQL probes
