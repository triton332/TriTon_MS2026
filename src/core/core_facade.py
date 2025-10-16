from engines.audio_engine import AudioEngine
from engines.visual_engine import VisualEngine
from engines.karaoke_engine import KaraokeEngine
from engines.ai_sync import AISync
from engines.render_engine import RenderEngine

class CoreFacade:
    def __init__(self):
        self.audio=AudioEngine(); self.visual=VisualEngine(); self.karaoke=KaraokeEngine(); self.ai=AISync(); self.render=RenderEngine()
