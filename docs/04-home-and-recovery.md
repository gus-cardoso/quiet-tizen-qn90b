# Home routing and recovery

The consolidated public Python helper is adapted from the commands used on the
owner's TV. Its syntax and offline package/parser checks pass; it has not been
re-run end-to-end against the TV as a public release. Review it before use.

Proceed only after the visible functional checks pass and a fresh backup exists.
The SDK context on the observed TV successfully called
app_operation_set_current_app(main, QuietHome1.Home) and wrote the Home/startup
preferences. No root was needed for this specific operation. Do not assume it
will work on another firmware, and do not work around permission denial by
replacing Samsung binaries or weakening system security.

Using the tvArgs variables from setup and a **fresh** backup folder:

```powershell
python tools/tv.py status @tvArgs --snapshot .local/backups/YOUR_PHASE
python tools/tv.py route @tvArgs --snapshot .local/backups/YOUR_PHASE --validated
```

The helper stages only its three .NET files, hash-checks them, captures the actual
operation/main handler and guards package identity and original preferences.
It stores original operation, Home and startup both locally and on TV before
mutation. It changes operation first, then Home/startup, reads them back, and
attempts selector-specific restoration if assignment fails. A network loss can
interrupt recovery: inspect state and run restore once connectivity returns.
Never rerun blindly or replace the live registry from an old DB.

The routing helper is deliberately limited to QuietHome1.Home and the observed
Samsung Home handler com.samsung.tv.csfs. If your original differs, stop and adapt
a separately reviewed profile. Keep the helper and backups until recovery and
restart testing are complete; they are inert files, not a running daemon.

After all three selectors read back as QuietHome1.Home:

1. Press Home while viewing HDMI and after exiting a streaming app.
2. Turn off/on normally for standby/wake; test Home and essential functions.
3. Hold Power until the TV restarts and Samsung's logo appears; test again.
4. Re-run status and retain the updated private validation record.

**Observed behavior:** both power cycles resumed the last HDMI input. Home still
opened Quiet Home. The saved startup preference did not prove automatic
foregrounding; this repository does not claim that feature works.

## Restore original routing

```powershell
python tools/tv.py restore @tvArgs --snapshot .local/backups/YOUR_ROUTING_PHASE
python tools/tv.py status @tvArgs --snapshot .local/backups/YOUR_ROUTING_PHASE
```

Restore checks current selectors for drift, restores the three saved values, and
reads them back. On the observed unit the originals were operation/Home =
com.samsung.tv.csfs and startup = org.tizen.tv-viewer. Your snapshot is authoritative.
No packages or app data are removed. Never uninstall the selected Home app before
restoring routing to an installed, working handler.

For a launcher-only uninstall after routing restoration, verify QuietHome1.Home
still belongs to QuietHome1 and executes QuietHomeStandalone.dll, then use SDB to
uninstall only QuietHome1. Never clear streaming-app data or factory-reset as a
first recovery action. A downgrade may require uninstalling only the test app
then reinstalling its preserved signed package; its own data may reset.

## Samsung Home in the background

Samsung Home and the sidebar were left enabled as recovery fallbacks. One
post-restart process snapshot showed neither running while Quiet Home was active.
That is a snapshot, not a guarantee they can never launch later. Native
org.tizen.menu may remain running after settings use and must be preserved.
No stock Home/sidebar disabling, browser cleanup or settings bridge was applied.
