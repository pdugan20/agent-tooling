from __future__ import annotations

import unittest
from unittest import mock

import validate_repository


class RepositoryValidationTests(unittest.TestCase):
    def test_current_repository_is_valid(self) -> None:
        validate_repository.validate_repository()

    def test_release_tag_must_match_manifest(self) -> None:
        with mock.patch.object(validate_repository, "plugin_version", return_value="1.2.3"):
            self.assertEqual(
                validate_repository.validate_release_tag("patrick-delivery-v1.2.3"),
                "1.2.3",
            )
            with self.assertRaisesRegex(validate_repository.ValidationError, "does not match"):
                validate_repository.validate_release_tag("patrick-delivery-v1.2.4")

    def test_release_tag_rejects_other_namespaces(self) -> None:
        with self.assertRaisesRegex(validate_repository.ValidationError, "must use"):
            validate_repository.validate_release_tag("v0.2.0")


if __name__ == "__main__":
    unittest.main()
