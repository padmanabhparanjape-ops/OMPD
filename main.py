from ui.dashboard import Dashboard
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = Dashboard()
window.show()
sys.exit(app.exec())