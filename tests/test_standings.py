
import unittest
from copy import deepcopy

from tournament.standings import (
    validate_league,
    calculate_standings,
    rank_standings
)


class BaseStandingsTest(unittest.TestCase):
    """Shared test data and fixture factory."""

    def setUp(self):
        self.teams = [
            {"id": "TM001", "name": "Arsenal"},
            {"id": "TM002", "name": "Chelsea"},
            {"id": "TM003", "name": "Liverpool"},
            {"id": "TM004", "name": "Everton"}
        ]

    def make_fixture(
        self,
        fixture_id="M001",
        home_id="TM001",
        away_id="TM002",
        status="played",
        home_score=2,
        away_score=1
    ):
        return {
            "id": fixture_id,
            "home_id": home_id,
            "away_id": away_id,
            "status": status,
            "home_score": home_score,
            "away_score": away_score
        }


# =====================================================
# VALIDATION TESTS
# =====================================================

class TestValidateLeague(BaseStandingsTest):

    def test_valid_league(self):
        validate_league(self.teams, [])

    def test_duplicate_team_ids_raise_error(self):
        teams = self.teams + [
            {"id": "TM001", "name": "Manchester United"}
        ]

        with self.assertRaises(ValueError):
            validate_league(teams, [])

    def test_duplicate_team_names_raise_error(self):
        teams = deepcopy(self.teams)
        teams[1]["name"] = "ARSENAL"

        with self.assertRaises(ValueError):
            validate_league(teams, [])

    def test_duplicate_fixture_ids_raise_error(self):
        fixtures = [
            self.make_fixture("M001"),
            self.make_fixture(
                fixture_id="M001",
                home_id="TM001",
                away_id="TM003"
            )
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_duplicate_team_pairing_raises_error(self):
        fixtures = [
            self.make_fixture("M001"),
            self.make_fixture(
                fixture_id="M002",
                home_id="TM002",
                away_id="TM001"
            )
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_team_cannot_play_against_itself(self):
        fixtures = [
            self.make_fixture(
                home_id="TM001",
                away_id="TM001"
            )
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_unknown_team_id_raises_error(self):
        fixtures = [
            self.make_fixture(away_id="TM999")
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_invalid_fixture_status_raises_error(self):
        fixtures = [
            self.make_fixture(status="Played")
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_none_home_score_raises_error(self):
        fixtures = [
            self.make_fixture(home_score=None)
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_negative_home_score_raises_error(self):
        fixtures = [
            self.make_fixture(home_score=-1)
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_negative_away_score_raises_error(self):
        fixtures = [
            self.make_fixture(away_score=-1)
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_boolean_score_raises_error(self):
        fixtures = [
            self.make_fixture(home_score=True)
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_string_score_raises_error(self):
        fixtures = [
            self.make_fixture(home_score="2")
        ]

        with self.assertRaises(ValueError):
            validate_league(self.teams, fixtures)

    def test_pending_fixture_with_stray_scores_is_valid(self):
        fixtures = [
            self.make_fixture(
                status="pending",
                home_score=5,
                away_score=3
            )
        ]

        validate_league(self.teams, fixtures)

    def test_invalid_team_count_raises_error(self):
        with self.assertRaises(ValueError):
            validate_league(self.teams[:3], [])

    def test_non_list_teams_raise_error(self):
        with self.assertRaises(ValueError):
            validate_league(None, [])

    def test_non_list_fixtures_raise_error(self):
        with self.assertRaises(ValueError):
            validate_league(self.teams, None)

    def test_missing_team_field_raises_error(self):
        teams = deepcopy(self.teams)
        del teams[0]["name"]

        with self.assertRaises(ValueError):
            validate_league(teams, [])

    def test_missing_fixture_field_raises_error(self):
        fixture = self.make_fixture()
        del fixture["status"]

        with self.assertRaises(ValueError):
            validate_league(self.teams, [fixture])


# =====================================================
# CALCULATION TESTS
# =====================================================

class TestCalculateStandings(BaseStandingsTest):

    def test_no_played_fixtures(self):
        standings = calculate_standings(self.teams, [])

        self.assertEqual(len(standings), 4)

        for team in standings:
            self.assertEqual(team["played"], 0)
            self.assertEqual(team["wins"], 0)
            self.assertEqual(team["draws"], 0)
            self.assertEqual(team["losses"], 0)
            self.assertEqual(team["goals_for"], 0)
            self.assertEqual(team["goals_against"], 0)
            self.assertEqual(team["goal_difference"], 0)
            self.assertEqual(team["points"], 0)

    def test_home_win_2_1(self):
        fixtures = [self.make_fixture()]

        standings = calculate_standings(
            self.teams, fixtures
        )

        arsenal = next(
            t for t in standings if t["id"] == "TM001"
        )

        chelsea = next(
            t for t in standings if t["id"] == "TM002"
        )

        self.assertEqual(arsenal["played"], 1)
        self.assertEqual(arsenal["wins"], 1)
        self.assertEqual(arsenal["goals_for"], 2)
        self.assertEqual(arsenal["goals_against"], 1)
        self.assertEqual(arsenal["goal_difference"], 1)
        self.assertEqual(arsenal["points"], 3)

        self.assertEqual(chelsea["played"], 1)
        self.assertEqual(chelsea["losses"], 1)
        self.assertEqual(chelsea["goals_for"], 1)
        self.assertEqual(chelsea["goals_against"], 2)
        self.assertEqual(chelsea["goal_difference"], -1)
        self.assertEqual(chelsea["points"], 0)

    def test_draw_awards_one_point_each(self):
        fixtures = [
            self.make_fixture(
                home_score=1,
                away_score=1
            )
        ]

        standings = calculate_standings(
            self.teams, fixtures
        )

        for team in standings:
            if team["id"] in ("TM001", "TM002"):
                self.assertEqual(team["played"], 1)
                self.assertEqual(team["draws"], 1)
                self.assertEqual(team["points"], 1)
                self.assertEqual(team["wins"], 0)
                self.assertEqual(team["losses"], 0)

    def test_draw_leaves_other_teams_untouched(self):
        fixtures = [
            self.make_fixture(
                home_score=1,
                away_score=1
            )
        ]

        standings = calculate_standings(
            self.teams, fixtures
        )

        untouched_teams = [
            team for team in standings
            if team["id"] in ("TM003", "TM004")
        ]

        for team in untouched_teams:
            self.assertEqual(team["played"], 0)
            self.assertEqual(team["wins"], 0)
            self.assertEqual(team["draws"], 0)
            self.assertEqual(team["losses"], 0)
            self.assertEqual(team["goals_for"], 0)
            self.assertEqual(team["goals_against"], 0)
            self.assertEqual(team["goal_difference"], 0)
            self.assertEqual(team["points"], 0)

    def test_pending_fixture_is_ignored(self):
        fixtures = [
            self.make_fixture(
                status="pending",
                home_score=5,
                away_score=3
            )
        ]

        standings = calculate_standings(
            self.teams, fixtures
        )

        for team in standings:
            self.assertEqual(team["played"], 0)
            self.assertEqual(team["wins"], 0)
            self.assertEqual(team["draws"], 0)
            self.assertEqual(team["losses"], 0)
            self.assertEqual(team["points"], 0)
            self.assertEqual(team["goals_for"], 0)
            self.assertEqual(team["goals_against"], 0)

    def test_unknown_team_id_raises_error(self):
        fixtures = [
            self.make_fixture(away_id="TM999")
        ]

        with self.assertRaises(ValueError):
            calculate_standings(self.teams, fixtures)

    def test_duplicate_fixture_does_not_award_points_twice(self):
        fixtures = [
            self.make_fixture("M001"),
            self.make_fixture(
                fixture_id="M002",
                home_id="TM001",
                away_id="TM002",
                home_score=3,
                away_score=0
            )
        ]

        with self.assertRaises(ValueError):
            calculate_standings(self.teams, fixtures)

    def test_inputs_are_unchanged(self):
        teams = deepcopy(self.teams)

        fixtures = [
            self.make_fixture()
        ]

        original_teams = deepcopy(teams)
        original_fixtures = deepcopy(fixtures)

        calculate_standings(teams, fixtures)

        self.assertEqual(teams, original_teams)
        self.assertEqual(fixtures, original_fixtures)

    def test_points_and_goals_invariants(self):
        fixtures = [
            self.make_fixture(
                "M001",
                "TM001",
                "TM002",
                home_score=2,
                away_score=1
            ),
            self.make_fixture(
                "M002",
                "TM001",
                "TM003",
                home_score=0,
                away_score=0
            ),
            self.make_fixture(
                "M003",
                "TM002",
                "TM003",
                home_score=3,
                away_score=1
            ),
            self.make_fixture(
                "M004",
                "TM003",
                "TM004",
                home_score=3,
                away_score=1
            )
        ]

        standings = calculate_standings(
            self.teams, fixtures
        )

        total_points = sum(
            team["points"] for team in standings
        )

        total_wins = sum(
            team["wins"] for team in standings
        )

        total_draws = sum(
            team["draws"] for team in standings
        )

        total_losses = sum(
            team["losses"] for team in standings
        )

        total_goals_for = sum(
            team["goals_for"] for team in standings
        )

        total_goals_against = sum(
            team["goals_against"] for team in standings
        )

        self.assertEqual(total_wins, total_losses)

        self.assertEqual(
            total_points,
            (3 * total_wins) + total_draws
        )

        self.assertEqual(
            total_goals_for,
            total_goals_against
        )


# =====================================================
# RANKING TESTS
# =====================================================

class TestRankStandings(unittest.TestCase):

    def setUp(self):
        self.standings = [
            {
                "id": "TM001",
                "name": "Zeta",
                "points": 7,
                "goal_difference": 4,
                "goals_for": 10
            },
            {
                "id": "TM002",
                "name": "alpha",
                "points": 7,
                "goal_difference": 4,
                "goals_for": 10
            },
            {
                "id": "TM003",
                "name": "Bravo",
                "points": 7,
                "goal_difference": 4,
                "goals_for": 10
            }
        ]

    def test_alphabetical_order_independent_of_registration(self):
        first = rank_standings(
            deepcopy(self.standings)
        )

        second = rank_standings(
            deepcopy(list(reversed(self.standings)))
        )

        expected = ["alpha", "Bravo", "Zeta"]

        self.assertEqual(
            [team["name"] for team in first],
            expected
        )

        self.assertEqual(
            [team["name"] for team in second],
            expected
        )

    def test_ranking_is_independent_of_shuffle(self):
        first = rank_standings(
            deepcopy(self.standings)
        )

        shuffled = [
            self.standings[1],
            self.standings[2],
            self.standings[0]
        ]

        second = rank_standings(
            deepcopy(shuffled)
        )

        self.assertEqual(
            [team["id"] for team in first],
            [team["id"] for team in second]
        )

    def test_positions_are_sequential(self):
        ranked = rank_standings(
            deepcopy(self.standings)
        )

        self.assertEqual(
            [team["position"] for team in ranked],
            [1, 2, 3]
        )


if __name__ == "__main__":
    unittest.main()
