from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def build_ui(self):
    """
    Build the complete dashboard UI.
    This file ONLY creates the interface.
    No AI / Camera / Database logic belongs here.
    """

    build_root_layout(self)

    build_sidebar(self)

    build_pages(self)

    finish_layout(self)


# ==========================================================
# ROOT LAYOUT
# ==========================================================

def build_root_layout(self):

    self.main_layout = QHBoxLayout(self)
    self.main_layout.setContentsMargins(15, 15, 15, 15)
    self.main_layout.setSpacing(15)


# ==========================================================
# SIDEBAR
# ==========================================================

def build_sidebar(self):

    self.sidebar = QFrame()
    self.sidebar.setObjectName("Sidebar")
    self.sidebar.setMinimumWidth(220)
    self.sidebar.setMaximumWidth(240)

    sidebar_layout = QVBoxLayout(self.sidebar)

    sidebar_layout.setContentsMargins(
        20,
        20,
        20,
        20,
    )

    sidebar_layout.setSpacing(18)

    logo = QLabel("🛡 OMPD")
    logo.setAlignment(Qt.AlignCenter)
    logo.setObjectName("Logo")

    subtitle = QLabel("PrivacyLens")
    subtitle.setAlignment(Qt.AlignCenter)
    subtitle.setObjectName("Subtitle")

    sidebar_layout.addWidget(logo)
    sidebar_layout.addWidget(subtitle)

    sidebar_layout.addSpacing(25)

    self.dashboard_btn = QPushButton("🏠 Dashboard")
    self.scan_btn = QPushButton("🔍 Privacy Scan")
    self.activity_btn = QPushButton("📋 Activity Center")
    self.analytics_btn = QPushButton("📈 Analytics")
    self.settings_btn = QPushButton("⚙ Settings")
    self.about_btn = QPushButton("ℹ About")

    buttons = [
        self.dashboard_btn,
        self.scan_btn,
        self.activity_btn,
        self.analytics_btn,
        self.settings_btn,
    ]

    for button in buttons:

        button.setMinimumHeight(48)
        button.setCursor(Qt.PointingHandCursor)

        sidebar_layout.addWidget(button)

    sidebar_layout.addStretch()

    self.about_btn.setMinimumHeight(48)
    self.about_btn.setCursor(Qt.PointingHandCursor)

    sidebar_layout.addWidget(self.about_btn)

    self.dashboard_btn.clicked.connect(
    lambda: self.stack.setCurrentWidget(
        self.home_page
    )
)

    self.scan_btn.clicked.connect(
        lambda: self.stack.setCurrentWidget(
            self.scan_page
        )
    )

    self.activity_btn.clicked.connect(
        lambda: self.stack.setCurrentWidget(
            self.activity_page
        )
    )

    self.analytics_btn.clicked.connect(
        lambda: self.stack.setCurrentWidget(
            self.analytics_page
        )
    )

    self.settings_btn.clicked.connect(
        lambda: self.stack.setCurrentWidget(
            self.settings_page
        )
    )

    self.about_btn.clicked.connect(
        lambda: self.stack.setCurrentWidget(
            self.about_page
        )
    )

    self.main_layout.addWidget(self.sidebar)

def build_pages(self):

    self.stack = QStackedWidget()

    self.home_page = QWidget()
    build_home_page(self)
    self.scan_page = QWidget()
    self.activity_page = QWidget()
    self.analytics_page = QWidget()
    self.settings_page = QWidget()
    self.about_page = QWidget()

    self.stack.addWidget(self.home_page)
    self.stack.addWidget(self.scan_page)
    self.stack.addWidget(self.activity_page)
    self.stack.addWidget(self.analytics_page)
    self.stack.addWidget(self.settings_page)
    self.stack.addWidget(self.about_page)
    self.stack.setCurrentWidget(
    self.home_page
)

    self.main_layout.addWidget(
        self.stack,
        stretch=1
    )

def build_home_page(self):

    home_layout = QHBoxLayout(self.home_page)
    home_layout.setAlignment(Qt.AlignTop)
    home_layout.setContentsMargins(15, 15, 15, 15)
    home_layout.setSpacing(15)

    # -------------------------------
    # LEFT
    # -------------------------------

    left_widget = QWidget()
    left_widget.setSizePolicy(
    QSizePolicy.Expanding,
    QSizePolicy.Expanding
)
    left_layout = QVBoxLayout(left_widget)
    left_layout.setSpacing(15)

    # -------------------------------
    # TOP BAR
    # -------------------------------

    top_bar = QFrame()
    top_bar.setObjectName("TopBar")

    top_layout = QHBoxLayout(top_bar)
    top_layout.setContentsMargins(15, 10, 15, 10)

    title = QLabel("PrivacyLens Dashboard")
    title.setSizePolicy(
    QSizePolicy.Expanding,
    QSizePolicy.Preferred
)
    title.setObjectName("Title")

    self.camera_status = QLabel("● Offline")
    self.camera_status.setObjectName("StatusOffline")

    self.session_label = QLabel("Session 00:00")

    self.fps = QLabel("FPS : 0")

    self.privacy_score = QLabel("Privacy : 100")

    top_layout.addWidget(title)
    top_layout.addStretch()
    top_layout.addWidget(self.camera_status)
    top_layout.addSpacing(20)
    top_layout.addWidget(self.session_label)
    top_layout.addSpacing(20)
    top_layout.addWidget(self.fps)
    top_layout.addSpacing(20)
    top_layout.addWidget(self.privacy_score)

    left_layout.addWidget(top_bar)

    # -------------------------------
    # CAMERA
    # -------------------------------

    camera_card = QFrame()
    camera_card.setObjectName("CameraCard")

    camera_layout = QVBoxLayout(camera_card)
    camera_layout.setContentsMargins(10, 10, 10, 10)

    self.camera = QLabel("Camera Preview")
    self.camera.setObjectName("CameraPreview")
    self.camera.setAlignment(Qt.AlignCenter)
    self.camera.setWordWrap(True)
    self.camera.setMinimumHeight(450)
    self.camera.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Expanding
    )

    camera_layout.addWidget(self.camera)

    left_layout.addWidget(camera_card)

    # -------------------------------
    # RIGHT
    # -------------------------------

    build_right_panel(self)

    right_widget = QWidget()
    right_widget.setSizePolicy(
    QSizePolicy.Preferred,
    QSizePolicy.Expanding
)

    home_right_layout = QVBoxLayout(right_widget)

    home_right_layout.setContentsMargins(5, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setVerticalScrollBarPolicy(
    Qt.ScrollBarAsNeeded
)

    scroll.setWidget(self.right_panel)
    scroll.setHorizontalScrollBarPolicy(
    Qt.ScrollBarAlwaysOff
)

    home_right_layout.addWidget(scroll)

    home_layout.addWidget(left_widget, 4)
    home_layout.addWidget(right_widget, 2)

    # -------------------------------
    # FINAL
    # -------------------------------

    home_layout.setStretch(0, 4)
    home_layout.setStretch(1, 2)

def build_right_panel(self):

    self.right_panel = QFrame()
    self.right_panel.setObjectName("RightPanel")
    self.right_panel.setMinimumWidth(420)
    self.right_panel.setMaximumWidth(520)

    right_layout = QVBoxLayout(self.right_panel)
    right_layout.setContentsMargins(10, 10, 10, 10)
    right_layout.setSpacing(15)

    # =====================================================
    # CAMERA CONTROLS
    # =====================================================

    camera_card = QFrame()
    camera_card.setSizePolicy(
    QSizePolicy.Expanding,
    QSizePolicy.Expanding
)
    camera_card.setObjectName("Card")

    camera_layout = QVBoxLayout(camera_card)
    camera_layout.setSpacing(10)

    title = QLabel("Camera Controls")
    title.setObjectName("CardTitle")

    self.camera_selector = QComboBox()
    self.camera_selector.addItems([
        "Camera 0",
        "Camera 1",
    ])

    self.resolution_selector = QComboBox()
    self.resolution_selector.addItems([
        "640 × 480",
        "1280 × 720",
        "1920 × 1080",
    ])

    self.start_button = QPushButton("▶ Start Camera")
    self.stop_button = QPushButton("■ Stop Camera")

    self.start_button.clicked.connect(self.start_camera)
    self.stop_button.clicked.connect(self.stop_camera)

    camera_layout.addWidget(title)
    camera_layout.addWidget(self.camera_selector)
    camera_layout.addWidget(self.resolution_selector)
    camera_layout.addWidget(self.start_button)
    camera_layout.addWidget(self.stop_button)

    right_layout.addWidget(camera_card)
    right_layout.addSpacing(8)

    # =====================================================
    # DETECTION
    # =====================================================

    detect_card = QFrame()
    detect_card.setObjectName("Card")

    detect_layout = QVBoxLayout(detect_card)
    detect_layout.setSpacing(8)

    detect_title = QLabel("Detection")
    detect_title.setObjectName("CardTitle")

    self.face_blur = QPushButton("Face Blur : ON")
    self.object_blur = QPushButton("Object Blur : ON")
    self.ocr = QPushButton("OCR : ON")

    self.face_blur.clicked.connect(self.toggle_face_blur)
    self.object_blur.clicked.connect(self.toggle_object_blur)
    self.ocr.clicked.connect(self.toggle_ocr)

    self.conf_slider_label = QLabel(
        f"Confidence : {self.yolo_conf:.2f}"
    )

    self.conf_slider = QSlider(Qt.Horizontal)
    self.conf_slider.setRange(0, 100)
    self.conf_slider.setValue(int(self.yolo_conf * 100))
    self.conf_slider.valueChanged.connect(
        self.on_conf_slider_changed
    )

    detect_layout.addWidget(detect_title)
    detect_layout.addWidget(self.face_blur)
    detect_layout.addWidget(self.object_blur)
    detect_layout.addWidget(self.ocr)
    detect_layout.addWidget(self.conf_slider_label)
    detect_layout.addWidget(self.conf_slider)

    right_layout.addWidget(detect_card)
    right_layout.addSpacing(8)

    # =====================================================
    # PRIVACY
    # =====================================================

    privacy_card = QFrame()
    privacy_card.setObjectName("Card")

    privacy_layout = QVBoxLayout(privacy_card)
    privacy_layout.setSpacing(8)

    privacy_title = QLabel("Privacy")
    privacy_title.setObjectName("CardTitle")

    self.blur_slider_label = QLabel(
        f"Blur Strength : {self.blur_strength}"
    )

    self.blur_slider = QSlider(Qt.Horizontal)
    self.blur_slider.setRange(1, 100)
    self.blur_slider.setValue(self.blur_strength)
    self.blur_slider.valueChanged.connect(
        self.on_blur_slider_changed
    )

    privacy_layout.addWidget(privacy_title)
    privacy_layout.addWidget(self.blur_slider_label)
    privacy_layout.addWidget(self.blur_slider)
    privacy_group = QGroupBox("Sensitive Objects")
    privacy_group.setCheckable(True)
    privacy_group.setChecked(True)
    privacy_group.setFlat(False)

    group_layout = QVBoxLayout(privacy_group)

    self.object_checkboxes = {}

    for obj in self.yolo.sensitive_objects:

        cb = QCheckBox(obj)

        cb.setChecked(self.yolo.sensitive_objects[obj])

        cb.stateChanged.connect(
            lambda state, name=obj:
            self.on_sensitive_class_toggled(
                name,
                state
            )
        )

        self.object_checkboxes[obj] = cb

        group_layout.addWidget(cb)

    self.scan_button = QPushButton("🔍 Privacy Scan")
    self.scan_button.clicked.connect(self.scan_text)

    privacy_layout.addWidget(privacy_group)

    privacy_layout.addSpacing(10)

    privacy_layout.addWidget(self.scan_button)

    right_layout.addWidget(privacy_card)
    right_layout.addSpacing(8)

    # =====================================================
    # LIVE STATS
    # =====================================================

    stats = QFrame()
    stats.setObjectName("Card")

    stats_layout = QGridLayout(stats)
    stats_layout.setHorizontalSpacing(12)
    stats_layout.setVerticalSpacing(12)
    stats_layout.setContentsMargins(10, 10, 10, 10)

    def stat(title, value):

        frame = QFrame()
        frame.setMinimumHeight(85)
        frame.setObjectName("StatCard")

        layout = QVBoxLayout(frame)

        value_label = QLabel(value)
        value_label.setObjectName("StatValue")

        title_label = QLabel(title)
        title_label.setObjectName("StatLabel")

        layout.addWidget(value_label)
        layout.addWidget(title_label)

        return frame, value_label

    fps_card, self.fps_value = stat("FPS", "--")
    face_card, self.faces_value = stat("Faces", "0")
    obj_card, self.objects_value = stat("Objects", "0")
    txt_card, self.text_value = stat("Sensitive", "0")
    privacy_stat, self.privacy_value = stat("Privacy", "100")
    threat_stat, self.threat_value = stat("Threat", "LOW")

    stats_layout.addWidget(fps_card, 0, 0)
    stats_layout.addWidget(face_card, 0, 1)
    stats_layout.addWidget(obj_card, 1, 0)
    stats_layout.addWidget(txt_card, 1, 1)
    stats_layout.addWidget(privacy_stat, 2, 0)
    stats_layout.addWidget(threat_stat, 2, 1)

    right_layout.addWidget(stats)
    right_layout.addSpacing(8)

    # =====================================================
    # ACTIVITY
    # =====================================================

    activity = QFrame()
    activity.setObjectName("Card")

    activity_layout = QVBoxLayout(activity)
    activity_layout.setSpacing(10)

    activity_title = QLabel("Activity Center")
    activity_title.setObjectName("CardTitle")

    self.logs = QTextEdit()
    self.logs.setMinimumHeight(250)
    self.logs.setPlaceholderText(
        "Recent detections will appear here..."
    )
    self.logs.setReadOnly(True)
    self.logs.setLineWrapMode(
    QTextEdit.WidgetWidth
)

    activity_layout.addWidget(activity_title)
    activity_layout.addWidget(self.logs)

    right_layout.addWidget(activity, stretch=1)

    # =====================================================
    # STATUS
    # =====================================================

    status = QFrame()
    status.setObjectName("StatusBar")

    status_layout = QHBoxLayout(status)

    self.status = QLabel("Ready")
    self.status.setObjectName("StatusLabel")

    self.session_info = QLabel("Camera: Offline")
    self.session_info.setObjectName("StatusLabel")

    self.model_status = QLabel("AI Ready")
    self.model_status.setObjectName("StatusGood")

    status_layout.addWidget(self.status)
    status_layout.addStretch()
    status_layout.addWidget(self.session_info)
    status_layout.addSpacing(15)
    status_layout.addWidget(self.model_status)

    right_layout.addWidget(status)
    right_layout.addStretch()

# ==========================================================
# FINISH UI
# ==========================================================

def finish_layout(self):

    self.setLayout(self.main_layout)

    # Open Home page on startup
    self.stack.setCurrentWidget(self.home_page)

    # Initial activity messages
    self.logs.append("OMPD Started")
    self.logs.append("YOLO Model Loaded")
    self.logs.append("OCR Engine Loaded")
    self.logs.append("Waiting for camera...")

    # Initial status
    self.status.setText("Application Ready")