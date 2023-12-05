import os
import re
import shutil
import subprocess
import time

DAYS_TO_KEEP = 7


def main() -> None:
    paths = get_direnvs()
    deleted, kept = delete_old_envs(paths)
    print("This will take a long time...")

    subprocess.run(
        ["nix-collect-garbage", "--quiet", "--delete-older-than", f"{DAYS_TO_KEEP}d"]
    )

    print("Deleted:\n{}".format("\n".join(deleted)))
    print("\nKept:\n{}".format("\n".join(kept)))


def delete_old_envs(direnvs: list[str]) -> tuple[list[str], list[str]]:
    now = time.time()
    deleted = []
    kept = []

    for direnv in direnvs:
        file_path = f"{direnv}/bin/nix-direnv-reload"

        if not os.path.exists(file_path):
            shutil.rmtree(direnv)
            deleted.append(direnv)
            continue

        mtime = os.path.getmtime(file_path)
        if (now - mtime) / (24 * 60 * 60) > DAYS_TO_KEEP:
            shutil.rmtree(direnv)
            deleted.append(direnv)
        else:
            kept.append(direnv)

    return deleted, kept


def get_direnvs() -> list[str]:
    pattern = re.compile(r"^(.+\.direnv)/flake-profile.+ -> .+nix-shell-env$")
    process = subprocess.run(
        ["nix-store", "--gc", "--print-roots"], capture_output=True
    )
    paths = []

    for line in process.stdout.decode("utf-8").splitlines():
        match = pattern.search(line)
        if match:
            paths.append(match.group(1))

    return paths


if __name__ == "__main__":
    main()
