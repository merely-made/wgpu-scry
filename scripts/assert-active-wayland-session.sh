#!/usr/bin/env bash
# Copyright 2026 Mark Alan Boykin
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0

# logind session IDs change across logins. Check the runner user's current
# sessions without choosing a display, creating a session, or changing one.
set -euo pipefail

runner_uid=$(id -u)
if ! session_ids=$(loginctl show-user "$runner_uid" -p Sessions --value); then
    echo "Could not enumerate the runner user's logind sessions." >&2
    exit 1
fi

found=0
for session_id in $session_ids; do
    if ! properties=$(loginctl show-session "$session_id" -p User -p Active -p Type); then
        echo "Could not inspect logind session $session_id." >&2
        exit 1
    fi
    session_user=
    session_active=
    session_type=
    while IFS= read -r property; do
        case "$property" in
            User=*) session_user=${property#User=} ;;
            Active=*) session_active=${property#Active=} ;;
            Type=*) session_type=${property#Type=} ;;
        esac
    done <<< "$properties"
    if [[ "$session_user" == "$runner_uid" && "$session_active" == yes && "$session_type" == wayland ]]; then
        printf 'Verified active Wayland session %s for runner UID %s.\n' "$session_id" "$runner_uid"
        found=1
    fi
done

if [[ "$found" != 1 ]]; then
    echo "No active Wayland logind session belongs to the runner user." >&2
    exit 1
fi
