# Instructions for this QN90B adaptation

Read README.md and all numbered docs before touching a TV. This profile records
one QN55QN90BAFXZA on owner-reported T-PTMAKUC-1720.7, not all QN90B models.
On any mismatch, stop before mutation and investigate a separate profile.
Use an explicitly supplied TV IP and callback host; never scan the LAN.

Inventory and back up the actual device before mutation. Keep verified local and
TV-side per-database SQLite .backup snapshots and original routing selectors.
Prepare exact inverse operations before applying changes. Never overwrite the
first backup or restore an entire old database over a live registry.

Preserve HDMI, sound, networking, Bluetooth, accessibility, streaming apps and
native settings. Never globally disable org.tizen.menu. Do not kill all apps,
clear app data, log users out or disable stock Home just because it is installed.
A process snapshot does not prove permanent absence. Do not add watchdogs.

Use the standalone signed QuietHome1 package. Do not replace a Samsung app binary,
flash firmware, change passwd/SDB verification keys, or bypass another model's
root guard. The SDK UID901/System routing path worked on the observed device;
that is not root and may not work on another firmware.

Keep SDK sessions sequential and commands below 30 seconds. Use separate capture
calls for dotnet helpers and vconftool commands. Capture failed combined invocations
before retrying; they can leave partial state. Verify before/after and restore
all changed selectors if any assignment fails.

Manually test UI, apps, HDMI/picture/sound, settings, network and Bluetooth before
assigning Home. Read back operation/main, Home and startup; then test the Home
button, full restart and standby/wake separately. The observed TV resumes the
last HDMI input at power-on even though Home opens Quiet Home; do not claim
startup foregrounding or universal persistence.

Keep proprietary data, signing material, local art and builds under ignored
.local/. Never publish raw logs, addresses, serial/DUID, account data, screenshots,
certificates, tokens, stock binaries or DBs. Scan staged content before publishing.
Retain upstream MIT/third-party notices. Compile against matching device refs,
keep Private=false and never bundle Samsung DLLs. Clearly distinguish the tested
private installation from the sanitized public build with placeholder art.
