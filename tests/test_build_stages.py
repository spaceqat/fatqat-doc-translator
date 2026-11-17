"""Regression checks for separate RTD commands and the original local CLI."""

from contextlib import ExitStack
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import inject_build
import translate


class BuildStageTests(unittest.TestCase):
    def test_locale_defaults_use_rtd_language_and_honor_custom_override(self):
        for environment, expected in (
            ({}, "zh"),
            ({"READTHEDOCS_LANGUAGE": "ko"}, "ko"),
            ({"READTHEDOCS_LANGUAGE": "zh-cn"}, "zh"),
            ({"READTHEDOCS_LANGUAGE": "en"}, "zh"),
            ({"READTHEDOCS_LANGUAGE": "ko", "FATQAT_LOCALE": "zh"}, "zh"),
        ):
            with self.subTest(environment=environment), patch.dict(
                "os.environ", environment, clear=True
            ):
                self.assertEqual(inject_build.default_locale(), expected)

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(translate.configure_locale, "zh")
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        (self.root / "UPSTREAM_COMMIT").write_text("abc123")
        (self.root / "UPSTREAM_REF").write_text("main")
        self.workdir = self.root / ".build"
        self.clone = self.workdir / "upstream"
        (self.clone / ".git").mkdir(parents=True)
        self.output = self.root / "site"
        self.output.mkdir()
        self.stack.enter_context(patch.object(inject_build, "ROOT", self.root))
        self.checkout = self.stack.enter_context(
            patch.object(inject_build, "checkout", return_value=self.clone)
        )
        self.stack.enter_context(patch.object(inject_build, "assert_snapshot"))
        self.revision = self.stack.enter_context(
            patch.object(inject_build.subprocess, "check_output", return_value="abc123\n")
        )
        self.run = self.stack.enter_context(patch.object(inject_build, "run"))
        self.stack.enter_context(patch.object(inject_build.shutil, "copytree"))
        self.stack.enter_context(patch.object(inject_build, "generate_config"))
        self.check = self.stack.enter_context(
            patch.object(translate, "run_check", return_value=0)
        )

    def invoke(self, stage=None):
        argv = ["inject_build.py", "--output", str(self.output), "--workdir",
                str(self.workdir), "--require-complete"]
        if stage:
            argv += ["--stage", stage]
        with patch.object(sys, "argv", argv), patch.dict(
            "os.environ", {"FATQAT_LOCALE": "ko"}
        ):
            return inject_build.main()

    def test_split_build_matches_default_and_keeps_korean_locale(self):
        self.assertEqual(self.invoke(), 0)
        full_commands = [call.args[0] for call in self.run.call_args_list]
        self.run.reset_mock()
        self.checkout.reset_mock()
        for stage in ("prepare", "tutorials", "english", "translated"):
            self.assertEqual(self.invoke(stage), 0)
        self.assertEqual(full_commands, [call.args[0] for call in self.run.call_args_list])
        self.checkout.assert_called_once()
        source = json.loads((self.output / "translation-source.json").read_text())
        self.assertEqual(source["locale"], "ko")
        self.assertIn("mkdocs.ko.yml", full_commands[-1])

    def test_failed_translation_check_stops_before_install_or_execution(self):
        self.check.return_value = 1
        self.assertEqual(self.invoke("prepare"), 1)
        self.checkout.assert_not_called()
        self.run.assert_not_called()

    def test_stale_checkout_is_rejected_before_later_stage(self):
        self.revision.return_value = "old-commit\n"
        with self.assertRaisesRegex(ValueError, "rerun --stage prepare"):
            self.invoke("translated")
        self.run.assert_not_called()

    def test_failed_tutorial_execution_stops_full_build(self):
        def execute(command, **kwargs):
            if "--execute-if-needed" in command:
                raise inject_build.subprocess.CalledProcessError(1, command)
        self.run.side_effect = execute
        with self.assertRaises(inject_build.subprocess.CalledProcessError):
            self.invoke()
        self.assertFalse(any("mkdocs" in call.args[0] for call in self.run.call_args_list))


if __name__ == "__main__":
    unittest.main()
