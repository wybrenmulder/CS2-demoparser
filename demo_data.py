from dataclasses import dataclass
from demoparser2 import DemoParser


@dataclass()  # init=True
class PlayerStats:
    steamid: int
    user_name: str
    team_number: int
    kills: int
    assists: int
    rounds: int
    deaths: int
    saves: int
    damage: int
    kd: float
    kpr: float
    apr: float
    adr: float
    impact: float
    kast: float
    hltv2: float
    trade_kill_opportunities: int
    trade_kill_attempts: int
    trade_kill_success: int
    traded_death_opportunities: int
    traded_death_attempts: int
    traded_death_success: int
    opd_attempts: float
    opd_success: float
    opd_traded: float
    opd_most_killed: str
    opd_best_weapon: str
    opd_most_died_to: str
    flash_assists: float
    enemies_flashed_per_flash: float
    teammates_flashed_per_flash: float
    avg_blind_time: float
    avg_he_dmg: float
    avg_he_team_dmg: float
    avg_unused_utility: int

    def __init__(self, steamid: int, player_name: str, team_number: int):
        self.steamid = steamid
        self.user_name = player_name
        self.team_number = team_number
        self.kills = 0
        self.assists = 0
        self.rounds = 0
        self.deaths = 0
        self.saves = 0
        self.damage = 0
        self.kd = 0.0
        self.kpr = 0.0
        self.apr = 0.0
        self.adr = 0.0
        self.impact = 0.0
        self.kast = 0.0
        self.hltv2 = 0.0
        self.trade_kill_opportunities = 0
        self.trade_kill_attempts = 0
        self.trade_kill_success = 0
        self.traded_death_opportunities = 0
        self.traded_death_attempts = 0
        self.traded_death_success = 0
        self.opd_attempts = 0.0
        self.opd_success = 0.0
        self.opd_traded = 0.0
        self.opd_most_killed = ""
        self.opd_best_weapon = ""
        self.opd_most_died_to = ""
        self.flash_assists = 0.0
        self.enemies_flashed_per_flash = 0.0
        self.teammates_flashed_per_flash = 0.0
        self.avg_blind_time = 0.0
        self.avg_he_dmg = 0.0
        self.avg_he_team_dmg = 0.0
        self.avg_unused_utility = 0


@dataclass
class DemoInfo:
    rounds: int
    tick_rate: int

    def __init__(self, parser):
        self.rounds = self.get_rounds(parser)
        self.tick_rate = 64

    def get_rounds(self, parser):
        round_end_events = parser.parse_event("round_end")
        round_count = len(round_end_events)

        return round_count


@dataclass
class PlayerStatsManager:
    players: dict[int, PlayerStats]

    def __init__(self, parser: DemoParser):
        # Dictionary to hold PlayerStats objects keyed by steamid
        self.players = {}

        # Parse player info at the start
        playerinfo = parser.parse_player_info()
        for _, player in playerinfo.iterrows():
            steamid = player["steamid"]
            username = player["name"]
            team_number = player["team_number"]

            # Create PlayerStats object for each player
            self.players[steamid] = PlayerStats(steamid, username, team_number)

    def process_player_deaths(self, parser: DemoParser):
        # Parse player_death events
        player_death_events = parser.parse_event("player_death")

        for _, death in player_death_events.iterrows():
            victim_steamid = int(death["user_steamid"])
            attacker_steamid = int(death["attacker_steamid"])

            # Update victim's death count
            if victim_steamid in self.players:
                self.players[victim_steamid].deaths += 1

            # Update attacker's kill count, but only if the attacker isn't the same as the victim (not a suicide)
            if attacker_steamid in self.players and attacker_steamid != victim_steamid:
                self.players[attacker_steamid].kills += 1

    def display_player_stats(self):
        print("Player Stats:")
        for stats in self.players.values():
            print(f"Player: {stats.user_name} (SteamID: {stats.steamid})")
            print(f"  Kills: {stats.kills}")
            print(f"  Deaths: {stats.deaths}")
            print("------------------------------")


@dataclass
class MatchStartAndEnd:
    begin_new_match: any
    round_announce_match_start: any
    round_announce_match_point: any
    round_announce_last_round_half: any

    def __init__(self, parser):
        self.begin_new_match = parser.parse_event("begin_new_match")
        self.round_announce_match_start = parser.parse_event(
            "round_announce_match_start"
        )
        self.round_announce_match_point = parser.parse_event(
            "round_announce_match_point"
        )
        self.round_announce_last_round_half = parser.parse_event(
            "round_announce_last_round_half"
        )
        self.round_poststart = parser.parse_event("round_poststart")
        self.round_prestart = parser.parse_event("round_prestart")
        self.round_officially_ended = parser.parse_event("round_officially_ended")
        self.cs_win_panel_match = parser.parse_event("cs_win_panel_match")
        self.round_time_warning = parser.parse_event("round_time_warning")
        self.round_freeze_end = parser.parse_event("round_freeze_end")


@dataclass
class MatchAnnouncementAndRestart:
    announce_phase_end: any
    cs_pre_restart: any
    hltv_versioninfo: any
    cs_round_start_beep: any
    cs_round_final_beep: any

    def __init__(self, parser):
        self.announce_phase_end = parser.parse_event("announce_phase_end")
        self.cs_pre_restart = parser.parse_event("cs_pre_restart")
        self.hltv_versioninfo = parser.parse_event("hltv_versioninfo")
        self.cs_round_start_beep = parser.parse_event("cs_round_start_beep")
        self.cs_round_final_beep = parser.parse_event("cs_round_final_beep")


@dataclass
class PlayerActions:
    weapon_fire: any
    weapon_reload: any
    weapon_zoom: any
    item_pickup: any
    item_equip: any

    def __init__(self, parser):
        self.weapon_fire = parser.parse_event("weapon_fire")
        self.weapon_reload = parser.parse_event("weapon_reload")
        self.weapon_zoom = parser.parse_event("weapon_zoom")
        self.item_pickup = parser.parse_event("item_pickup")
        self.item_equip = parser.parse_event("item_equip")


@dataclass
class PlayerMovements:
    player_footstep: any
    player_jump: any
    player_spawn: any
    player_disconnect: any
    player_connect: any
    player_connect_full: any

    def __init__(self, parser):
        self.player_footstep = parser.parse_event("player_footstep")
        self.player_jump = parser.parse_event("player_jump")
        self.player_spawn = parser.parse_event("player_spawn")
        self.player_disconnect = parser.parse_event("player_disconnect")
        self.player_connect = parser.parse_event("player_connect")
        self.player_connect_full = parser.parse_event("player_connect_full")


@dataclass
class BombRelatedEvents:
    bomb_planted: any
    bomb_beginplant: any
    bomb_defused: any
    bomb_dropped: any
    bomb_pickup: any

    def __init__(self, parser):
        self.bomb_planted = parser.parse_event("bomb_planted")
        self.bomb_beginplant = parser.parse_event("bomb_beginplant")
        self.bomb_defused = parser.parse_event("bomb_defused")
        self.bomb_begindefuse = parser.parse_event("bomb_begindefuse")
        self.bomb_dropped = parser.parse_event("bomb_dropped")
        self.bomb_pickup = parser.parse_event("bomb_pickup")


@dataclass
class GrenadesAndExplosives:
    hegrenade_detonate: any
    smokegrenade_detonate: any
    smokegrenade_expired: any
    flashbang_detonate: any
    inferno_startburn: any
    inferno_expire: any
    decoy_started: any
    decoy_detonate: any

    def __init__(self, parser):
        self.hegrenade_detonate = parser.parse_event("hegrenade_detonate")
        self.smokegrenade_detonate = parser.parse_event("smokegrenade_detonate")
        self.smokegrenade_expired = parser.parse_event("smokegrenade_expired")
        self.flashbang_detonate = parser.parse_event("flashbang_detonate")
        self.inferno_startburn = parser.parse_event("inferno_startburn")
        self.inferno_expire = parser.parse_event("inferno_expire")
        self.decoy_started = parser.parse_event("decoy_started")
        self.decoy_detonate = parser.parse_event("decoy_detonate")


@dataclass
class PlayerDamageAndDeath:
    bullet_damage: any
    player_hurt: any
    player_death: any
    other_death: any
    player_blind: any

    def __init__(self, parser):
        self.bullet_damage = parser.parse_event("bullet_damage")
        self.player_hurt = parser.parse_event("player_hurt")
        self.player_death = parser.parse_event("player_death")
        self.other_death = parser.parse_event("other_death")
        self.player_blind = parser.parse_event("player_blind")


@dataclass
class TeamAndRankUpdates:
    player_team: any
    rank_update: any

    def __init__(self, parser):
        self.player_team = parser.parse_event("player_team")
        self.rank_update = parser.parse_event("rank_update")


@dataclass
class Communication:
    chat_message: any

    def __init__(self, parser):
        self.chat_message = parser.parse_event("chat_message")


@dataclass
class MiscellaneousGameEvents:
    buytime_ended: any
    server_cvar: any

    def __init__(self, parser):
        self.buytime_ended = parser.parse_event("buytime_ended")
        self.server_cvar = parser.parse_event("server_cvar")
