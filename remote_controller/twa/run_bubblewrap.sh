#!/usr/bin/env bash
set -euo pipefail

# run_bubblewrap.sh - helper to initialize and build a TWA project using Bubblewrap (via npx)
# Usage:
#   HOST=yourdomain.com PACKAGE_ID=com.example.fourwremote ./run_bubblewrap.sh
# HOST must be HTTPS-hosted and reachable by Bubblewrap to fetch the PWA manifest.

HOST=${HOST:-}
PACKAGE_ID=${PACKAGE_ID:-com.example.fourwremote}
OUTDIR=${OUTDIR:-project}

if [ -z "$HOST" ]; then
  echo "ERROR: Please set HOST (the https host where your PWA is served)."
  echo "Example: HOST=example.com PACKAGE_ID=com.myorg.fourwremote ./run_bubblewrap.sh"
  exit 1
fi

MANIFEST_URL="https://${HOST}/src/autonomous_driving_practice/remote_controller/manifest.json"

echo "Using manifest: $MANIFEST_URL"
echo "Output directory: $OUTDIR"
echo "Package ID: $PACKAGE_ID"

echo "Running bubblewrap init (may prompt for values)..."
npx --yes @bubblewrap/cli init --manifest="$MANIFEST_URL" --directory="$OUTDIR"

echo "Now building the Android project (this will call Gradle inside $OUTDIR)..."
npx --yes @bubblewrap/cli build --directory="$OUTDIR"

echo "Done. The Android project is in $OUTDIR. Open it in Android Studio to sign/build an AAB for Play Store."
