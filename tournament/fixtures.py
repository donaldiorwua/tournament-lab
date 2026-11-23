 
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
        ValueError: If the number of teams is outside the range of 4–8,
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