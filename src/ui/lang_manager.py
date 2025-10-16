from PyQt6.QtCore import QObject, pyqtSignal
import json, os
class LangManager(QObject):
    languageChanged = pyqtSignal(dict)
    def __init__(self, lang_dir:str, default:str="vi"):
        super().__init__(); self.lang_dir=lang_dir; self.current=default; self.bundle={}; self.set_language(default)
    def set_language(self, code:str):
        path=os.path.join(self.lang_dir,f"lang_{code}.json")
        if not os.path.isfile(path): path=os.path.join(self.lang_dir,"lang_vi.json"); code="vi"
        with open(path,"r",encoding="utf-8") as f: self.bundle=json.load(f)
        self.current=code; self.languageChanged.emit(self.bundle)
    def tr(self,key:str)->str: return self.bundle.get(key,key)
