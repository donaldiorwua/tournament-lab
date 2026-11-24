

def validate_league(teams, fixtures):
    """
    Validate teams and fixtures before processing a league.

    Team rules:
    - Teams must be provided as a list.
    - League must contain between 4 and 8 teams.
    - Every team must be a dictionary.
    - Every team must have an ID and name.
    - Team IDs must be unique.
    - Team names must contain 2-30 characters.
    - Team names must be unique (case-insensitive).

    Fixture rules:
    - Fixtures must be provided as a list.
    - Every fixture must be a dictionary.
    - Every fixture must have the required fields.
    - Fixture IDs must be unique.
    - Every fixture must reference existing teams.
    - A team cannot play against itself.
    - Each pair of teams can only play once.
    - Status must be exactly 'played' or 'pending'.
    - Played fixtures must have non-negative integer scores.
    - Pending fixtures must have both scores set to None.
    """

    # Required fields
    team_fields = {"id", "name"}

    fixture_fields = {
        "id",
        "home_id",
        "away_id",
        "status",
        "home_score",
        "away_score"
    }

    # Validate collection types
    if not isinstance(teams, list):
        raise ValueError("Teams must be provided as a list.")

    if not isinstance(fixtures, list):
        raise ValueError("Fixtures must be provided as a list.")

    # Validate number of teams
    if len(teams) < 4 or len(teams) > 8:
        raise ValueError(
            "A league must contain between 4 and 8 teams."
        )

    team_ids = set()
    team_names = set()
    fixture_ids = set()
    team_pairs = set()

    # --------------------------------------------------
    # Validate teams
    # --------------------------------------------------

    for index, team in enumerate(teams):

        if not isinstance(team, dict):
            raise ValueError(
                f"Team at index {index} must be a dictionary."
            )

        # Check required fields
        missing_fields = team_fields - team.keys()

        if missing_fields:
            raise ValueError(
                f"Team at index {index} is missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )

        team_id = team["id"]
        team_name = team["name"]

        # Validate team ID
        if not isinstance(team_id, str) or not team_id.strip():
            raise ValueError(
                f"Invalid team ID at index {index}."
            )

        if team_id in team_ids:
            raise ValueError(
                f"Duplicate team ID: {team_id}"
            )

        team_ids.add(team_id)

        # Validate team name
        if not isinstance(team_name, str):
            raise ValueError(
                f"Team name for {team_id} must be a string."
            )

        if not 2 <= len(team_name.strip()) <= 30:
            raise ValueError(
                f"Team name must contain between 2 and 30 "
                f"characters: {team_name!r}"
            )

        normalized_name = team_name.strip().casefold()

        if normalized_name in team_names:
            raise ValueError(
                f"Duplicate team name: {team_name}"
            )

        team_names.add(normalized_name)

    # --------------------------------------------------
    # Validate fixtures
    # --------------------------------------------------

    for index, fixture in enumerate(fixtures):

        if not isinstance(fixture, dict):
            raise ValueError(
                f"Fixture at index {index} must be a dictionary."
            )

        # Check required fields
        missing_fields = fixture_fields - fixture.keys()

        if missing_fields:
            raise ValueError(
                f"Fixture at index {index} is missing fields: "
                f"{', '.join(sorted(missing_fields))}"
            )

        fixture_id = fixture["id"]
        home_id = fixture["home_id"]
        away_id = fixture["away_id"]
        status = fixture["status"]

        # Validate fixture ID
        if not isinstance(fixture_id, str) or not fixture_id.strip():
            raise ValueError(
                f"Invalid fixture ID at index {index}."
            )

        if fixture_id in fixture_ids:
            raise ValueError(
                f"Duplicate fixture ID: {fixture_id}"
            )

        fixture_ids.add(fixture_id)

        # Validate team references
        if home_id not in team_ids:
            raise ValueError(
                f"Unknown home team ID: {home_id}"
            )

        if away_id not in team_ids:
            raise ValueError(
                f"Unknown away team ID: {away_id}"
            )

        # Prevent a team playing itself
        if home_id == away_id:
            raise ValueError(
                f"Team cannot play against itself: {home_id}"
            )

        # Check duplicate pairings regardless of home/away order
        team_pair = frozenset((home_id, away_id))

        if team_pair in team_pairs:
            raise ValueError(
                f"Duplicate fixture pairing: {home_id} vs {away_id}"
            )

        team_pairs.add(team_pair)

        # Validate fixture status
        if status not in ("played", "pending"):
            raise ValueError(
                f"Invalid fixture status: {status!r}"
            )

        home_score = fixture["home_score"]
        away_score = fixture["away_score"]

        if status == "played":

            # bool is a subclass of int, so use type(...) is int
            if (
                type(home_score) is not int
                or type(away_score) is not int
                or home_score < 0
                or away_score < 0
            ):
                raise ValueError(
                    f"Invalid scores in fixture {fixture_id}. "
                    "Scores must be non-negative integers."
                )

def calculate_standings(teams, fixtures):
    """
    Calculate league statistics for all teams.

    Record keys:
    id, name, played, wins, draws, losses,
    goals_for, goals_against, goal_difference, points.

    Only played fixtures contribute to standings.
    """

    # Validate all league data first
    validate_league(teams, fixtures)

    standings = {}

    # Initialize standings
    for team in teams:
        team_id = team["id"]

        standings[team_id] = {
            "id": team_id,
            "name": team["name"],
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0
        }

    # Process played fixtures
    for fixture in fixtures:

        if fixture["status"] != "played":
            continue

        home = standings[fixture["home_id"]]
        away = standings[fixture["away_id"]]

        home_score = fixture["home_score"]
        away_score = fixture["away_score"]

        # Update matches played
        home["played"] += 1
        away["played"] += 1

        # Update goals
        home["goals_for"] += home_score
        home["goals_against"] += away_score

        away["goals_for"] += away_score
        away["goals_against"] += home_score

        # Determine match outcome
        if home_score > away_score:

            home["wins"] += 1
            away["losses"] += 1
            home["points"] += 3

        elif home_score < away_score:

            away["wins"] += 1
            home["losses"] += 1
            away["points"] += 3

        else:

            home["draws"] += 1
            away["draws"] += 1

            home["points"] += 1
            away["points"] += 1

    # Calculate goal difference
    for team in standings.values():
        team["goal_difference"] = (
            team["goals_for"] - team["goals_against"]
        )

    return list(standings.values())


def rank_standings(standings):
    """
    Rank teams by:
    1. Points descending
    2. Goal difference descending
    3. Goals for descending
    4. Team name case-insensitive ascending
    """
    ranked = {}
    ranked = sorted(
        standings,
        key=lambda team: (
            -team["points"],
            -team["goal_difference"],
            -team["goals_for"],
            team["name"].casefold()
        )
    )

    for position, team in enumerate(ranked, start=1):
        team["position"] = position

    return ranked
