
import unittest
from copy import deepcopy

from tournament.fixtures import record_score


class TestUpdateFixture(unittest.TestCase):

    def setUp(self):
        """Create fresh fixtures before every test."""
        self.fixtures = [
            {
                "id": "M001",
                "home_id": "TM005",
                "away_id": "TM006",
                "home_score": None,
                "away_score": None,
                "status": "pending"
            },
            {
                "id": "M002",
                "home_id": "TM001",
                "away_id": "TM002",
                "home_score": None,
                "away_score": None,
                "status": "pending"
            },
            {
                "id": "M003",
                "home_id": "TM003",
                "away_id": "TM004",
                "home_score": None,
                "away_score": None,
                "status": "pending"
            }
        ]

    # 1. Valid fixture update
    def test_valid_score_updates_fixture(self):
        result = record_score(self.fixtures, "M001", 2, 1)

        self.assertEqual(result["home_score"], 2)
        self.assertEqual(result["away_score"], 1)
        self.assertEqual(result["status"], "played")

    # 2. Prevent scoring a fixture twice
    def test_second_score_is_rejected(self):
        record_score(self.fixtures, "M001", 2, 1)

        original_result = deepcopy(self.fixtures)

        with self.assertRaises(ValueError):
            record_score(self.fixtures, "M001", 3, 2)

        self.assertEqual(self.fixtures, original_result)

    # 3. Unknown fixture ID
    def test_unknown_fixture_id_is_rejected(self):
        original = deepcopy(self.fixtures)

        with self.assertRaises(ValueError):
            record_score(self.fixtures, "M999", 2, 1)

        self.assertEqual(self.fixtures, original)

    # 4. Negative scores
    def test_negative_scores_are_rejected(self):
        invalid_scores = [
            (-1, 2),
            (2, -1),
            (-1, -1)
        ]

        for home, away in invalid_scores:
            with self.subTest(home=home, away=away):
                original = deepcopy(self.fixtures)

                with self.assertRaises(ValueError):
                    record_score(self.fixtures, "M001", home, away)

                self.assertEqual(self.fixtures, original)

    # 5. Boolean scores
    def test_boolean_scores_are_rejected(self):
        invalid_scores = [
            (True, 2),
            (False, 2),
            (2, True),
            (2, False),
            (True, False)
        ]

        for home, away in invalid_scores:
            with self.subTest(home=home, away=away):
                original = deepcopy(self.fixtures)

                with self.assertRaises(TypeError):
                    record_score(self.fixtures, "M001", home, away)

                self.assertEqual(self.fixtures, original)

    # 6. Floats, strings and None
    def test_non_integer_scores_are_rejected(self):
        invalid_values = [2.5, "3", None]

        for value in invalid_values:
            with self.subTest(value=value):

                # Invalid home score
                original = deepcopy(self.fixtures)

                with self.assertRaises(TypeError):
                    record_score(self.fixtures, "M001", value, 2)

                self.assertEqual(self.fixtures, original)

                # Invalid away score
                original = deepcopy(self.fixtures)

                with self.assertRaises(TypeError):
                    record_score(self.fixtures, "M001", 2, value)

                self.assertEqual(self.fixtures, original)

    # 7. No partial updates
    def test_invalid_away_score_leaves_both_scores_unchanged(self):
        with self.assertRaises(TypeError):
            record_score(self.fixtures, "M001", 3, True)

        fixture = self.fixtures[0]

        self.assertIsNone(fixture["home_score"])
        self.assertIsNone(fixture["away_score"])
        self.assertEqual(fixture["status"], "pending")

    # 8. Zero-zero score
    def test_zero_zero_score_is_accepted(self):
        result = record_score(self.fixtures, "M001", 0, 0)

        self.assertEqual(result["home_score"], 0)
        self.assertEqual(result["away_score"], 0)
        self.assertEqual(result["status"], "played")

    # 9. Other fixtures remain unchanged
    def test_updating_one_fixture_does_not_change_others(self):
        original_second = deepcopy(self.fixtures[1])
        original_third = deepcopy(self.fixtures[2])

        record_score(self.fixtures, "M001", 2, 1)

        self.assertEqual(self.fixtures[1], original_second)
        self.assertEqual(self.fixtures[2], original_third)

    # 10. Return the updated fixture
    def test_updated_fixture_is_returned(self):
        result = record_score(self.fixtures, "M001", 2, 1)

        self.assertIs(result, self.fixtures[0])

    # 11. Empty fixtures list
    def test_empty_fixtures_list_is_rejected(self):
        with self.assertRaises(ValueError):
            record_score([], "M001", 2, 1)

    # 12. Unexpected fixture status
    def test_cancelled_fixture_is_rejected(self):
        self.fixtures[0]["status"] = "cancelled"

        original = deepcopy(self.fixtures)

        with self.assertRaises(ValueError):
            record_score(self.fixtures, "M001", 2, 1)

        # Every record must remain unchanged.
        self.assertEqual(self.fixtures, original)

    # 13. Non-list fixtures input
    def test_non_list_fixtures_are_rejected(self):
        invalid_inputs = [
            None,
            {},
            "fixtures",
            123
        ]

        for invalid in invalid_inputs:
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    record_score(invalid, "M001", 2, 1)

    # 14. Non-dictionary fixture entries
    def test_non_dictionary_fixture_items_are_rejected(self):
        invalid_fixtures = [
            ["not a dictionary"],
            [None],
            [123],
            ["M001", "M002"]
        ]

        for invalid in invalid_fixtures:
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    record_score(invalid, "M001", 2, 1)


if __name__ == "__main__":
    unittest.main()
