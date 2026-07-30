from __future__ import annotations

import unittest

import check_mcp_auth

POLICY = {
    "oauthRequired": ["expo", "Mintlify Admin"],
    "knownBlocked": {
        "sentry": {
            "issue": "https://example.com/upstream-issue",
            "reason": "Known OAuth incompatibility.",
        }
    },
    "noOAuthRequired": {
        "firebase": "Uses Firebase CLI authentication.",
    },
}


class McpAuthCheckTests(unittest.TestCase):
    def test_reports_expected_machine_state(self) -> None:
        checks, additional = check_mcp_auth.evaluate(
            [
                {"name": "expo", "auth_status": "o_auth"},
                {"name": "Mintlify Admin", "auth_status": "not_logged_in"},
                {"name": "sentry", "auth_status": "not_logged_in"},
                {"name": "firebase", "auth_status": "unsupported"},
                {"name": "openaiDeveloperDocs", "auth_status": "unsupported"},
            ],
            POLICY,
        )

        self.assertEqual(
            [(check.label, check.name, check.failure) for check in checks],
            [
                ("CONNECTED", "expo", False),
                ("NEEDS LOGIN", "Mintlify Admin", True),
                ("BLOCKED", "sentry", False),
                ("NO OAUTH", "firebase", False),
            ],
        )
        self.assertEqual(
            [(check.label, check.name) for check in additional],
            [("NO OAUTH", "openaiDeveloperDocs")],
        )

    def test_missing_expected_server_is_a_failure(self) -> None:
        checks, _ = check_mcp_auth.evaluate([], POLICY)

        self.assertTrue(all(check.failure for check in checks if check.label == "MISSING"))
        self.assertEqual(sum(check.label == "MISSING" for check in checks), 4)


if __name__ == "__main__":
    unittest.main()
