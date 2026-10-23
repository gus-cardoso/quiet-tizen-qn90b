# Developer setup and private backups

Use a computer on the TV's network. Install Samsung's official Tizen Studio/TV
extension and SDB, then enable Developer Mode in the TV Apps screen and set the
computer's actual callback/host address. Restart only as the TV instructs.
Keep the TV's Developer Mode authorization available throughout testing.

Create a Samsung **TV** author/distributor certificate profile with Certificate
Manager. The tested profile used Public privilege and the exact TV DUID in the
distributor certificate. A TV Key/serial is not a substitute for the DUID.
Back up author.p12 and distributor.p12 privately and preserve the author identity
for updates. Never share the certificate passwords or commit certificate files.

Official references:
- https://developer.samsung.com/smarttv/develop/getting-started/setting-up-sdk/creating-certificates.html
- https://developer.samsung.com/smarttv/develop/faq/tizen-net-tv.html

The helper uses the external SDK transport from samsung-tv-root, pinned during
adaptation to 3b97edf3762db7670585d73e29623dc56195bf98. Clone it under ignored
.local/transport and install its Python dependencies in an isolated environment.
Read that project's SDB command-channel implementation. This guide uses SDK
capture, not the root probe or archive-root workflows.

```powershell
git clone https://github.com/chris-ritsen/samsung-tv-root .local/transport
git -C .local/transport checkout 3b97edf3762db7670585d73e29623dc56195bf98
```

Set local variables for your own network and installed SDB. The example values
below are placeholders, not a scan or a discovery procedure:

```powershell
$tvIp = 'YOUR_TV_IP'
$callbackIp = 'YOUR_COMPUTER_IP'
$sdbExe = 'PATH_TO_SDB_EXE'
& $sdbExe connect "${tvIp}:26101"
$tvArgs = @('--host', $tvIp, '--callback', $callbackIp, '--sdb', $sdbExe,
  '--transport-src', '.local/transport/src', '--firmware', 'T-PTMAKUC-1720.7')
python tools/tv.py doctor @tvArgs
python tools/tv.py backup @tvArgs
```

Doctor is read-only; review runtime/model output against the profile. The tool
requires the exact observed model and declared firmware. Other firmware needs
independent investigation, not a forged argument.

Backup creates unique TV-side SQLite .backup snapshots of .pkgmgr_parser.db,
.app-context.db and .webappservice.db, checks integrity, transfers in bounded
chunks, and verifies byte counts and SHA-256 locally. Files and a private manifest
stay under .local/backups. It captures Home/startup preferences; the routing phase
captures the operation/main handler before mutation. Never publish these files.

A capture callback needs inbound connectivity from this explicit TV to this
computer. Resolve the local firewall/Developer Mode host configuration if it
fails. Do not disable all firewall protection. SDK commands run sequentially;
keep individual commands below 30 seconds. Run dotnet and vconftool in separate
captures; combining them caused the observed SDK invocation to close unexpectedly.
