import itertools
import os
import re
import shutil
import subprocess
import time

DAYS_TO_KEEP = 7


def main() -> None:
    direnvs, results = get_environments()
    deleted_binaries, kept_binaries = delete_old_binaries(results)
    deleted_direnvs, kept_direnvs = delete_old_envs(direnvs)
    print("This will take a long time...")

    subprocess.run(
        ["nix-collect-garbage", "--quiet", "--delete-older-than", f"{DAYS_TO_KEEP}d"]
    )

    print(
        "Deleted:\n{}".format(
            "\n".join(itertools.chain(deleted_direnvs, deleted_binaries))
        )
    )
    print("\nKept:\n{}".format("\n".join(itertools.chain(kept_direnvs, kept_binaries))))


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


def delete_old_binaries(results: list[str]) -> tuple[list[str], list[str]]:
    now = time.time()
    deleted = []
    kept = []

    for result in results:
        ctime = os.path.getctime(result)
        if (now - ctime) / (24 * 60 * 60) > DAYS_TO_KEEP:
            os.unlink(result)
            deleted.append(result)
        else:
            kept.append(result)

    return deleted, kept


def get_environments() -> tuple[list[str], list[str]]:
    direnv_pattern = re.compile(r"^(.+\.direnv)/flake-profile.+ -> .+nix-shell-env$")
    result_pattern = re.compile(r"^(.+/result) ->")
    process = subprocess.run(
        ["nix-store", "--gc", "--print-roots"], capture_output=True
    )
    direnvs = []
    results = []

    for line in process.stdout.decode("utf-8").splitlines():
        direnv = direnv_pattern.search(line)
        if direnv:
            direnvs.append(direnv.group(1))

        result = result_pattern.search(line)
        if result:
            results.append(result.group(1))

    return direnvs, results


if __name__ == "__main__":
    main()
