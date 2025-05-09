from dataclasses import dataclass
from demoparser2 import DemoParser
from pandas import DataFrame


@dataclass()
class PlayerStats:
    steamid: int
    user_name: str
    team_name: str
    initial_health: int
    remaining_health: int
    kills: int
    assists: int
    rounds: int
    deaths: int
    saves: int
    dmg_armor: int
    dmg_health: int
    dmg_received: int
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
    trade_kill_success: float
    traded_death_opportunities: int
    traded_death_attempts: int
    traded_death_success: float
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

    def __init__(self, steamid: int, player_name: str, team_name: str):
        self.steamid = steamid
        self.user_name = player_name
        self.team_name = team_name
        self.initial_health = 100
        self.remaining_health = 100
        self.kills = 0
        self.assists = 0
        self.rounds = 0
        self.deaths = 0
        self.saves = 0
        self.dmg_armor = 0
        self.dmg_health = 0
        self.dmg_received = 0
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
        self.trade_kill_success = 0.0
        self.traded_death_opportunities = 0
        self.traded_death_attempts = 0
        self.traded_death_success = 0.0
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
    tick_rate: int
    round_end_delay: int
    rounds: int
    defined_rounds: any

    def __init__(self, parser):
        self.tick_rate = 64
        self.round_end_delay = 7 * self.tick_rate
        self.rounds = self.get_rounds(parser)
        self.defined_rounds = self.define_rounds(parser)

    def get_rounds(self, parser):
        round_end_events = parser.parse_event("round_end")
        return len(round_end_events)
    
    def get_round_idx(self, tick: int):
        for _, full_round in self.defined_rounds.iterrows():
            if full_round["round_start"] <= tick <= full_round["round_end_with_delay"]:
                return full_round["round"]
        return None

    def define_rounds(self, parser):
        round_start = parser.parse_event("round_start")
        round_end = parser.parse_event("round_end")

        defined_rounds = {
            "round": round_start["round"],
            "round_start": round_start["tick"],
            "round_end": round_end["tick"],
            "round_end_with_delay": round_end["tick"] + self.round_end_delay
        }

        return DataFrame(data=defined_rounds)
    
    def get_round_for_death(self, death_tick: int, round_info: DataFrame) -> (int, str):
        
        # Determines the round in which the death occurred or if it occurred during the delay period after a round.
        # Returns a tuple (round_number, status), where status is 'normal' or 'after_end'.
        
        for _, round_data in round_info.iterrows():
            # Normal round deaths
            if round_data["round_start"] <= death_tick <= round_data["round_end"]:
                return round_data["round"], "normal"

            # Deaths after round end but within delay
            if round_data["round_end"] < death_tick <= round_data["round_end_with_delay"]:
                return round_data["round"], "after_end"

        # If no match is found, return -1 or handle the error appropriately
        return -1, "unknown"


@dataclass
class PlayerStatsManager:
    players: dict[int, PlayerStats]
    demo_info: any
    damage_tracker: dict
    alive_at_round_end: dict
    bomb_plants_by_round: dict
    bomb_defuses_by_round: dict

    def __init__(self, parser: DemoParser):
        self.players = {}
        self.demo_info = DemoInfo(parser)
        self.damage_tracker = {}
        self.alive_at_round_end = {}
        self.bomb_plants_by_round = {}
        self.bomb_defuses_by_round = {}

    def declare_player(self, parser):
        playerinfo = parser.parse_player_info()
        for _, player in playerinfo.iterrows():
            steamid = player["steamid"]
            username = player["name"]
            team_number = player["team_number"]
            if team_number == 1:
                team_name = "Spectators"
            elif team_number == 2:
                team_name = "CT"
            elif team_number == 3:
                team_name = "T"
            else:
                team_name = "Unknown"

            print(username, team_name, team_number)

            self.players[steamid] = PlayerStats(steamid, username, team_name)

    def switch_sides(self, parser):
        # Parse round end events to track rounds played
        round_end_events = parser.parse_event("round_end", other=["total_rounds_played", "round_win_status"])
        
        # Store initial teams (CT or T)
        team_mapping = {steamid: player.team_name for steamid, player in self.players.items()}

        for _, round_end in round_end_events.iterrows():
            round_number = round_end.get("total_rounds_played", 0)

            # **Switch AFTER Round 12 (so at Round 13)**
            if round_number == 13 or (round_number > 24 and (round_number - 1) % 12 == 0):
                # Swap teams correctly
                for steamid in team_mapping:
                    team_mapping[steamid] = "CT" if team_mapping[steamid] == "T" else "T"

            # Create lists of players for each team
            ct_players = [player.user_name for steamid, player in self.players.items() if team_mapping[steamid] == "CT"]
            t_players = [player.user_name for steamid, player in self.players.items() if team_mapping[steamid] == "T"]

            # Print correct teams per round
            # print(f"Round {round_number}:")
            # print(f"  CT: {', '.join(ct_players)}")
            # print(f"  T: {', '.join(t_players)}\n")

    def process_alive_at_round_end(self, parser: DemoParser):
        player_death_events = parser.parse_event("player_death")
        round_info = self.demo_info.define_rounds(parser)  # Get round info

        alive_players = {}  # Track alive players per round

        for _, death in player_death_events.iterrows():
            victim_name = death["user_name"]
            death_tick = int(death["tick"])
            death_round = self.demo_info.get_round_for_death(death_tick, round_info)
            # Convert round number to native int
            death_round = (int(death_round[0]), death_round[1])


            # Initialize alive players at the start of each round
            if death_round not in alive_players:
                alive_players[death_round] = {
                    "CT": [p.user_name for p in self.players.values() if p.team_name == "CT"],
                    "T": [p.user_name for p in self.players.values() if p.team_name == "T"]
                }

            # Remove the victim from the alive players list
            for team in ["CT", "T"]:
                if victim_name in alive_players[death_round][team]:
                    alive_players[death_round][team].remove(victim_name)

        # Print remaining alive players at the END of each round
        # for round_num, teams in sorted(alive_players.items()):
        #     print(f"\nRound {round_num} - Alive Players at End:")
        #     print(f"  CT: {', '.join(teams['CT']) if teams['CT'] else 'None'}")
        #     print(f"  T: {', '.join(teams['T']) if teams['T'] else 'None'}")

        # print(alive_players)
        return alive_players
        
    def get_winner_of_rounds(self, parser: DemoParser):
        round_end_events = parser.parse_event("round_end")
        round_info = self.demo_info.define_rounds(parser)  # Optional if not already called

        round_winners = {}

        for _, event in round_end_events.iterrows():
            try:
                round_number = int(event["round"])
                reason = event["reason"]
                winning_team = event["winner"]  # was previously incorrectly using "winning_team"

                # Store with round and reason as key
                round_winners[(round_number, reason)] = winning_team
            except KeyError as e:
                print(f"[ERROR] Missing expected key in event: {e}")
                continue

        return round_winners
    
    def analyze_round_end_scenario(self, parser):
        # Get round winners and alive players at round end
        round_winners = self.get_winner_of_rounds(parser)
        alive_players = self.process_alive_at_round_end(parser)  # should already be filled from process_alive_at_round_end()

        # Reason mapping for round end conditions
        reason_mapping = {
            "ct_killed": "T win (all CTs killed)",
            "t_killed": "CT win (all Ts killed)",
            "bomb_defused": "Bomb defused",
            "bomb_exploded": "Bomb exploded",
            "time_ran_out": "Time ran out",
        }

        print(alive_players)
        print("\n--- Round Summary ---")

        for (round_num, reason), winner in sorted(round_winners.items()):
            # Use (round_num, 'normal') to match keys in alive_players
            round_key = (round_num, 'normal')
            ct_alive = alive_players.get(round_key, {}).get("CT", [])
            t_alive = alive_players.get(round_key, {}).get("T", [])

            # Map the reason to a more readable string
            readable_reason = reason_mapping.get(reason, reason)

            # Print the round summary
            print(f"Round {round_num}:")
            print(f"  Winner        : {winner}")
            print(f"  End Condition : {readable_reason}")
            print(f"  CTs Alive     : {', '.join(ct_alive) if ct_alive else 'None'}")
            print(f"  Ts Alive      : {', '.join(t_alive) if t_alive else 'None'}\n")

    def process_player_death(self, parser: DemoParser):
        player_death_events = parser.parse_event("player_death")
        round_info = self.demo_info.define_rounds(parser)

        for _, death in player_death_events.iterrows():
            victim_steamid = int(death["user_steamid"])
            victim_name = death["user_name"]
            attacker_steamid = death.get("attacker_steamid", None)
            assister_steamid = death.get("assister_steamid")
            weapon = death.get("weapon", None)
            death_tick = int(death["tick"])
            death_round, status = self.demo_info.get_round_for_death(death_tick, round_info)

            if assister_steamid is not None:
                assister_steamid = int(assister_steamid)

            # Check if the victim died to a bomb explosion
            if attacker_steamid is None and weapon == "planted_c4":
                continue

            # Exception for killed by world
            if attacker_steamid is not None and weapon == "world":
                continue

            # If there's a valid attacker
            if attacker_steamid is not None:
                attacker_steamid = int(attacker_steamid)
                if attacker_steamid in self.players and attacker_steamid != victim_steamid:
                    self.players[attacker_steamid].kills += 1

            # Count the victim's death
            if victim_steamid in self.players:
                self.players[victim_steamid].deaths += 1

            # Count assists
            if assister_steamid and assister_steamid in self.players:
                self.players[assister_steamid].assists += 1

            if status == "normal":
                print(f"Player {victim_name} died in round {death_round}, tick {death_tick}.")
            elif status == "after_end":
                print(20 * "-")
                print(f"EXCEPTION: Player {victim_name} died in the round_end_delay AFTER round {death_round} ended, tick {death_tick}.")
                print(20 * "-")
            else:
                print(f"Player {victim_name} died at tick {death_tick}, but round couldn't be determined.")

    def process_player_hurt(self, parser: DemoParser):
        player_hurt_events = parser.parse_event("player_hurt")
        current_round = None  # Track the current round to detect changes

        # Initialize damage tracking dictionaries
        round_damage_summary = {}
        total_damage_taken_per_victim = {}

        for _, dmg in player_hurt_events.iterrows():
            hurt_event_tick = int(dmg["tick"])
            round_number = self.demo_info.get_round_idx(hurt_event_tick)

            # Handle round transition
            if current_round is not None and current_round != round_number:
                self.print_round_summary(current_round, round_damage_summary)
                round_damage_summary.clear()
                total_damage_taken_per_victim.clear()

            current_round = round_number
            self.process_damage_event(dmg, round_damage_summary, total_damage_taken_per_victim)

        # Print final round summary
        self.print_round_summary(current_round, round_damage_summary)

    def process_damage_event(self, dmg, round_damage_summary, total_damage_taken_per_victim):
        victim_steamid = int(dmg["user_steamid"])
        victim_name = str(dmg["user_name"])
        attacker_steamid = dmg.get("attacker_steamid", None)
        attacker_name = str(dmg["attacker_name"]) if attacker_steamid else "FALL DAMAGE"
        dmg_health = int(dmg["dmg_health"])
        weapon = str(dmg["weapon"])

        print(f"Hurt event: {victim_name} took {dmg_health} damage from {attacker_name} using {weapon}.")

        # Handle fall damage separately
        if attacker_steamid is None:
            self.process_fall_dmg(victim_steamid, dmg_health, total_damage_taken_per_victim)
            return

        attacker_steamid = int(attacker_steamid)

        # Handle team damage
        if self.is_friendly_fire(attacker_steamid, victim_steamid):
            self.process_team_dmg(attacker_steamid, victim_steamid, dmg_health, total_damage_taken_per_victim)
            return

        # Track and clamp damage
        self.track_damage(attacker_steamid, victim_steamid, dmg_health, round_damage_summary, total_damage_taken_per_victim)

    def is_friendly_fire(self, attacker_steamid, victim_steamid):
        return self.players[attacker_steamid].team_name == self.players[victim_steamid].team_name

    def process_fall_dmg(self, victim_steamid, dmg_health, total_damage_taken_per_victim):
        # Handle fall damage logic
        print(f"Processing fall damage: {dmg_health} damage to {self.players[victim_steamid].user_name}.")
        total_damage_taken_so_far = total_damage_taken_per_victim.get(victim_steamid, 0)
        remaining_damage_cap = 100 - total_damage_taken_so_far
        effective_damage = min(dmg_health, remaining_damage_cap)

        total_damage_taken_per_victim[victim_steamid] = total_damage_taken_so_far + effective_damage
        self.players[victim_steamid].remaining_health -= effective_damage

        print(f"Fall damage applied: {self.players[victim_steamid].user_name}'s health reduced by {effective_damage}. Remaining health: {self.players[victim_steamid].remaining_health}")

    def process_team_dmg(self, attacker_steamid, victim_steamid, dmg_health, total_damage_taken_per_victim):
        # Handle team damage logic (friendly fire)
        print(f"Processing team damage: {dmg_health} damage from {self.players[attacker_steamid].user_name} to {self.players[victim_steamid].user_name}.")
        total_damage_taken_so_far = total_damage_taken_per_victim.get(victim_steamid, 0)
        remaining_damage_cap = 100 - total_damage_taken_so_far
        effective_damage = min(dmg_health, remaining_damage_cap)

        total_damage_taken_per_victim[victim_steamid] = total_damage_taken_so_far + effective_damage
        self.players[victim_steamid].remaining_health -= effective_damage

        print(f"Teammate damage applied: {self.players[victim_steamid].user_name}'s health reduced by {effective_damage}. Remaining health: {self.players[victim_steamid].remaining_health}")

    def track_damage(self, attacker_steamid, victim_steamid, dmg_health, round_damage_summary, total_damage_taken_per_victim):
        # Track and clamp damage based on caps
        total_damage_so_far = total_damage_taken_per_victim.get(victim_steamid, 0)
        remaining_damage_cap = 100 - total_damage_so_far
        effective_damage = min(dmg_health, remaining_damage_cap)

        # Update damage dictionaries
        if attacker_steamid not in round_damage_summary:
            round_damage_summary[attacker_steamid] = {}
        if victim_steamid not in round_damage_summary[attacker_steamid]:
            round_damage_summary[attacker_steamid][victim_steamid] = 0
        if victim_steamid not in total_damage_taken_per_victim:
            total_damage_taken_per_victim[victim_steamid] = 0

        # Apply the effective damage
        total_damage_taken_per_victim[victim_steamid] += effective_damage
        round_damage_summary[attacker_steamid][victim_steamid] += effective_damage

        # Handle damage clamping
        if effective_damage < dmg_health:
            print(f"Damage clamped: {self.players[attacker_steamid].user_name} dealt {effective_damage} (instead of {dmg_health}) to {self.players[victim_steamid].user_name}.")

        # Add to attacker’s total damage
        self.players[attacker_steamid].dmg_health += effective_damage

    def print_round_summary(self, round_number, round_damage_summary):
        print(f"--- End of Round {round_number} Damage Summary ---")
        for attacker_id, victims in round_damage_summary.items():
            attacker_name = self.players[attacker_id].user_name
            for victim_id, dmg_amount in victims.items():
                victim_name = self.players[victim_id].user_name
                print(f"{attacker_name} dealt {dmg_amount} damage to {victim_name}")
        print("---------------------------------------")

    def calculate_kd(self):
        for player in self.players.values():
            if player.deaths > 0:
                player.kd = player.kills / player.deaths
            else:
                player.kd = player.kills

    # def check_for_clutches(self):
    #     pass

    # def check_for_saves(self):
    #     pass

    # def check_ct_save(self):
    #     pass

    # def check_t_save(self):
    #     pass

    # def check_for_trades(self):
    #     pass

    # def calculate_kast(self):
    #     pass

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

    def calculate_hltv2(self):
        for player in self.players.values():
            player.hltv2 = 0.0073 * player.kast + 0.3591 * player.kpr + -0.5329 * player.dpr + 0.2372 * player.impact + 0.0032 * player.adr + 0.1587
            # print(f"kast {player.kast}, kpr {player.kpr}, dpr {player.dpr}, impact {player.impact}, adr {player.adr}")

    def display_player_stats(self):
        for stats in self.players.values():
            print(f"Player: {stats.user_name}:")
            # prinf(f"  SteamID: {stats.steamid}")
            # print(f"  Kills: {stats.kills}")
            # print(f"  Deaths: {stats.deaths}")
            # print(f"  Assists: {stats.assists}")
            # print(f"  KD: {stats.kd:.2f}")
            # print(f"  KPR: {stats.kpr:.2f}")
            # print(f"  DPR: {stats.dpr:.2f}")
            # print(f"  APR: {stats.apr:.2f}")
            # print(f"  Impact: {stats.impact:.2f}")
            # print(f"  ADR: {round(stats.adr)}")
            # print(f"  Impact: {stats.impact:.2f}")
            # print(f"  HLTV 2.0 Rating: {stats.hltv2:.2f}")
            # print(f"  Damage to Health: {stats.dmg_health}")
            # print(f"  Damage to Armor: {stats.dmg_armor}")
            # print(f"  Fall damage taken: {stats.fall_damage_taken}")
            print(f"  Rounds saved: {stats.saves}")
            # print(f"  Trade kill opportunities {stats.trade_kill_opportunities}")
            # print(f"  Trade kill attempts {stats.trade_kill_attempts}")
            # print(f"  Trade kill success {stats.trade_kill_success}")
            # print(f"  Traded death opportunities {stats.traded_death_opportunities}")
            # print(f"  Traded death attempts {stats.traded_death_attempts}")
            # print(f"  Traded death kill success {stats.traded_death_success}")
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
