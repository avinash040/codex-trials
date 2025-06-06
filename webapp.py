from flask import Flask, render_template, request, jsonify
import numpy as np
import aubio
import soundfile as sf
import io

app = Flask(__name__)


def freq_to_note(freq):
    if freq <= 0:
        return None
    A4 = 440.0
    note_num = int(round(69 + 12 * np.log2(freq / A4)))
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = note_num // 12 - 1
    return f"{note_names[note_num % 12]}{octave}"


def detect_pitches(samples, samplerate, hop_size=512, amp_threshold=0.02):
    """Return pitch events from an audio array.

    amp_threshold is the minimum RMS amplitude required for a pitch to be
    considered valid. Quieter segments are treated as silence so unintentional
    sounds do not appear in the output.
    """

    tolerance = 0.8
    win_s = 1024
    pitch_o = aubio.pitch('default', win_s, hop_size, samplerate)
    pitch_o.set_unit('Hz')
    pitch_o.set_tolerance(tolerance)

    pitches = []
    timestamps = []

    for i in range(0, len(samples), hop_size):
        block = samples[i:i + hop_size]
        if len(block) < hop_size:
            block = np.pad(block, (0, hop_size - len(block)))
        amp = np.sqrt(np.mean(block ** 2))
        pitch = float(pitch_o(block)[0]) if amp >= amp_threshold else 0.0
        pitches.append(pitch)
        timestamps.append(i / float(samplerate))

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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    data = request.files['audio']
    audio_bytes = data.read()
    with io.BytesIO(audio_bytes) as buf:
        samples, samplerate = sf.read(buf, dtype='float32')
    samples = samples.mean(axis=1) if samples.ndim > 1 else samples
    events = detect_pitches(samples, samplerate)
    return jsonify(events)


if __name__ == '__main__':
    app.run(debug=True)
