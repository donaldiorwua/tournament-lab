 
def generate_fixtures(teams):
    fixtures = []
    count = 0

    if not isinstance(teams, list):
        raise TypeError("teams must be a list of dictionaries")
    if not all(isinstance(team, dict) for team in teams):
        raise TypeError("Each team must be a dictionary")
    if len(teams) < 4 or len(teams) > 8:
        raise ValueError("teams must be 4 and not more than 8")
   
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