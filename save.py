import hltv_rating
import main


def get_players_by_team():
    """Fetch and separate players into T-side and CT-side based on current team info."""
    df_player_info = main.demo.parse_player_info()
    
    players_on_t_side = []
    players_on_ct_side = []

    for _, player in df_player_info.iterrows():
        if player["team"] == "T":
            players_on_t_side.append(player["name"])
        elif player["team"] == "CT":
            players_on_ct_side.append(player["name"])

    return players_on_t_side, players_on_ct_side


def check_for_saves():
    """
    Check if players save their loadout at the end of the round.
    A save occurs if:
    - T-side: The player doesn't plant the bomb and stays alive.
    - CT-side: The player doesn't defuse the bomb and stays alive.
    """
    df_round_end = main.demo.parse_event("round_end")  # Parse round end events
    df_bomb_plant = main.demo.parse_event("bomb_planted")  # Parse bomb plant events
    df_bomb_defuse = main.demo.parse_event("bomb_defused")  # Parse bomb defuse events

    for [_, round_info] in df_round_end.iterrows():
        winning_side = round_info["winner"]  # Who won the round (CT or T)
        surviving_players = round_info["surviving_players"]  # Players still alive at the end

        # Get player teams for this round
        players_on_t_side, players_on_ct_side = get_players_by_team()

        bomb_planted = any(df_bomb_plant["round"] == round_info["round"])  # Was bomb planted this round?
        bomb_defused = any(df_bomb_defuse["round"] == round_info["round"])  # Was bomb defused this round?

        # Check for T-side saves
        if winning_side == "CT" and not bomb_planted:  # CT won but bomb wasn't planted
            for player in surviving_players:
                if player in players_on_t_side:  # Check if player is a T
                    print(f"{player} on T-side saved (didn't plant bomb, stayed alive).")
                    hltv_rating.add_save(player)  # Optional: Add save info to HLTV rating

        # Check for CT-side saves
        if winning_side == "T" and bomb_planted and not bomb_defused:  # T won by bomb explosion, no defuse
            for player in surviving_players:
                if player in players_on_ct_side:  # Check if player is a CT
                    print(f"{player} on CT-side saved (didn't defuse bomb, stayed alive).")
                    hltv_rating.add_save(player)  # Optional: Add save info to HLTV rating
