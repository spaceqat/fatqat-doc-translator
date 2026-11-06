"""Build translated HTML at the RTD version root from a pinned checkout."""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import yaml
from site_config import upstream_config, read_config, translate_nav, translate_gallery
import translate

ROOT = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), check=True, **kwargs)


def checkout(repository, workdir, commit):
    clone = workdir.resolve() / "upstream"
    if not clone.exists():
        run(["git", "init", "--quiet", clone])
        run(["git", "-C", clone, "remote", "add", "origin", repository])
    # A reusable build directory retains expensive tutorial execution caches.
    actual = subprocess.check_output(
        ["git", "-C", str(clone), "remote", "get-url", "origin"], text=True
    ).strip()
    if actual != repository:
        raise ValueError("Build directory belongs to a different upstream repository")
    run(["git", "-C", clone, "fetch", "--depth", "1", "origin", commit])
    run(["git", "-C", clone, "checkout", "--quiet", "--detach", commit])
    return clone


def assert_snapshot(clone):
    for relative in ("en", "tutorial-sources/en"):
        snapshot = ROOT / "upstream-docs" / relative
        prefix = "docs/mkdocs/" + relative + "/"
        tracked = subprocess.check_output(
            ["git", "-C", str(clone), "ls-files", prefix], text=True
        ).splitlines()
        expected = {
            str(Path(p).relative_to("docs/mkdocs/" + relative)) for p in tracked
        }
        actual = {
            str(p.relative_to(snapshot)) for p in snapshot.rglob("*") if p.is_file()
        }
        if expected != actual:
            raise ValueError(
                f"Snapshot file list differs from pinned upstream: {relative}"
            )
        for path in tracked:
            snap = snapshot / Path(path).relative_to("docs/mkdocs/" + relative)
            if snap.read_bytes().replace(b"\r\n", b"\n") != (
                clone / path
            ).read_bytes().replace(b"\r\n", b"\n"):
                raise ValueError(f"Snapshot content differs: {path}")


def generate_config(clone, canonical_url, locale="zh"):
    merged = translate.global_map(translate.load_database())
    lookup = lambda text: translate._lookup(merged, translate.normalize(text)) or text
    config = yaml.safe_load(
        (ROOT / f"overlay/mkdocs.{locale}.yml").read_text(encoding="utf-8")
    )
    config["hooks"] = [str(ROOT / "overlay/translation_notice.py")]
    config["nav"] = translate_nav(read_config(clone / "mkdocs.yml")["nav"], lookup)
    config["site_url"] = canonical_url.rstrip("/") + "/"
    (clone / f"mkdocs.{locale}.yml").write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    gallery = yaml.safe_load(
        (clone / "docs/mkdocs/tutorial-sources/gallery.yml").read_text(encoding="utf-8")
    )
    target = clone / f"gallery.{locale}.generated.yml"
    target.write_text(
        yaml.safe_dump(
            translate_gallery(gallery, lookup, locale), allow_unicode=True, sort_keys=False
        ),
        encoding="utf-8",
    )
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--locale", choices=("zh", "ko"), default=os.environ.get("FATQAT_LOCALE", "zh"))
    parser.add_argument("--workdir", type=Path, default=ROOT / ".build")
    parser.add_argument("--upstream-url", default=upstream_config()["repository"])
    parser.add_argument("--site-url", default="http://127.0.0.1:8767/")
    parser.add_argument("--skip-install", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument(
        "--stage", choices=("all", "prepare", "tutorials", "english", "translated"),
        default="all", help="run one RTD step, or the complete local build (default)",
    )
    args = parser.parse_args()
    locale = args.locale
    translate.configure_locale(locale)
    output = Path(args.output).resolve()
    if output == ROOT or output in ROOT.parents or (output / ".git").exists():
        raise ValueError("Output must be a dedicated build directory")
    if args.require_complete and translate.run_check(require_complete=True):
        return 1
    commit = (ROOT / "UPSTREAM_COMMIT").read_text().strip()
    if args.stage in ("all", "prepare"):
        clone = checkout(args.upstream_url, args.workdir, commit)
    else:
        clone = args.workdir.resolve() / "upstream"
        if not (clone / ".git").exists():
            raise ValueError("Run --stage prepare before the other build stages")
        actual = subprocess.check_output(
            ["git", "-C", str(clone), "rev-parse", "HEAD"], text=True
        ).strip()
        if actual != commit:
            raise ValueError("Upstream checkout has changed; rerun --stage prepare")
    assert_snapshot(clone)
    python = sys.executable
    if args.stage in ("all", "prepare") and not args.skip_install:
        run([python, "-m", "pip", "install", clone])
        run(
            [
                python,
                "-m",
                "pip",
                "install",
                "-r",
                clone / "docs/mkdocs/requirements.txt",
                "jieba",
            ]
        )
    if args.stage == "prepare":
        return 0
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    # Execute once in a separate RTD command; both sites reuse these results.
    if args.stage in ("all", "tutorials"):
        run(
            [python, "docs/mkdocs/tools/build_tutorials.py", "--execute-if-needed"],
            cwd=clone, env=env,
        )
    if args.stage == "tutorials":
        return 0
    # English generates and validates the shared guide/homepage assets.
    if args.stage in ("all", "english"):
        run(
            [
                python,
                "-m",
                "mkdocs",
                "build",
                "--strict",
                "-f",
                "mkdocs.yml",
                "-d",
                args.workdir.resolve() / "english",
            ],
            cwd=clone,
            env=env,
        )
    if args.stage == "english":
        return 0
    mkdocs_root = clone / "docs/mkdocs"
    env["FATQAT_MKDOCS_ROOT"] = str(mkdocs_root)
    run(
        [python, ROOT / "tools/translate.py", "--locale", locale, "render",
         *(["--strict"] if args.require_complete else []), "--out-root", mkdocs_root],
        env=env,
    )
    shutil.copytree(
        mkdocs_root / "en/assets", mkdocs_root / locale / "assets", dirs_exist_ok=True
    )
    shutil.copytree(
        ROOT / "overlay/assets", mkdocs_root / locale / "assets", dirs_exist_ok=True
    )
    gallery = generate_config(clone, args.site_url, locale)
    run(
        [
            python,
            ROOT / "tools/build_zh_assets.py",
            "--clone",
            clone,
            "--gallery",
            gallery,
            "--locale",
            locale,
        ],
        env=env,
    )
    run(
        [
            python,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "-f",
            f"mkdocs.{locale}.yml",
            "-d",
            output,
        ],
        cwd=clone,
        env=env,
    )
    (output / "translation-source.json").write_text(
        json.dumps(
            {
                "locale": locale,
                "repository": args.upstream_url,
                "commit": commit,
                "ref": (ROOT / "UPSTREAM_REF").read_text().strip(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"{locale} site:", output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
