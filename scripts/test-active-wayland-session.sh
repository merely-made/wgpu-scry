#!/usr/bin/env bash
# Copyright 2026 Mark Alan Boykin
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

# Command-mocked preflight checks; never contact logind or change a session.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
mock_dir=$(mktemp -d)
cleanup() {
    rm -f -- "$mock_dir/id" "$mock_dir/loginctl" "$mock_dir/output"
    rmdir -- "$mock_dir"
}
trap cleanup EXIT

cat > "$mock_dir/id" <<'SH'
#!/usr/bin/env bash
[[ "$*" == "-u" ]] || exit 1
echo 1000
SH

cat > "$mock_dir/loginctl" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
if [[ "$1" == show-user ]]; then
    [[ "$*" == "show-user 1000 -p Sessions --value" ]] || exit 1
    case "$PREFLIGHT_CASE" in
        user_lookup_failure) exit 1 ;;
        no_sessions) echo "" ;;
        rotated) echo "c42 91" ;;
        *) echo 91 ;;
    esac
elif [[ "$1" == show-session ]]; then
    [[ "$3 $4 $5 $6 $7 $8" == "-p User -p Active -p Type" ]] || exit 1
    [[ "$2" == c42 || "$2" == 91 ]] || exit 1
    if [[ "$2" == c42 ]]; then
        printf 'User=1000\nActive=no\nType=x11\n'
        exit 0
    fi
    case "$PREFLIGHT_CASE" in
        session_lookup_failure) exit 1 ;;
        inactive) printf 'User=1000\nActive=no\nType=wayland\n' ;;
        x11) printf 'User=1000\nActive=yes\nType=x11\n' ;;
        other_uid) printf 'User=2000\nActive=yes\nType=wayland\n' ;;
        missing_type) printf 'User=1000\nActive=yes\n' ;;
        *) printf 'User=1000\nActive=yes\nType=wayland\n' ;;
    esac
else
    exit 1
fi
SH
chmod +x "$mock_dir/id" "$mock_dir/loginctl"

for test_case in rotated inactive x11 other_uid no_sessions user_lookup_failure session_lookup_failure missing_type; do
    actual=0
    PATH="$mock_dir:$PATH" PREFLIGHT_CASE="$test_case" \
        bash "$script_dir/assert-active-wayland-session.sh" > "$mock_dir/output" 2>&1 || actual=$?
    if [[ "$test_case" == rotated ]]; then
        if [[ "$actual" != 0 ]] || ! grep -Fq 'session 91 for runner UID 1000' "$mock_dir/output"; then
            cat "$mock_dir/output" >&2
            echo "FAIL: rotated session IDs should pass." >&2
            exit 1
        fi
    elif [[ "$actual" == 0 ]]; then
        echo "FAIL: $test_case must refuse admission." >&2
        exit 1
    fi
    printf 'PASS: %s\n' "$test_case"
done
