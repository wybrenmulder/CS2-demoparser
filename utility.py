def utility_damage(parser):
    # Get the damage data from the demo
    df_player_hurt = parser.parse_event("player_hurt")

    # Initialize dictionaries to hold damage totals
    he_damage_totals = {}
    molotov_damage_totals = {}
    all_players = set()  # To collect unique players

    # Loop through the data to collect damage totals
    for _, row in df_player_hurt.iterrows():
        # Get attacker name
        attacker = row["attacker_name"]

        # If attacker is None, skip the row
        if attacker is None or not attacker:
            continue

        weapon = row["weapon"]
        damage = row["dmg_health"]

        all_players.add(attacker)

        # Aggregate HE grenade damage
        if weapon == "hegrenade":
            if attacker not in he_damage_totals:
                he_damage_totals[attacker] = 0
            he_damage_totals[attacker] += damage

        # Aggregate Molotov damage
        elif weapon in {"molotov", "inferno"}:
            if attacker not in molotov_damage_totals:
                molotov_damage_totals[attacker] = 0
            molotov_damage_totals[attacker] += damage

    # Prepare the final output
    utility_damage = []
    for player in all_players:
        he_damage = he_damage_totals.get(player, 0)
        molotov_damage = molotov_damage_totals.get(player, 0)
        utility_damage_amount = he_damage + molotov_damage

        utility_damage.append(
            {
                "player": player,
                "he_damage": he_damage,
                "molotov_damage": molotov_damage,
                "utility_damage": utility_damage_amount,
            }
        )

    utility_damage = [
        {
            "player": player,
            "he_damage": he_damage_totals.get(player, 0),
            "molotov_damage": molotov_damage_totals.get(player, 0),
            "utility_damage": he_damage_totals.get(player, 0)
            + molotov_damage_totals.get(player, 0),
        }
        for player in all_players
    ]

    return utility_damage
