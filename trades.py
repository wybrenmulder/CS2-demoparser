from dataclasses import dataclass
import main


@dataclass
class TradeData:
    trade_kill_opportunities: int
    trade_kill_attempts: int
    trade_kill_successes: int

    def __init__(self):
        self.trade_kill_opportunities = 0
        self.trade_kill_attempts = 0
        self.trade_kill_successes = 0


trade_data = TradeData()


def check_if_death_is_traded():
    for [_, kill] in main.kills.iterrows():
        victim_name = kill["user_name"]
        killer_name = kill["attacker_name"]
        kill_tick = kill["tick"]
        trade_window = kill_tick + 320

        for [_, possible_trade] in main.kills.iterrows():
            if (
                possible_trade["user_name"] == killer_name
                and kill_tick < possible_trade["tick"] <= trade_window
            ):
                trader_name = possible_trade["attacker_name"]
                trade_tick = possible_trade["tick"]
                trade_ticks = trade_tick - kill_tick
                trade_seconds = trade_ticks / main.tick_rate

                print(
                    f"{trader_name} traded {victim_name} by killing {killer_name} in {trade_seconds:.2f} seconds ({trade_ticks} ticks)"
                )
                break
