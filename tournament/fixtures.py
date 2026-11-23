 
def generate_fixtures(teams):
    """
    Generate round-robin fixtures for a tournament.

    Each team plays against every other team exactly once.

    Args:
        teams (list): A list of team dictionaries. Each dictionary
            must contain a unique 'id' key.

    Returns:
        list: A list of fixture dictionaries containing:
            - id: Unique fixture ID (e.g. M001).
            - home_id: ID of the home team.
            - away_id: ID of the away team.
            - home_score: Initially None.
            - away_score: Initially None.
            - status: Initially 'pending'.

    Raises:
        TypeError: If teams is not a list or contains non-dictionary items.
        ValueError: If the number of teams is outside the range of 4-8,
            a team ID is missing, or duplicate team IDs are found.
    """
    fixtures = []
    count = 0

    if not isinstance(teams, list):
        raise TypeError("teams must be a list of dictionaries")

    if not all(isinstance(team, dict) for team in teams):
        raise TypeError("Each team must be a dictionary")

    if len(teams) < 4 or len(teams) > 8:
        raise ValueError("teams must be 4 and not more than 8")

    # Check that every team has an ID
    if not all("id" in team for team in teams):
        raise ValueError("Every team must have an ID")

    # Check for duplicate team IDs
    team_ids = [team["id"] for team in teams]

    if len(team_ids) != len(set(team_ids)):
        raise ValueError("Duplicate team IDs are not allowed")
   
    for index, home_team in enumerate(teams):
        for away_team in teams[index + 1:]:
            fixture_id = f"M{count + 1:03d}"
            count += 1

            fixture = {
                "id" : fixture_id,
                "home_id": home_team["id"],
                "away_id": away_team["id"],
                "home_score": None,
                "away_score": None,
                "status": "pending"
            }
            fixtures.append(fixture)
    
    return fixtures


def record_score(fixtures, fixture_id, home_score, away_score):
    """
    Record the result of a pending fixture.

    Finds a fixture by its ID, validates its status and scores,
    then updates both scores and changes its status to "played".

    All validations are performed before modifying the fixture
    to prevent partial updates or accidental changes.

    Args:
        fixtures (list): A list of fixture dictionaries.
        fixture_id (str): The unique ID of the fixture to update.
        home_score (int): The home team's final score.
        away_score (int): The away team's final score.

    Returns:
        dict: The updated fixture dictionary.

    Raises:
        TypeError: If fixtures is not a list, a fixture is not a
            dictionary, or either score is not an exact integer.
        ValueError: If the fixture ID does not exist, the fixture
            is not pending, or either score is negative.
    """
    if not isinstance(fixtures, list):
        raise TypeError("fixtures must be a list of dictionaries")

    if not all(isinstance(fixture, dict) for fixture in fixtures):
        raise TypeError("Each fixture must be a dictionary")
    
    if not all("id" in fixture for fixture in fixtures):
        raise ValueError("Every team must have an ID")
    
    if type(home_score) is not int or type(away_score) is not int:
        raise TypeError("score must be a valid integer, boolean values are not allowed")
    
    if home_score < 0 or away_score < 0:
        raise ValueError("negative scores are not allowed")
    
    fixture = None
    for match in fixtures:
        if match["id"] == fixture_id:
            fixture = match
            break

    if fixture is None:
        raise ValueError("fixture_id does not exist")
    
    if fixture["status"] == "played":
        raise ValueError("Fixture already played")
    
    if fixture["status"] != "pending":
        raise ValueError("only pending fixtures can be scored")
    
    fixture["home_score"] = home_score
    fixture["away_score"] = away_score
    fixture["status"] = "played"

    return fixture