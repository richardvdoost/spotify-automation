#!python3

import argparse
import subprocess
import time

PLAYLISTS = {
    "bedtimes": "64VdS4dsqof17W3L3gAbE1",
    "broke": "5GN54Qe9X2gXhRa4LTXcnY",
    "chill": "3yHsqOLOzoFEm60M99SWJv",
    "country": "5armxQabx9PcgYB2KyZclh",
    "croissant": "4gbhvNjMs77Ex9FZIuGP4u",
    "favorites": "6ni68MkGnCQhyoJohHiuHC",
    "journal": "2hNvTwmTycXAhuYZtwqp57",
    "latin": "7iC8QpZ6KgHLaryFDgGfGO",
    "lofi": "37i9dQZF1DWWQRwui0ExPn",
    "lounge": "0gxJozy2nEfFdRoVgXtW1N",
    "motivation": "7c3upnoRmYC4d2X03jwkXp",
    "mythical": "1EttrSm3AKA8MpUqIN7RaT",
    "nl": "2bBpHaiDyPXdlhTTI5mJIH",
    "old": "2KGsnNbtbs4oTnVue3Cb4a",
    "pasta": "6MZ0mFE5uVzUDgzZd0iPxh",
    "popi": "6DFTGg4vxsnaGqDoBwO7XG",
    "rasta": "1CrztYhtvmsXyFbKFyHb3K",
    "sfw": "5Sd3qK4AvwE0nQzcscMHMA",
    "techno": "61qO0IuYwm9Sa0oym5W0ik",
    "tropic": "5CvYV8IMucPulbn82INrAU",
    "wakey": "7eBXOXIHcWQUlDpnAbb4CD",
}

MIN_VOLUME = 8
PLAYLIST_INIT_VOLUME = 0.15
PLAYLIST_SWITCH_VOLUME = 0.2
PLAYLIST_STARTING = 25
PLAYLIST_SWITCH = (12, 12)
DEFAULT_FADE = 5
SLEEP_WAIT = 5
SLEEP_FADE = 15


def main():
    COMMANDS = {
        "play": play,
        "pause": pause,
        "volume": volume,
        "fade": fade,
        "sleep": sleep,
        "wake": wake,
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
    end_volume = get_volume()

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
        fade_volume(
            round(MIN_VOLUME + (end_volume - MIN_VOLUME) * PLAYLIST_SWITCH_VOLUME),
            fade_out,
        )
    else:
        set_volume(round(MIN_VOLUME + (end_volume - MIN_VOLUME) * PLAYLIST_INIT_VOLUME))

    osascript('tell application "Spotify" to set shuffling to true')
    osascript(f'tell application "Spotify" to play track "spotify:playlist:{playlist}"')

    fade_volume(end_volume, fade_in)


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
        print(
            f"Fade receives two parameters: [target volume] [duration={DEFAULT_FADE}]"
        )
        return

    print(
        f"Fading Spotify volume from {get_volume()} to {target_volume} in"
        f" {duration:.0f} seconds"
    )

    fade_volume(target_volume, duration)


def sleep(parameters):
    print("Spotify Sleep")

    orig_volume = get_volume()

    if len(parameters) == 2:
        print(
            f"Waiting {parameters[0]} minutes, then fading down volume in"
            f" {parameters[1]} minutes."
        )
        wait = float(parameters[0]) * 60
        fade_time = float(parameters[1]) * 60

        time.sleep(wait)

    elif len(parameters) == 1:
        fade_time = float(parameters[0]) * 60

    else:
        time.sleep(SLEEP_WAIT)
        fade_time = SLEEP_FADE

    fade_volume(8, fade_time)

    pause()
    set_volume(orig_volume)

    print("Done")


def wake(parameters):
    print("Spotify Wake")

    target_volume = max(75, get_volume())

    if len(parameters) == 2:
        print(
            f"Waiting {parameters[0]} minutes, then fading down volume in"
            f" {parameters[1]} minutes."
        )
        wait = float(parameters[0]) * 60
        fade_time = float(parameters[1]) * 60

        time.sleep(wait)

    elif len(parameters) == 1:
        fade_time = float(parameters[0]) * 60

    else:
        time.sleep(SLEEP_WAIT)
        fade_time = SLEEP_FADE

    pause()
    set_volume(8)
    play()
    fade_volume(target_volume, fade_time)

    print("Done")


def fade_volume(target_volume, duration):
    start_volume = get_volume()
    volume_delta = int(abs(start_volume - target_volume))

    print(f"Fading volume from {start_volume} to {target_volume} in {duration} seconds")

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
    print()


def change_volume(delta):
    print(f"Changing volume volume by {delta}")
    set_volume(get_volume() + delta)


def is_playing():
    return osascript('tell application "Spotify" to player state') == "playing"


def get_volume():
    return int(osascript('tell application "Spotify" to get sound volume'))


def set_volume(level):
    print(f"Setting volume to: {level}%  ", end="\r")
    level = max(0, min(level + 1, 100))
    osascript(f'tell application "Spotify" to set sound volume to {level}')


def osascript(command):
    completed = subprocess.run(
        ["osascript", "-e", command], check=True, capture_output=True
    )
    return completed.stdout.decode().strip()


if __name__ == "__main__":
    main()
