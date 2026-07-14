import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from ui.dashboard import Dashboard

app = QApplication(sys.argv)

style = (
    Path(__file__).parent
    / "assets"
    / "style.qss"
)

if style.exists():
    with open(style, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

window = Dashboard()
window.show()

sys.exit(app.exec())