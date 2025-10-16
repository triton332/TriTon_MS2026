# Tri Ton Music Studio 2026 – Core Flow (Development)

## Run (UI skeleton)
```
pip install -r requirements.txt
python -m src.ui.ui_main
```

## Modules
- engines/: audio_engine, visual_engine, karaoke_engine, ai_sync, render_engine
- core/: core_facade (wire-up point)
- ui/: PyQt6 UI + i18n JSON (vi/en)

## Next Steps
- Wire AudioEngine into UI playback controls
- Implement VisualEngine preview (waveform neon)
- Add KaraokeEngine overlay and settings panel
- Implement RenderEngine (FFmpeg pipeline to MKV)
