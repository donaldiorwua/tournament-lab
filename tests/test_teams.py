
import unittest
import copy

from tournament.teams import (
    normalize_name,
    add_team,
    create_team_id,
    name_key
)

class TestRegistration(unittest.TestCase):

    def setUp(self):
        self.teams = []
        add_team(self.teams, "Existing Team")

    # 1. Test name normalization
    def test_name_is_trimmed_preserving_capitalization(self):
        result = normalize_name("  Red Comets  ")

        self.assertEqual(result, "Red Comets")

    def test_whitespace_only_name_raises_value_error(self):
        teams_before = copy.deepcopy(self.teams)

        with self.assertRaises(ValueError):
            add_team(self.teams, "     ")

        self.assertEqual(self.teams, teams_before)

    # 2. Test successful team registration
    def test_add_team_successfully(self):
        teams = []

        result = add_team(teams, "Red Comets")

        self.assertEqual(
            result,
            {"id": "TM001", "name": "Red Comets"}
        )
        self.assertEqual(
            teams,
            [{"id": "TM001", "name": "Red Comets"}]
        )

    def test_second_team_gets_next_id(self):
        teams = []

        add_team(teams, "Red Comets")
        result = add_team(teams, "Blue Stars")

        self.assertEqual(
            result,
            {"id": "TM002", "name": "Blue Stars"}
        )

    # 3. Test duplicate team names
    def test_duplicate_name_raises_value_error(self):
        add_team(self.teams, "Red Comets")
        teams_before = copy.deepcopy(self.teams)

        with self.assertRaises(ValueError):
            add_team(self.teams, "red comets")

        self.assertEqual(self.teams, teams_before)

    # 4. Test name length boundaries
    def test_name_length_validation(self):
        invalid_names = ["A", "A" * 31]

        for name in invalid_names:
            with self.subTest(name=name):
                teams_before = copy.deepcopy(self.teams)

                with self.assertRaises(ValueError):
                    add_team(self.teams, name)

                self.assertEqual(self.teams, teams_before)

        # Exactly 2 and 30 characters should be accepted
        add_team(self.teams, "AB")
        add_team(self.teams, "A" * 30)

        self.assertEqual(len(self.teams), 3)

    # 5. Test length validation after trimming
    def test_name_length_after_trimming(self):
        # Raw length is 3, trimmed length is 1: reject
        teams_before = copy.deepcopy(self.teams)

        with self.assertRaises(ValueError):
            add_team(self.teams, " A ")

        self.assertEqual(self.teams, teams_before)

        # Raw length is 32, trimmed length is 30: accept
        name = " " + "A" * 30 + " "
        result = add_team(self.teams, name)

        self.assertEqual(result["name"], "A" * 30)

    # 6. Test non-string names
    def test_non_string_name_raises_type_error(self):
        invalid_names = [123, None, [], True]

        for name in invalid_names:
            with self.subTest(name=name):
                teams_before = copy.deepcopy(self.teams)

                with self.assertRaises(TypeError):
                    add_team(self.teams, name)

                self.assertEqual(self.teams, teams_before)

    # 7. Test invalid teams collection
    def test_non_list_teams_raises_type_error(self):
        teams = "not a list"

        with self.assertRaises(TypeError):
            add_team(teams, "Red Comets")

        self.assertEqual(teams, "not a list")

    # 8. Test maximum team limit
    def test_ninth_team_raises_value_error(self):
        teams = []

        for i in range(8):
            add_team(teams, f"Team {i:02d}")

        teams_before = copy.deepcopy(teams)

        with self.assertRaises(ValueError):
            add_team(teams, "Ninth Team")

        self.assertEqual(teams, teams_before)

    # 9. Test team ID generation with gaps
    def test_create_team_id_with_gaps(self):
        teams = [
            {"id": "TM001", "name": "A"},
            {"id": "TM004", "name": "B"}
        ]

        self.assertEqual(create_team_id(teams), "TM005")

    def test_create_team_id_empty_list(self):
        self.assertEqual(create_team_id([]), "TM001")

    # 10. Test name_key
    def test_name_key_case_insensitive(self):
        self.assertEqual(
            name_key("Red Comets"),
            name_key("red comets")
        )

    # 11. Optional Unicode casefolding test
    def test_unicode_casefold_duplicate(self):
        add_team(self.teams, "Straße FC")
        teams_before = copy.deepcopy(self.teams)

        with self.assertRaises(ValueError):
            add_team(self.teams, "STRASSE FC")

        self.assertEqual(self.teams, teams_before)


if __name__ == "__main__":
    unittest.main()
