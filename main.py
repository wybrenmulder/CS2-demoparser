from demoparser2 import DemoParser
from demo_data import DemoInfo, PlayerStatsManager

demo = DemoParser("./assets/testdemo.dem")


def main():
    demo_info = DemoInfo(demo)

    print(f"Total Rounds Played: {demo_info.rounds}")
    print(f"Tick Rate: {demo_info.tick_rate}")

    player_death_events = demo.parse_event("player_death")
    print(player_death_events.columns)

    stats_manager = PlayerStatsManager(demo)
    stats_manager.process_player_deaths(demo)
    stats_manager.display_player_stats()


if __name__ == "__main__":
    main()
