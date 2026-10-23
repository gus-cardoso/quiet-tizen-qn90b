# Build, sign and test the standalone package

Obtain these matching assemblies from your own TV or permitted matching SDK and
store them in .local/tv-framework: Tizen.NUI.dll, Tizen.Applications.Common.dll,
Tizen.System.dll and Tizen.dll. Observed source folder on this TV was
/usr/share/dotnet.tizen/framework/. Inspect actual paths and transfer/hash-check
each file privately. Do not use random desktop/mobile references or publish them.
The project sets Private=false so Samsung assemblies are not bundled.

The observed build used an isolated .NET 6 SDK targeting netcoreapp3.1, compatible
with the TV's .NET 3.1.3 runtime. This old runtime is a device constraint, not a
recommendation for new desktop software. Supply your own dotnet path if needed.

Review the source mappings in launcher/src/Home.cs and the catalog before building.
For custom apps, copy launcher/assets/apps.json to ignored apps.local.json; use
actual installed IDs and local PNGs. See the artwork guide.

```powershell
python tools/build.py --framework .local/tv-framework --dotnet PATH_TO_DOTNET
```

The output is an unsigned existing TPK under .local/package, and the routing helper
under .local/build/Routing. The build never connects to a TV. Sign the **existing
TPK file** using your own active Samsung TV certificate profile:

```powershell
tizen package -t tpk -s YOUR_CERTIFICATE_PROFILE -o .local/signed -- .local/package/QuietHome1-0.1.9-unsigned.tpk
& $sdbExe -s "${tvIp}:26101" install .local/signed/QuietHome1-0.1.9-unsigned.tpk
tizen run -p QuietHome1.Home -t QN55QN90BAFXZA
```

Do not pass the package directory to the signer; the tested CLI expected package
build metadata and failed that path. Some SDK CLI errors returned exit code zero:
verify the signed file exists and inspect installation acceptance/readback.
A filename ending unsigned.tpk can still be the signed output in .local/signed.

Before installing, inventory QuietHome1 and QuietHome1.Home. If the identity is
already used by another application, stop. Updates must retain the same author
certificate. Do not overwrite an unrelated app identity.

Keep Samsung Home as default until these visible checks pass:

- UI pages render, text/icons are legible, remote D-pad/Select/Back work.
- PS5 and both Switch cards select the intended input with picture and sound.
- Streaming app shortcuts open the right app and playback works.
- Remote volume/mute, All Settings, Network and Bluetooth device list work.
- Advanced settings remain accessible and accessibility behavior is acceptable.

This source has no four-minute timeout. Back exits the launcher from Home; Back
from the Apps page returns to Quiet Home. Until routing is assigned, reopen the
standalone app via Samsung Apps (mint house icon / Quiet Home Test) or tizen run.

App launching uses the public appmanager.launch privilege. Private native input
and sound calls can fail on other firmware and report a fallback message.
Brightness, Game Mode and Sleep Timer open Samsung settings rather than writing
unverified values. Clock updates every 30 seconds and pauses with the application;
no watchdog, controller polling loop or network telemetry client is included.
