import sys, os
from PyQt6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,
    QPushButton,QListWidget,QLabel,QFileDialog,QSlider,QMenuBar,QAction,QMessageBox)
from PyQt6.QtCore import Qt
from ui.lang_manager import LangManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        lang_dir=os.path.join(os.path.dirname(__file__),"i18n")
        self.lang=LangManager(lang_dir,default="vi"); self.lang.languageChanged.connect(self.apply_language)
        self.setWindowTitle(self.lang.tr("app_title")); self._build_menu(); self._build_ui()
        self.apply_language(self.lang.bundle); self.statusBar().showMessage(self.lang.tr("status_ready"))
    def _build_menu(self):
        menubar=QMenuBar(self); self.setMenuBar(menubar)
        self.menuLanguage=menubar.addMenu(self.lang.tr("menu_language"))
        action_vi=QAction(self.lang.tr("lang_vi"),self); action_en=QAction(self.lang.tr("lang_en"),self)
        action_vi.triggered.connect(lambda: self.lang.set_language("vi"))
        action_en.triggered.connect(lambda: self.lang.set_language("en"))
        self.menuLanguage.addAction(action_vi); self.menuLanguage.addAction(action_en)
    def _build_ui(self):
        central=QWidget(); root=QVBoxLayout(central)
        ctrl=QHBoxLayout()
        self.btnAdd=QPushButton(self.lang.tr("btn_add_music"))
        self.btnPrev=QPushButton(self.lang.tr("btn_prev"))
        self.btnPlay=QPushButton(self.lang.tr("btn_play"))
        self.btnNext=QPushButton(self.lang.tr("btn_next"))
        self.sldVol=QSlider(Qt.Orientation.Horizontal); self.sldVol.setRange(0,100); self.sldVol.setValue(80)
        ctrl.addWidget(self.btnAdd); ctrl.addWidget(self.btnPrev); ctrl.addWidget(self.btnPlay); ctrl.addWidget(self.btnNext)
        ctrl.addWidget(QLabel(self.lang.tr("volume"))); ctrl.addWidget(self.sldVol)
        self.lblPlaylist=QLabel(self.lang.tr("playlist")); self.list=QListWidget()
        root.addLayout(ctrl); root.addWidget(self.lblPlaylist); root.addWidget(self.list); self.setCentralWidget(central)
        self.btnAdd.clicked.connect(self.add_music); self.btnPlay.clicked.connect(self.toggle_play_stub)
    def apply_language(self,bundle:dict):
        self.setWindowTitle(bundle.get("app_title","Tri Ton Music Studio 2026"))
        self.menuLanguage.setTitle(bundle.get("menu_language","Language"))
        self.btnAdd.setText(bundle.get("btn_add_music","Add Music"))
        self.btnPrev.setText(bundle.get("btn_prev","Previous"))
        self.btnPlay.setText(bundle.get("btn_play","Play"))
        self.btnNext.setText(bundle.get("btn_next","Next"))
        self.lblPlaylist.setText(bundle.get("playlist","Playlist"))
        if self.statusBar(): self.statusBar().showMessage(bundle.get("status_ready","Ready"))
    def add_music(self):
        path,_=QFileDialog.getOpenFileName(self,"Select WAV","","WAV Files (*.wav)")
        if not path: return
        for i in range(self.list.count()):
            if self.list.item(i).text()==path:
                QMessageBox.information(self,"Info","Tệp đã tồn tại trong playlist / File already in playlist."); return
        self.list.addItem(path); 
        if self.list.count()==1: self.list.setCurrentRow(0)
    def toggle_play_stub(self):
        if self.btnPlay.text() in (self.lang.tr("btn_play"),"Play","Phát"):
            self.btnPlay.setText(self.lang.tr("btn_pause")); self.statusBar().showMessage(self.lang.tr("status_playing"))
        else:
            self.btnPlay.setText(self.lang.tr("btn_play")); self.statusBar().showMessage(self.lang.tr("status_paused"))
def main():
    app=QApplication(sys.argv); w=MainWindow(); w.resize(900,560); w.show(); sys.exit(app.exec())
if __name__=="__main__": main()
