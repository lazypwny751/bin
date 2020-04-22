#!/usr/bin/env python

import time, sys, random


def single_loading():
    print("Loading...")
    for i in range(0, 100):
        time.sleep(0.01)
        width = (i + 1) // 4
        bar = "[" + "#" * width + " " * (25 - width) + "]"
        sys.stdout.write(u"\u001b[1000D" + bar)
        sys.stdout.flush()
    print("\n...Bosh!")


def multi_loading(count):
    all_progress = [0] * count
    sys.stdout.write("\n" * count)  # Make sure we have space to draw the bars
    while any(x < 100 for x in all_progress):
        time.sleep(0.01)
        # Randomly increment one of our progress values
        unfinished = [(i, v) for (i, v) in enumerate(all_progress) if v < 100]
        index, _ = random.choice(unfinished)
        all_progress[index] += 1

        # Draw the progress bars
        sys.stdout.write(u"\u001b[1000D")  # Move left
        sys.stdout.write(u"\u001b[" + str(count) + "A")  # Move up
        for progress in all_progress:
            width = progress // 4
            print("[" + "#" * width + " " * (25 - width) + "]")


multi_loading(4)
