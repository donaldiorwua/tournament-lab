
MIN_NAME_LEN = 2
MAX_NAME_LEN = 30
MAX_TEAMS = 8

def normalize_name(raw_team_name):
    if not isinstance(raw_team_name, str):
        raise TypeError("Team_name must be string")
    cleaned_team_name = raw_team_name.strip()
    if len(cleaned_team_name) < MIN_NAME_LEN or len(cleaned_team_name) > MAX_NAME_LEN:
        raise ValueError("Team_name must no be less than 2 and more than 30 characters")

    return cleaned_team_name

def name_key(name):
    striped_name = name.strip()
    return striped_name.casefold()

def create_team_id(teams):
    numbers = [
        int(team["id"][2:])
        for team in teams
        if team["id"].startswith("TM") and team["id"][2:].isdigit()
    ]
    return f"TM{max(numbers, default=0) + 1:03d}"

def add_team(teams, raw_team_name):
    if not isinstance(teams, list):
        raise TypeError("Teams must be a list of team dictionaries")
    display_name = normalize_name(raw_team_name)
    if len(teams) >= MAX_TEAMS:
        raise ValueError("Cannot register more than 8 teams")
    new_key = name_key(display_name)
    for team in teams:
        if name_key(team["name"]) == new_key:
            raise ValueError("A team with that name already exists")
    new_team = {"id": create_team_id(teams), "name": display_name}
    teams.append(new_team)
    return new_team