#!/usr/bin/env bash
# Share the app with friends: shared mode (accounts + sandboxed judge) behind a Cloudflare quick tunnel.
#
#   CP_INVITE_CODE=some-secret tools/share.sh
#
# Prints a public https://<random>.trycloudflare.com address. Friends open it, choose "Create account"
# and enter the invite code. Your own account: python3 tools/users.py add <name> --mine
# The site is reachable only while this script (and this laptop) is running.
set -euo pipefail
cd "$(dirname "$0")/.."
PORT=${PORT:-8765}
: "${CP_INVITE_CODE:?Set CP_INVITE_CODE to a secret your friends will type when they sign up}"
export CP_INVITE_CODE
python3 server.py --multi-user --port "$PORT" --no-browser &
SERVER=$!
trap 'kill $SERVER 2>/dev/null' EXIT
sleep 2
kill -0 $SERVER  # the server refused to start (see the message above)
if command -v cloudflared >/dev/null; then
  cloudflared tunnel --no-autoupdate --url "http://127.0.0.1:$PORT"
else
  echo "cloudflared is not installed, so the app is only on http://127.0.0.1:$PORT."
  echo "Install it from https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
  wait $SERVER
fi
