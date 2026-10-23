# Compatibility and observed runtime

Only one television/firmware combination was investigated: QN55QN90BAFXZA with
owner-reported T-PTMAKUC-1720.7. About This TV is the firmware source; a CLI flag
is an operator declaration, not independent detection.

Observed system: ARMv7, Linux 5.4.77, Tizen platform 6.5.0, release text beginning
Tizen6/TV, active .NET runtime 3.1.3. The original quiet-tizen case study uses a
2025 U8000F and cannot be treated as a universal Samsung profile.

The root transport preflight had a release-family mismatch. Bixby Promotion and
QuickLaunch stock containers used by the base recipes were absent. Neither the
original model check nor the root guard was bypassed. No root session, firmware
flash, passwd change, SDB key replacement or stock binary replacement was used.

An unregistered NUI preview failed during application-context initialization.
A small registered developer-signed probe displayed successfully; a full standalone
.NET 3.1 launcher then worked. Exact device framework references mattered because
newer Window APIs and image settings were unavailable on this runtime.

The SDK command context reported UID901 and SMACK System. It could invoke the
Home-operation API and vconftool for the selected Home/startup keys. Those
capabilities are observations on this firmware, not promised privileges.

The observed HDMI source values were 13 (Switch), 14 (PS5), 16 (Switch 2). The
obsolete source 15 in the base example was corrected. These reflect the owner's
wiring; inspect actual source discovery before changing Home.cs on another TV.

Original routing on the observed unit: operation/main and Home were
com.samsung.tv.csfs; startup was org.tizen.tv-viewer. Capture your own originals.
The observed device had 447 initial app records; registered probe + launcher
brought the count to 449. All existing disable/onboot/autorestart fields remained
unchanged. The tools do not disable Samsung Home, sidebar or native settings.
