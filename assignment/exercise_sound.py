#!/usr/bin/env python3
"""
PWM Tone Generator

based on https://www.coderdojotc.org/micropython/sound/04-play-scale/
"""

import machine
import utime

# GP16 is the speaker pin
SPEAKER_PIN = 16

# create a Pulse Width Modulation Object on this pin
speaker = machine.PWM(machine.Pin(SPEAKER_PIN))


def playtone(frequency: float, duration: float) -> None:
    speaker.duty_u16(1000)
    speaker.freq(frequency)
    utime.sleep(duration)


def quiet():
    speaker.duty_u16(0)


notes={
    "C5":523.25,
    "B4":466.16,
    "A4":415.30,
    "G4":392.00
    }


melody = [
    ("C5",0.5), ("B4", 0.5), ("A4", 0.5), ("G4",0.5), ("G4", 0.3), ("A4", 0.3),
    ("A4", 0.3), ("A4", 0.3), ("G4", 0.3), ("A4", 0.3), ("A4", 0.3), ("A4", 0.3)
    ]

print("Playing frequency (Hz):")

for note, duration in melody:
    playtone(notes[note], duration)

# Turn off the PWM
quiet()
