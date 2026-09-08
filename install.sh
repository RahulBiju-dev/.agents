#!/usr/bin/env sh
# Entry point: run this from inside the project you want the toolkit in.
#
#   git clone https://github.com/RahulBiju-dev/agents.git ~/.agents-src
#   cd your-project && ~/.agents-src/install.sh
#
# Every argument is forwarded to scripts/install.py (--target, --hosts,
# --link-style, --dry-run, --uninstall). The current directory is never
# changed, because install.py defaults --target to it.

set -eu

script=$0
while [ -L "$script" ]; do
    link=$(readlink "$script")
    case $link in
        /*) script=$link ;;
        *) script=$(dirname -- "$script")/$link ;;
    esac
done
here=$(CDPATH= cd -- "$(dirname -- "$script")" && pwd -P)

if command -v python3 >/dev/null 2>&1; then
    python=python3
elif command -v python >/dev/null 2>&1; then
    python=python
else
    echo "install.sh: no python3 on PATH; this installer needs Python 3.10 or newer" >&2
    exit 1
fi

exec "$python" "$here/scripts/install.py" "$@"
