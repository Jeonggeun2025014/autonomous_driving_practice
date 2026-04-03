#!/usr/bin/env bash
# Helper script: shows recommended Bubblewrap commands to create a TWA project
set -e

echo "This script prints recommended bubblewrap commands. Ensure bubblewrap is installed."
echo
echo "1) Initialize project (replace <HOST> with your hosting domain where manifest.json is available over HTTPS):"
echo "   bubblewrap init --manifest=https://<HOST>/src/autonomous_driving_practice/remote_controller/manifest.json --directory=project"
echo
echo "2) Build the TWA project (inside the created project dir):"
echo "   bubblewrap build --directory=project"
echo
echo "Notes: Bubblewrap requires the PWA to be served over HTTPS. Use a real host for Play Store packaging."
