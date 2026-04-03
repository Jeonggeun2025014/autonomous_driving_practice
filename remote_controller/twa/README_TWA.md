Android TWA (Trusted Web Activity) packaging guide

This folder contains a minimal template and helper script to package the remote controller PWA as an Android TWA using Bubblewrap.

Prerequisites
- Node.js and npm installed.
- Java JDK (11+) and Android SDK/Platform tools installed for building the final app.
- Bubblewrap CLI (installed globally or via npm in this folder).

Quick steps (recommended)
1. Install Bubblewrap (global):

   npm install -g @bubblewrap/cli

2. Edit `twa-manifest.json` fields: `host`, `packageId`, `name`, `launcherName`, and `manifest` `start_url` if necessary.

3. From this folder, run (this will create an Android project):

   bubblewrap init --manifest=https://<HOST>/src/autonomous_driving_practice/remote_controller/manifest.json --manifest=https://<HOST>/src/autonomous_driving_practice/remote_controller/manifest.json --directory=project

   # or using the local manifest if hosting locally and serving over HTTPS (recommended for production)

4. Build the project:

   bubblewrap build --directory=project

5. Create a keystore (if you don't have one):

   keytool -genkeypair -v -keystore my-release-key.jks -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000

6. Sign the AAB/APK according to Android docs and upload to Play Console.

Notes
- Bubblewrap may prompt for values and will create an Android Studio project under `project/`.
- For Play Store, prefer generating an Android App Bundle (AAB) via the Android build tools.
- For local testing you can run the generated APK on a device or emulator.

If you want, I can:
- Run a ready-made Bubblewrap command sequence in a script (non-destructive) and produce the generated project files (requires Bubblewrap installed locally).
- Create a GitHub Actions workflow skeleton to build and sign your TWA using secrets.
