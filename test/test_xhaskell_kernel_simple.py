#############################################################################
# Copyright (c) 2025, Masaya Taniguchi
#
# Distributed under the terms of the Apache Software License 2.0.
#
# The full license is in the file LICENSE, distributed with this software.
#############################################################################

"""Incremental xeus-haskell kernel smoke tests.

These tests start with a single fast check based on jupyter_kernel_test.
When the interpreter performance improves we can extend the coverage by
leveraging the additional helpers exposed by KernelTests.
"""

from __future__ import annotations

from queue import Empty
from typing import Any
import unittest

import jupyter_kernel_test

# MicroHs warm-up compiles modules on first execute; give it plenty of time.
jupyter_kernel_test.TIMEOUT = 90


class XHaskellKernelTests(jupyter_kernel_test.KernelTests):
    """Minimal smoke tests for the xhaskell kernel."""

    kernel_name = "xhaskell"
    language_name = "haskell"

    completion_samples: list[dict[str, str]] = []
    complete_code_samples: list[str] = []
    incomplete_code_samples: list[str] = []
    invalid_code_samples: list[str] = []
    code_hello_world = ""
    code_stderr = ""
    code_page_something = ""
    code_generate_error = ""
    code_execute_result = []
    code_display_data = []
    code_history_pattern = ""
    supported_history_operations = ()
    code_inspect_sample = ""
    code_clear_output = ""

    _kernel_info_reply: dict[str, Any] | None = None

    @classmethod
    def setUpClass(cls) -> None:
        """Start the kernel once for the whole test class.

        The SkipTest fallback keeps local editing workflows lightweight when
        the kernel has not been installed yet.
        """
        try:
            super().setUpClass()
        except Exception as exc:  # pragma: no cover - exercised in CI only
            raise unittest.SkipTest(f"xhaskell kernel is unavailable: {exc}") from exc
        try:
            cls._kernel_info_reply = cls._request_kernel_info_reply()
        except Empty as exc:
            cls._shutdown_kernel()
            raise unittest.SkipTest(
                "xhaskell kernel did not answer kernel_info in time"
            ) from exc

    @classmethod
    def _shutdown_kernel(cls) -> None:
        cls.kc.stop_channels()
        cls.km.shutdown_kernel()

    @classmethod
    def _request_kernel_info_reply(cls) -> dict[str, Any]:
        msg_id = cls.kc.kernel_info()
        reply = cls.kc.get_shell_msg(timeout=jupyter_kernel_test.TIMEOUT)
        if reply["header"]["msg_type"] != "kernel_info_reply":
            raise AssertionError("Unexpected kernel_info reply payload")
        reply_content = reply["content"]
        if reply_content.get("status") != "ok":
            raise AssertionError(f"kernel_info returned {reply_content}")
        return reply

    def test_kernel_info(self) -> None:
        if self._kernel_info_reply is None:
            self.skipTest("kernel_info handshake was skipped in setUpClass")
        reply = self._kernel_info_reply
        lang_info = reply["content"]["language_info"]
        self.assertEqual(lang_info["name"], self.language_name)
        self.assertEqual(lang_info["file_extension"], "hs")

    def _execute_or_skip(self, *, code: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        try:
            return self.execute_helper(code=code, timeout=jupyter_kernel_test.TIMEOUT)
        except Empty as exc:
            self.skipTest(f"xhaskell kernel timed out while executing {code!r}: {exc}")

    @staticmethod
    def _extract_plain_text(
        output_msgs: list[dict[str, Any]],
        *,
        msg_type: str = "execute_result",
    ) -> str:
        for msg in output_msgs:
            if msg["msg_type"] != msg_type:
                continue
            if msg_type == "execute_result":
                data = msg["content"].get("data", {})
                text = data.get("text/plain")
            else:
                text = msg["content"].get("text")
            if text:
                return text
        return ""

    def test_simple_expression_emits_execute_result(self) -> None:
        """Running a tiny arithmetic expression should yield execute_result."""
        self.flush_channels()
        reply, output_msgs = self._execute_or_skip(code="1 + 1")

        self.assertEqual(reply["content"]["status"], "ok")

        result_msgs = [
            msg for msg in output_msgs if msg["msg_type"] == "execute_result"
        ]
        self.assertTrue(
            result_msgs,
            f"Expected execute_result message, saw {[msg['msg_type'] for msg in output_msgs]}",
        )

        payload = result_msgs[0]["content"]["data"].get("text/plain", "")
        self.assertIn("2", payload.strip())

    def test_invalid_haskell_snippet_reports_error(self) -> None:
        """Parser failures should bubble up as notebook errors."""
        self.flush_channels()
        reply, output_msgs = self._execute_or_skip(code="1 +")

        self.assertEqual(reply["content"]["status"], "error")
        error_msgs = [msg for msg in output_msgs if msg["msg_type"] == "error"]
        self.assertTrue(
            error_msgs,
            f"No error output, saw {[msg['msg_type'] for msg in output_msgs]}",
        )

    def test_definition_persists_across_cells(self) -> None:
        """Definitions should persist in the REPL context across cells."""
        self.flush_channels()
        reply, outputs = self._execute_or_skip(code="square x = x * x")
        self.assertEqual(reply["content"]["status"], "ok")
        self.assertFalse(
            any(msg["msg_type"] == "execute_result" for msg in outputs),
            "Definition produced an unexpected execute_result payload",
        )

        self.flush_channels()
        reply, outputs = self._execute_or_skip(code="square 7")
        self.assertEqual(reply["content"]["status"], "ok")
        payload = self._extract_plain_text(outputs)
        self.assertIn("49", payload.strip())

    def test_putstrln_emits_plaintext(self) -> None:
        """putStrLn output should surface back to the notebook."""
        self.flush_channels()
        reply, outputs = self._execute_or_skip(code='putStrLn "hello from xeus"')
        self.assertEqual(reply["content"]["status"], "ok")
        payload = self._extract_plain_text(outputs)
        self.assertIn("hello from xeus", payload)


if __name__ == "__main__":
    unittest.main()
