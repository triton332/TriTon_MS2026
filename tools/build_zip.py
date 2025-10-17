## 5) `tools/build_zip.py`
```python
from pathlib import Path
import shutil, datetime


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)


INCLUDE = [
    "app-ui",
    "audio-core",
    "render-core",
    "README.md",
    "requirements.txt",
    "tools",
]


stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
zip_name = DIST / f"studio-2026_{stamp}"


TMP = ROOT / ".pack_tmp"
if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir()


for item in INCLUDE:
    src = ROOT / item
    if src.exists():
        if src.is_dir():
            shutil.copytree(src, TMP / src.name)
        else:
            shutil.copy2(src, TMP / src.name)


archive_path = shutil.make_archive(str(zip_name), "zip", root_dir=TMP)
shutil.rmtree(TMP)
print(f"Created artifact: {archive_path}")
