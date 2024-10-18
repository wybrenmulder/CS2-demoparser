from player_stats import PlayerStats


def calculate_kast(player_stats: PlayerStats) -> float:
    """
    Calculate KAST (Kill, Assist, Survived, Trade) percentage.
    KAST is defined as (Kills + Assists + Survived + Traded deaths) / Total rounds played
    """
    total_kast_events = (
        player_stats.kills +
        player_stats.assists +
        player_stats.saves  # Include only saves for simplicity
    )
    
    if player_stats.rounds > 0:
        return total_kast_events / player_stats.rounds
    return 0.0


def calculate_impact(player_stats: PlayerStats) -> float:
    if player_stats.rounds > 0:
        return (player_stats.kills + player_stats.assists) / player_stats.rounds
    return 0.0


def calculate_hltv_rating(player_stats: PlayerStats) -> float:
    kast = calculate_kast(player_stats)
    kpr = player_stats.kills / player_stats.rounds if player_stats.rounds > 0 else 0
    dpr = player_stats.deaths / player_stats.rounds if player_stats.rounds > 0 else 0
    impact = calculate_impact(player_stats)
    adr = player_stats.damage / player_stats.rounds if player_stats.rounds > 0 else 0
    
    rating = (
        (0.0073 * kast) +
        (0.3591 * kpr) +
        (-0.5329 * dpr) +
        (0.2372 * impact) +
        (0.0032 * adr) +
        (0.1587)
    )
    
    return rating
