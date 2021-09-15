#!python3

import argparse
import subprocess
import time

PLAYLISTS = {
    "chill": ("3yHsqOLOzoFEm60M99SWJv", "6tunhVGD8C05MZNjSVIsjw"),
    "favorites": ("6ni68MkGnCQhyoJohHiuHC", "37BZB0z9T8Xu7U3e65qxFy"),
    "sfw": ("5Sd3qK4AvwE0nQzcscMHMA", "5W3N9NkOl0tLaqi5LZbUOC"),
    "old": ("2KGsnNbtbs4oTnVue3Cb4a", "0X3LTPRlsqs7rFZGVy6SSH"),
    "bedtimes": ("64VdS4dsqof17W3L3gAbE1", "5xKw68A720RT2Q4XrsmMg2"),
}

MIN_VOLUME = 8
PLAYLIST_INIT_VOLUME = 40
PLAYLIST_FADE_IN = 30


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
        start_playlist(*PLAYLISTS[args.command])


def start_playlist(playlist, track):
    set_volume(PLAYLIST_INIT_VOLUME)

    osascript(
        f'tell application "Spotify" to play track "spotify:track:{track}" in context "spotify:playlist:{playlist}"'
    )

    fade_volume(100, PLAYLIST_FADE_IN)


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
        duration = float(parameters[1]) * 60

    elif len(parameters) == 1:
        target_volume = int(parameters[0])
        duration = 10

    else:
        raise Exception("Fade needs two parameters: [target volume] [duration]")

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
        raise Exception(f"Sleep needs one or two parameters, got {len(parameters)}")

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
