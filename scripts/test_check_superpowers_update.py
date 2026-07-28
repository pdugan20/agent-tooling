from __future__ import annotations

import unittest
from unittest import mock

import check_superpowers_update


class SuperpowersUpdateCheckTests(unittest.TestCase):
    def test_reports_matching_upstream_as_current(self) -> None:
        with mock.patch.object(
            check_superpowers_update,
            "resolve_remote_commit",
            return_value="a" * 40,
        ):
            status = check_superpowers_update.build_status(
                {
                    "upstreamRepository": "https://example.com/upstream.git",
                    "upstreamCommit": "a" * 40,
                    "upstreamVersion": "6.2.0",
                    "forkVersion": "6.2.0-config.1",
                }
            )

        self.assertIs(status["outdated"], False)
        self.assertEqual(status["latestCommit"], "a" * 40)

    def test_reports_new_upstream_commit(self) -> None:
        with mock.patch.object(
            check_superpowers_update,
            "resolve_remote_commit",
            return_value="b" * 40,
        ):
            status = check_superpowers_update.build_status(
                {
                    "upstreamRepository": "https://example.com/upstream.git",
                    "upstreamCommit": "a" * 40,
                    "upstreamVersion": "6.2.0",
                    "forkVersion": "6.2.0-config.1",
                }
            )

        self.assertIs(status["outdated"], True)
        self.assertEqual(status["currentCommit"], "a" * 40)
        self.assertEqual(status["latestCommit"], "b" * 40)


if __name__ == "__main__":
    unittest.main()
