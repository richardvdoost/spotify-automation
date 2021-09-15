#!python3

import argparse
import subprocess
import time

PLAYLISTS = {
    "chill": "3yHsqOLOzoFEm60M99SWJv",
    "favorites": "6ni68MkGnCQhyoJohHiuHC",
    "sfw": "5Sd3qK4AvwE0nQzcscMHMA",
    "old": "2KGsnNbtbs4oTnVue3Cb4a",
    "country": "5armxQabx9PcgYB2KyZclh",
    "techno": "61qO0IuYwm9Sa0oym5W0ik",
    "rasta": "1CrztYhtvmsXyFbKFyHb3K",
    "bedtimes": "64VdS4dsqof17W3L3gAbE1",
    "latin": "7iC8QpZ6KgHLaryFDgGfGO",
    "nl": "2bBpHaiDyPXdlhTTI5mJIH",
    "croissant": "4gbhvNjMs77Ex9FZIuGP4u",
    "tropic": "5CvYV8IMucPulbn82INrAU",
    "broke": "5GN54Qe9X2gXhRa4LTXcnY",
}

MIN_VOLUME = 8
PLAYLIST_INIT_VOLUME = 25
PLAYLIST_SWITCH_VOLUME = 30
PLAYLIST_STARTING = 30
PLAYLIST_SWITCH = (10, 20)
DEFAULT_FADE = 6
SLEEP_WAIT = 5
SLEEP_FADE = 10


def main():
    COMMANDS = {
        "play": play,
        "pause": pause,
        "volume": volume,
        "fade": fade,
        "sleep": sleep,
    }

    choices = list(COMMANDS.keys()) + list(PLAYLISTS.keys())

    parser = argparse.ArgumentParser(
        description="Spotify Automation - Tools to automate Spotify on Mac"
    )
    parser.add_argument("command", choices=choices)
    parser.add_argument("parameters", type=str, help="Parameters", nargs="*")
    args = parser.parse_args()

    if args.command in COMMANDS:
        COMMANDS[args.command](args.parameters)

    elif args.command in PLAYLISTS:
        print(f"Start Playlist: {args.command}")
        start_playlist(PLAYLISTS[args.command], args.parameters)


def start_playlist(playlist, parameters):

    should_switch = is_playing()

    if len(parameters) == 2:
        fade_out = int(parameters[0])
        fade_in = int(parameters[1])
    elif len(parameters) == 1:
        fade_out = PLAYLIST_SWITCH[0]
        fade_in = int(parameters[0])
    else:
        fade_out = PLAYLIST_SWITCH[0]
        fade_in = PLAYLIST_SWITCH[1] if should_switch else PLAYLIST_STARTING

    if should_switch:
        fade_volume(PLAYLIST_SWITCH_VOLUME, fade_out)
    else:
        set_volume(PLAYLIST_INIT_VOLUME)

    osascript('tell application "Spotify" to set shuffling to true')
    osascript(f'tell application "Spotify" to play track "spotify:playlist:{playlist}"')

    fade_volume(100, fade_in)


def play(parameters=None):
    osascript('tell application "Spotify" to play')


def pause(parameters=None):
    osascript('tell application "Spotify" to pause')


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


def fade(parameters):
    if len(parameters) == 2:
        target_volume = int(parameters[0])
        duration = float(parameters[1])

    elif len(parameters) == 1:
        target_volume = int(parameters[0])
        duration = DEFAULT_FADE

    else:
        print("Fade needs two parameters: [target volume] [duration]")
        return

    print(
        f"Fading Spotify volume from {get_volume()} to {target_volume} in {duration:.0f} seconds"
    )

    fade_volume(target_volume, duration)


def sleep(parameters):
    print("Spotify Sleep")

    orig_volume = get_volume()

    if len(parameters) == 2:
        print(
            f"Waiting {parameters[0]} minutes, then fading down volume in {parameters[1]} minutes."
        )
        wait = float(parameters[0]) * 60
        fade_time = float(parameters[1]) * 60

        time.sleep(wait)
        print("Starting volume fade")

    elif len(parameters) == 1:
        print(f"Fading down volume in {parameters[0]} minutes.")
        fade_time = float(parameters[0]) * 60

    else:
        time.sleep(SLEEP_WAIT)
        fade_time = SLEEP_FADE

    fade_volume(8, fade_time)

    pause()
    set_volume(orig_volume)

    print("Done")


def fade_volume(target_volume, duration):
    start_volume = get_volume()
    volume_delta = int(abs(start_volume - target_volume))

    if volume_delta == 0:
        return

    start_time = time.time()
    elapsed = 0
    current_volume = start_volume
    while elapsed < duration:
        elapsed = time.time() - start_time
        progress = elapsed / duration

        level = round((1.0 - progress) * start_volume + progress * target_volume)
        if level == current_volume:
            time.sleep(0.05)
            continue

        # print(f"Elapsed: {elapsed:.02f}s - Level: {level}")

        set_volume(level)

        current_volume = level
        if current_volume == target_volume:
            break


def change_volume(delta):
    set_volume(get_volume() + delta)


def is_playing():
    return osascript('tell application "Spotify" to player state') == "playing"


def get_volume():
    return int(osascript('tell application "Spotify" to get sound volume'))


def set_volume(level):
    level = max(0, min(level + 1, 100))
    osascript(f'tell application "Spotify" to set sound volume to {level}')


def osascript(command):
    completed = subprocess.run(
        ["osascript", "-e", command], check=True, capture_output=True
    )
    return completed.stdout.decode().strip()


if __name__ == "__main__":
    main()
