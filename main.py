from demoparser2 import DemoParser
from demo_data import DemoInfo

demo = DemoParser("./assets/testdemo.dem")


def main():
    # Parse the demo file

    # Initialize DemoInfo with the parsed data
    demo_info = DemoInfo(demo)

    # Output the rounds and tick rate
    print(f"Total Rounds Played: {demo_info.rounds}")
    print(f"Tick Rate: {demo_info.tick_rate}")


if __name__ == "__main__":
    main()
