# Pitch Detection Webapp

This repository contains a simple in-browser pitch detector. The `docs` folder hosts a standalone web app that records from your microphone, detects pitch and musical note, and keeps a history of notes for up to one minute.

## Hosting with GitHub Pages

1. Open your repository settings on GitHub.
2. In the **Pages** section, choose the `docs/` folder as the source and save.
3. Visit the provided URL to use the app.
4. The `docs/_config.yml` file sets a Jekyll theme so the page looks good.


## Local Python Tools

For offline experimentation there are Python scripts:

- `pitch_detector.py` – command line pitch detection using `sounddevice` and `aubio`.
- `webapp.py` – a simple Flask server (not needed for GitHub Pages).

Compile them to verify dependencies:

```bash
python3 -m py_compile pitch_detector.py webapp.py
```

