from dataclasses import dataclass
import parser


@dataclass(init=True)
class PlayerStats:
    steamid: int
    name: str
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

    def __init__(self):
        self.steamid = 0
        self.name = ""
        self.team_number = 0
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

    def __init__(self):
        self.rounds = 0
        self.tick_rate = 64


game_events = parser.demo.list_game_events()

print(game_events)

df_events = {}

for event in game_events:
    event_var_name = f"df_{event}"  # Create the key name like "df_event_name"
    df_events[event_var_name] = parser.demo.parse_event(event)

print(df_events)
