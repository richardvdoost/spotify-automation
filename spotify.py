#!python3

import argparse
import subprocess
import time


def main():

    COMMANDS = {"volume": volume, "sleep": sleep}

    parser = argparse.ArgumentParser(description="Spotify Automation - Tools to automate Spotify on Mac")
    parser.add_argument("command", choices=COMMANDS.keys())
    parser.add_argument("parameters", type=str, help="Parameters", nargs="+")
    args = parser.parse_args()

    COMMANDS[args.command](args.parameters)


def volume(parameters):
    command = parameters[0]

    if command == "get":
        print(get_volume())
        return

    if command[0] in ("+", "-"):
        delta = int(command)
        print(f"Changing volume volume by {delta}")
        change_volume(delta)
        return

    print(f"Setting volume to {command}")
    set_volume(int(command))


def sleep(parameters):
    print(f"Sleep: {parameters}")

    wait = parameters[0] if len(parameters) > 1 else 0
    time.sleep(int(wait))

    current_level = get_volume()
    pause = float(parameters[1]) / current_level
    for level in range(current_level - 1, 8, -1):
        start_time = time.time()
        set_volume(level)
        time.sleep(max(0, pause + start_time - time.time()))

    osascript('tell application "Spotify" to pause')
    print("Done")


def change_volume(delta):
    set_volume(get_volume() + delta)


def get_volume():
    return int(osascript('tell application "Spotify" to get sound volume'))


def set_volume(level):
    level = max(0, min(level + 1, 100))
    osascript(f'tell application "Spotify" to set sound volume to {level}')


def osascript(command):
    completed = subprocess.run(["osascript", "-e", command], check=True, capture_output=True)
    return completed.stdout.decode().strip()


if __name__ == "__main__":
    main()
