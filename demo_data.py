from dataclasses import dataclass
from demoparser2 import DemoParser
from pandas import DataFrame


@dataclass()
class PlayerStats:
    steamid: int
    user_name: str
    team_number: int
    kills: int
    assists: int
    rounds: int
    deaths: int
    saves: int
    dmg_armor: int
    dmg_health: int
    fall_damage_taken: int
    kd: float
    kpr: float
    dpr: float
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
        self.dmg_armor = 0
        self.dmg_health = 0
        self.fall_damage_taken = 0
        self.kd = 0.0
        self.kpr = 0.0
        self.dpr = 0.0
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
    defined_rounds: any
    tick_rate: int
    round_end_delay: int

    def __init__(self, parser):
        self.tick_rate = 64
        self.round_end_delay = 7 * self.tick_rate
        self.rounds = self.get_rounds(parser)
        self.defined_rounds = self.define_rounds(parser)

    def get_rounds(self, parser):
        round_end_events = parser.parse_event("round_end")
        round_count = len(round_end_events)

        return round_count
    
    def get_round_idx(self, tick: int):
        for _, full_round in self.defined_rounds.iterrows():
            if full_round["round_start"] <= tick <= full_round["round_end"] + self.round_end_delay:
                return full_round["round"]
        return None

    def define_rounds(self, parser):
        round_start = parser.parse_event("round_start")
        round_end = parser.parse_event("round_end")

        defined_rounds = {
            "round": round_start["round"],
            "round_start": round_start["tick"],
            "round_end": round_end["tick"] + self.round_end_delay,
        }

        return DataFrame(data=defined_rounds)


@dataclass
class PlayerStatsManager:
    players: dict[int, PlayerStats]
    demo_info: any
    damage_tracker: dict

    def __init__(self, parser: DemoParser):
        self.players = {}
        self.demo_info = DemoInfo(parser)
        self.damage_tracker = {}

        playerinfo = parser.parse_player_info()
        for _, player in playerinfo.iterrows():
            steamid = player["steamid"]
            username = player["name"]
            team_number = player["team_number"]

            self.players[steamid] = PlayerStats(steamid, username, team_number)
        
    def process_player_death(self, parser: DemoParser):
        player_death_events = parser.parse_event("player_death")

        for _, death in player_death_events.iterrows():
            victim_steamid = int(death["user_steamid"])
            attacker_steamid = int(death["attacker_steamid"])
            assister_steamid = death.get("assister_steamid")

            if assister_steamid is not None:
                assister_steamid = int(assister_steamid)

            if attacker_steamid in self.players and attacker_steamid != victim_steamid:
                self.players[attacker_steamid].kills += 1

            if victim_steamid in self.players:
                self.players[victim_steamid].deaths += 1

            if assister_steamid and assister_steamid in self.players:
                self.players[assister_steamid].assists += 1

    def process_player_hurt(self, parser: DemoParser):
        player_hurt_events = parser.parse_event("player_hurt")

        for _, dmg in player_hurt_events.iterrows():
            hurt_event_tick = int(dmg["tick"])
            round_number = self.demo_info.get_round_idx(hurt_event_tick)
            print(f"Hurt event in round {round_number}, tick {hurt_event_tick}")

            victim_steamid = int(dmg["user_steamid"])
            dmg_health = int(dmg["dmg_health"])
            dmg_armor = int(dmg["dmg_armor"])
            weapon = dmg["weapon"]
            attacker_name = dmg.get("attacker_name", None)
            attacker_steamid = dmg.get("attacker_steamid", None)

            # Fall damage
            if attacker_name is None and attacker_steamid is None and (weapon == "generic"):
                if victim_steamid in self.players:
                    self.players[victim_steamid].fall_damage_taken += dmg_health
                continue

            if attacker_steamid is not None:
                attacker_steamid = int(attacker_steamid)
                
                if attacker_steamid in self.players and attacker_steamid != victim_steamid:
                    self.players[attacker_steamid].dmg_health += dmg_health
                    self.players[attacker_steamid].dmg_armor += dmg_armor

    def calculate_kd(self):
        for player in self.players.values():
            if player.deaths > 0:
                player.kd = player.kills / player.deaths
            else:
                player.kd = player.kills
                
    def calculate_per_round_values(self, parser: DemoParser):
        demo_info = DemoInfo(parser)
        total_rounds = demo_info.rounds

        # Calculate KPR, DPR, and APR for each player
        for player in self.players.values():
            if total_rounds > 0:
                player.kpr = player.kills / total_rounds
                player.dpr = player.deaths / total_rounds
                player.apr = player.assists / total_rounds
                player.adr = player.dmg_health / total_rounds
            else:
                player.kpr = 0
                player.dpr = 0
                player.apr = 0
                player.adr = 0

    def calculate_impact(self):
        for player in self.players.values():
            player.impact = 2.13 * player.kpr + 0.42 * player.apr - 0.41

    def display_player_stats(self):
        for stats in self.players.values():
            print(f"Player: {stats.user_name} Damage: {stats.dmg_health}")
            # prinf(f"  SteamID: {stats.steamid}")
            # print(f"  Kills: {stats.kills}")
            # print(f"  Deaths: {stats.deaths}")
            # print(f"  Assists: {stats.assists}")
            # print(f"  KD: {stats.kd:.2f}")
            # print(f"  KPR: {stats.kpr:.2f}")
            # print(f"  DPR: {stats.dpr:.2f}")
            # print(f"  APR: {stats.apr:.2f}")
            # print(f"  Impact: {stats.impact:.2f}")
            # print(f"  ADR: {stats.adr:.2f}")
            # print(f"  Impact: {stats.impact:.2f}")
            # print(f"  Damage to Health: {stats.dmg_health}")
            # print(f"  Damage to Armor: {stats.dmg_armor}")
            # print(f"  Fall damage taken: {stats.fall_damage_taken}")
            # print("------------------------------")


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
