#!/usr/bin/env python3

import subprocess
import sys
from os import getcwd, path
from shlex import quote

LOCAL_GIT = "/usr/local/Cellar/git/2.43.0/bin/git"
REMOTE_GIT = "git"

HOST = "homedocker"

MOUNTED_PATH_PREFIX = "/System/Volumes/Data/net/192.168.1.20"
TEMP_FOLDER_PREFIX = "/var/folders"


FORCE_LOCAL_KEYWORDS = ("rebase",)


def isascii(s):
    return len(s) == len(s.encode())


def copy_temp_file(local_file):
    remote_prefix = "/tmp"
    if not local_file.startswith("/"):
        remote_prefix = f"{remote_prefix}/"
    remote_file = f"{remote_prefix}{local_file}"

    remote_base_dir = path.dirname(remote_file)
    mkdir_cmd = ["ssh", HOST, "mkdir", "-p", remote_base_dir]
    subprocess.run(mkdir_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    scp_cmd = ["scp", local_file, f"{HOST}:{remote_file}"]
    subprocess.run(scp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return remote_file


def prepare_args(args):
    for arg in args:
        if arg.startswith(TEMP_FOLDER_PREFIX):
            remote_file = copy_temp_file(arg)
            yield remote_file
            continue

        if not isascii(arg) or " " in arg or '"' in arg:
            arg = quote(arg)

        yield arg


def run_remmote_git(pwd, args):
    git_args = " ".join(prepare_args(args))
    git_cmd = f"cd {pwd}; {REMOTE_GIT} {git_args}"

    cmd = ["ssh", HOST, git_cmd]
    result = subprocess.run(cmd, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)
    return result.returncode


def run_local_git(args):
    result = subprocess.run(
        [
            LOCAL_GIT,
            *args,
        ],
        stdout=sys.stdout,
        stdin=sys.stdin,
        stderr=sys.stderr,
    )
    return result.returncode


def force_local(argv: list[str]) -> bool:
    for keyword in FORCE_LOCAL_KEYWORDS:
        for arg in argv:
            if keyword in argv:
                return True
    return False


if __name__ == "__main__":
    pwd = getcwd()
    if pwd.startswith(MOUNTED_PATH_PREFIX) and not force_local(sys.argv[1:]):
        returncode = run_remmote_git(pwd, sys.argv[1:])
    else:
        returncode = run_local_git(sys.argv[1:])
    sys.exit(returncode)
