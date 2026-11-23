import unittest
from copy import deepcopy

from tournament.fixtures import generate_fixtures


class TestGenerateFixtures(unittest.TestCase):

    def setUp(self):
        self.teams_3 = [
            {"id": f"TM{i:03d}", "name": f"Team {i}"}
            for i in range(1, 4)
        ]

        self.teams_4 = [
            {"id": f"TM{i:03d}", "name": f"Team {i}"}
            for i in range(1, 5)
        ]

        self.teams_5 = [
            {"id": f"TM{i:03d}", "name": f"Team {i}"}
            for i in range(1, 6)
        ]

        self.teams_6 = [
            {"id": f"TM{i:03d}", "name": f"Team {i}"}
            for i in range(1, 7)
        ]

        self.teams_7 = [
            {"id": f"TM{i:03d}", "name": f"Team {i}"}
            for i in range(1, 8)
        ]

        self.teams_8 = [
            {"id": f"TM{i:03d}", "name": f"Team {i}"}
            for i in range(1, 9)
        ]

        self.teams_9 = [
            {"id": f"TM{i:03d}", "name": f"Team {i}"}
            for i in range(1, 10)
        ]

    # 1. Four teams should produce 6 fixtures
    def test_four_teams_produce_six_fixtures(self):
        fixtures = generate_fixtures(self.teams_4)
        self.assertEqual(len(fixtures), 6)

    # 2. Six teams should produce 15 fixtures
    def test_six_teams_produce_fifteen_fixtures(self):
        fixtures = generate_fixtures(self.teams_6)
        self.assertEqual(len(fixtures), 15)

    # 3. Eight teams should produce 28 fixtures
    def test_eight_teams_produce_twenty_eight_fixtures(self):
        fixtures = generate_fixtures(self.teams_8)
        self.assertEqual(len(fixtures), 28)

    # 4. No unordered pair should repeat
    def test_no_unordered_pair_repeats(self):
        fixtures = generate_fixtures(self.teams_4)

        pairs = [
            frozenset((
                fixture["home_id"],
                fixture["away_id"]
            ))
            for fixture in fixtures
        ]

        self.assertEqual(len(pairs), len(set(pairs)))

    # 5. Every team appears in exactly N-1 fixtures
    def test_every_team_appears_n_minus_one_times(self):
        fixtures = generate_fixtures(self.teams_4)

        for team in self.teams_4:
            appearances = sum(
                1 for fixture in fixtures
                if fixture["home_id"] == team["id"]
                or fixture["away_id"] == team["id"]
            )

            self.assertEqual(
                appearances,
                len(self.teams_4) - 1
            )

    # 6. Fixture IDs must be unique and sequential from M001
    def test_ids_are_unique_and_sequential(self):
        fixtures = generate_fixtures(self.teams_4)

        expected_ids = [
            f"M{i:03d}"
            for i in range(1, len(fixtures) + 1)
        ]

        actual_ids = [
            fixture["id"]
            for fixture in fixtures
        ]

        self.assertEqual(actual_ids, expected_ids)
        self.assertEqual(len(actual_ids), len(set(actual_ids)))

    # 7. Every fixture starts with pending status and None scores
    def test_fixtures_have_initial_pending_status(self):
        fixtures = generate_fixtures(self.teams_4)

        for fixture in fixtures:
            self.assertEqual(fixture["status"], "pending")
            self.assertIsNone(fixture["home_score"])
            self.assertIsNone(fixture["away_score"])

    # 8. Same input should produce identical output
    def test_fixture_generation_is_deterministic(self):
        first_result = generate_fixtures(self.teams_4)
        second_result = generate_fixtures(self.teams_4)

        self.assertEqual(first_result, second_result)

    # 9. Three teams should raise ValueError
    def test_three_teams_raise_value_error(self):
        with self.assertRaises(ValueError):
            generate_fixtures(self.teams_3)

    # 10. Nine teams should raise ValueError
    def test_nine_teams_raise_value_error(self):
        with self.assertRaises(ValueError):
            generate_fixtures(self.teams_9)

    # 11. Non-list input should raise TypeError
    def test_non_list_input_raises_type_error(self):
        invalid_inputs = (
            "teams",
            {"id": "TM001"},
            123,
            None,
            ({"id": "TM001"},)
        )

        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                with self.assertRaises(TypeError):
                    generate_fixtures(invalid_input)

    # 12. Non-dictionary items should raise TypeError
    def test_non_dict_items_raise_type_error(self):
        invalid_teams = [
            {"id": "TM001", "name": "Team 1"},
            "Team 2",
            {"id": "TM003", "name": "Team 3"},
            {"id": "TM004", "name": "Team 4"}
        ]

        with self.assertRaises(TypeError):
            generate_fixtures(invalid_teams)

    # 13. Valid input list should not be modified
    def test_valid_input_list_is_not_modified(self):
        teams = deepcopy(self.teams_4)
        original_teams = deepcopy(teams)

        generate_fixtures(teams)

        self.assertEqual(teams, original_teams)

    # 14. Invalid input list should not be modified after an error
    def test_invalid_input_list_is_not_modified(self):
        teams = deepcopy(self.teams_3)
        original_teams = deepcopy(teams)

        with self.assertRaises(ValueError):
            generate_fixtures(teams)

        self.assertEqual(teams, original_teams)

    # 15. A fixture must never pair a team with itself
    def test_no_team_is_paired_with_itself(self):
        fixtures = generate_fixtures(self.teams_4)

        for fixture in fixtures:
            self.assertNotEqual(
                fixture["home_id"],
                fixture["away_id"]
            )

    # 16. Duplicate team IDs should raise ValueError
    # The original input list must remain unchanged.
    def test_duplicate_team_ids_raise_value_error(self):
        teams = deepcopy(self.teams_4)
        teams[3]["id"] = teams[0]["id"]

        original_teams = deepcopy(teams)

        with self.assertRaises(ValueError):
            generate_fixtures(teams)

        self.assertEqual(teams, original_teams)

    # 17. A team dictionary without an ID should raise ValueError
    def test_missing_team_id_raises_value_error(self):
        teams = deepcopy(self.teams_4)
        del teams[1]["id"]

        original_teams = deepcopy(teams)

        with self.assertRaises(ValueError):
            generate_fixtures(teams)

        self.assertEqual(teams, original_teams)

    # 18. Every fixture must reference IDs from the supplied teams
    def test_fixture_team_ids_belong_to_input_teams(self):
        fixtures = generate_fixtures(self.teams_4)

        valid_team_ids = {
            team["id"] for team in self.teams_4
        }

        for fixture in fixtures:
            with self.subTest(fixture=fixture["id"]):
                self.assertIn(fixture["home_id"], valid_team_ids)
                self.assertIn(fixture["away_id"], valid_team_ids)

    # 19. First fixture must have the exact expected structure and values
    def test_first_fixture_has_exact_expected_values(self):
        fixtures = generate_fixtures(self.teams_4)

        expected_first_fixture = {
            "id": "M001",
            "home_id": "TM001",
            "away_id": "TM002",
            "status": "pending",
            "home_score": None,
            "away_score": None
        }

        self.assertEqual(fixtures[0], expected_first_fixture)

    def test_five_and_seven_teams_are_valid(self):
        cases = [(self.teams_5, 10), (self.teams_7, 21)]
        for teams, expected in cases:
            with self.subTest(teams=len(teams)):
                self.assertEqual(len(generate_fixtures(teams)), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
