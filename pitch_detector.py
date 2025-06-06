import sys
import time
import numpy as np
import sounddevice as sd
import aubio


def freq_to_note(freq):
    if freq <= 0:
        return None
    A4 = 440.0
    # MIDI note number
    note_num = int(round(69 + 12 * np.log2(freq / A4)))
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = note_num // 12 - 1
    note = note_names[note_num % 12]
    return f"{note}{octave}"


def detect_pitches(duration=60, samplerate=44100, hop_size=512, amp_threshold=0.02):
    """Record audio and return pitch events.

    amp_threshold sets the minimum RMS amplitude needed to consider a pitch
    reading valid. Lower-level sounds are ignored so quiet background noise
    doesn't create spurious notes.
    """

    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    audio = audio.flatten()

    tolerance = 0.8
    win_s = 1024
    pitch_o = aubio.pitch('default', win_s, hop_size, samplerate)
    pitch_o.set_unit('Hz')
    pitch_o.set_tolerance(tolerance)

    pitches = []
    timestamps = []

    for i in range(0, len(audio), hop_size):
        samples = audio[i:i + hop_size]
        if len(samples) < hop_size:
            samples = np.pad(samples, (0, hop_size - len(samples)))
        amp = np.sqrt(np.mean(samples ** 2))
        pitch = pitch_o(samples)[0] if amp >= amp_threshold else 0.0
        time_stamp = i / float(samplerate)
        pitches.append(pitch)
        timestamps.append(time_stamp)

    events = []
    if pitches:
        current_note = freq_to_note(pitches[0])
        start_time = timestamps[0]
        for freq, t in zip(pitches[1:], timestamps[1:]):
            note = freq_to_note(freq)
            if note != current_note:
                events.append({'note': current_note, 'start': start_time, 'end': t})
                current_note = note
                start_time = t
        events.append({'note': current_note, 'start': start_time, 'end': timestamps[-1]})
    return events


def main():
    duration = 60
    if len(sys.argv) > 1:
        duration = float(sys.argv[1])
    events = detect_pitches(duration)
    print("Pitch history:")
    for e in events:
        note = e['note'] or 'None'
        hold = e['end'] - e['start']
        print(f"{note} held for {hold:.2f} sec (from {e['start']:.2f} to {e['end']:.2f})")


if __name__ == '__main__':
    main()
