# Artwork and provenance

Base: [quiet-tizen](https://github.com/jss8649/quiet-tizen/tree/cf518d7a9278dca7990e27756218258e44044a29).
Retain its MIT notice and the Free My TV, Inter and Material Symbols notices.
See NOTICE.md for exact commits and licenses.

The owner's installed-app icons were copied privately from that TV's installed
resources/cache and checked by hash and image decoding. None are published here.
The public catalog uses text-only PNG placeholders to avoid the old runtime's
SVG-text/hidden-parent compatibility issue. Supply PNGs privately under ignored
launcher/assets/app-icons and reference them from apps.local.json. Verify app IDs
against your own package registry; do not copy another user's custom app list.

The final private PS5 dock tile uses the authentic PlayStation family symbol,
unmodified geometry in white, above a smaller PS5 label. An early generated hero
image and a hand-drawn console icon were rejected and are not part of this repo.
To obtain the optional official mark locally:

```powershell
python tools/fetch_ps_logo.py
```

This fetches the official brand sprite from playstation.com, extracts only
ps-icon_brand_playstation-family, and saves a private dock SVG and provenance/hash
under ignored assets/custom-art and .local. The blue tile and PS5 wordmark are
from the base launcher. The optional symbol is not MIT-licensed by this project.
The build selects it when present; otherwise the public plain-PS5 tile is used.
The large PS5 feature card remains the original vector illustration.

No room photos or raw device screenshots are included. The mint house app icon
is a simple project-native graphic with readable QUIET HOME text, registered as
a native app icon in shared/res per Tizen's .NET packaging conventions:
https://github.com/Samsung/tizen-docs/blob/master/docs/application/dotnet/get-started/first-app.md

## Release hygiene

Run python tools/audit_public.py and inspect git diff --cached --stat and the
actual staged diff before any public push. The audit is a focused check, not a
complete secret scanner. Never add .local, private custom art, certificates,
DUID/serial, network addresses, databases, Samsung DLLs, signed TPKs or personal
photographs. Do not distribute an entire development workspace.
