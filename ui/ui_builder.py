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
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit
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
    logo.setFocusPolicy(Qt.NoFocus)

    subtitle = QLabel("PrivacyLens")
    subtitle.setAlignment(Qt.AlignCenter)
    subtitle.setObjectName("Subtitle")
    subtitle.setFocusPolicy(Qt.NoFocus)

    sidebar_layout.addWidget(logo)
    sidebar_layout.addWidget(subtitle)

    sidebar_layout.addSpacing(25)

    self.dashboard_btn = QPushButton("🏠 Dashboard")
    self.scan_btn = QPushButton("🔍 Privacy Scan")
    self.activity_btn = QPushButton("📋 Activity Center")
    self.history_btn = QPushButton("📜 History")
    self.analytics_btn = QPushButton("📈 Analytics")
    self.settings_btn = QPushButton("⚙ Settings")
    self.about_btn = QPushButton("ℹ About")

    buttons = [
        self.dashboard_btn,
        self.scan_btn,
        self.activity_btn,
        self.history_btn,
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

    self.history_btn.clicked.connect(
        lambda: (
            self.refresh_history(),
            self.stack.setCurrentWidget(
                self.history_page
            )
        )
    )

    self.analytics_btn.clicked.connect(
        lambda: (
            self.update_analytics(),
            self.stack.setCurrentWidget(
                self.analytics_page
            )
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
    build_scan_page(self)

    self.activity_page = QWidget()
    build_activity_page(self)

    self.history_page = QWidget()
    build_history_page(self)

    self.analytics_page = QWidget()
    build_analytics_page(self)

    self.settings_page = QWidget()
    build_settings_page(self)

    self.about_page = QWidget()
    build_about_page(self)

    self.stack.addWidget(self.home_page)
    self.stack.addWidget(self.scan_page)
    self.stack.addWidget(self.activity_page)
    self.stack.addWidget(self.history_page)
    self.stack.addWidget(self.analytics_page)
    self.stack.addWidget(self.settings_page)
    self.stack.addWidget(self.about_page)

    self.stack.setCurrentWidget(self.home_page)

    self.main_layout.addWidget(self.stack, stretch=1)

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

def build_scan_page(self):

    scan_layout = QVBoxLayout(self.scan_page)

    scan_layout.setContentsMargins(20, 20, 20, 20)
    scan_layout.setSpacing(20)

    # =====================================================
    # HEADER
    # =====================================================

    header_frame = QFrame()
    header_frame.setObjectName("TopBar")

    header_layout = QHBoxLayout(header_frame)
    header_layout.setContentsMargins(15, 10, 15, 10)

    header_label = QLabel(
        "🔍 Privacy Scan   <span style='font-size:15px;color:#8A8F98;'>:: Analyze an image before sharing</span>"
    )

    header_label.setObjectName("Title")
    header_label.setTextFormat(Qt.RichText)

    header_layout.addWidget(header_label)
    header_layout.addStretch()

    self.scan_health = QLabel("Privacy Health : SAFE")
    self.scan_health.setObjectName("StatusGood")

    header_layout.addWidget(self.scan_health)

    scan_layout.addWidget(header_frame)

    # =====================================================
    # MAIN BODY
    # =====================================================

    body = QHBoxLayout()
    body.setSpacing(18)

    left_side = QVBoxLayout()
    left_side.setSpacing(18)

    # =====================================================
    # IMAGE PREVIEW
    # =====================================================

    left = QFrame()
    left.setObjectName("Card")

    left_layout = QVBoxLayout(left)
    left_layout.setContentsMargins(12,12,12,12)
    left_layout.setSpacing(10)

    self.preview_title = QLabel("🖼 Uploaded Image")
    self.preview_title.setObjectName("CardTitle")

    self.scan_preview = QLabel()
    self.scan_preview.setObjectName("CameraPreview")

    self.scan_preview.setMinimumHeight(520)

    self.scan_preview.setAlignment(Qt.AlignCenter)

    self.scan_preview.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Expanding
    )

    self.scan_preview.setText(
        "No image captured.\n\nUpload an image or Scan Text."
    )

    left_layout.addWidget(self.preview_title)
    left_layout.addWidget(self.scan_preview)

    left_side.addWidget(left,3)

    # =====================================================
    # RESULTS TABLE
    # =====================================================

    results_card = QFrame()
    results_card.setObjectName("Card")

    results_layout = QVBoxLayout(results_card)
    results_layout.setContentsMargins(12,12,12,12)

    results_title = QLabel("Detected Privacy Risks")
    results_title.setObjectName("CardTitle")

    self.scan_results = QTableWidget()

    self.scan_results.setColumnCount(4)

    self.scan_results.setHorizontalHeaderLabels([
        "Category",
        "Detected Item",
        "Risk",
        "Confidence"
    ])

    self.scan_results.horizontalHeader().setSectionResizeMode(
        QHeaderView.Stretch
    )

    self.scan_results.verticalHeader().setVisible(False)

    self.scan_results.setAlternatingRowColors(True)

    self.scan_results.setSelectionBehavior(
        QTableWidget.SelectRows
    )

    self.scan_results.setEditTriggers(
        QTableWidget.NoEditTriggers
    )

    self.scan_results.setMinimumHeight(220)

    results_layout.addWidget(results_title)
    results_layout.addWidget(self.scan_results)

    left_side.addWidget(results_card,2)

    body.addLayout(left_side,7)

    # =====================================================
    # RIGHT PANEL
    # =====================================================

    right = QFrame()
    right.setObjectName("Card")

    right.setMinimumWidth(340)
    right.setMaximumWidth(360)

    right_layout = QVBoxLayout(right)

    right_layout.setContentsMargins(15,15,15,15)
    right_layout.setSpacing(16)

    health_title = QLabel("📊 Privacy Analysis")
    health_title.setObjectName("CardTitle")

    right_layout.addWidget(health_title)

    # =====================================================
    # BUTTONS
    # =====================================================

    self.scan_text_button = QPushButton("📄 Scan Text")
    self.upload_button = QPushButton("🖼 Upload Image")
    self.save_button = QPushButton("💾 Save Safe Image")
    self.report_button = QPushButton("📋 Export Report")

    button_grid = QGridLayout()
    button_grid.setHorizontalSpacing(10)
    button_grid.setVerticalSpacing(10)

    for btn in (
        self.scan_text_button,
        self.upload_button,
        self.save_button,
        self.report_button
    ):

        btn.setMinimumHeight(48)

        btn.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

    button_grid.addWidget(self.scan_text_button,0,0)
    button_grid.addWidget(self.upload_button,0,1)
    button_grid.addWidget(self.save_button,1,0)
    button_grid.addWidget(self.report_button,1,1)

    right_layout.addLayout(button_grid)

    # =====================================================
    # PRIVACY STATUS
    # =====================================================

    self.scan_score = QLabel("Privacy Score : 100")
    self.scan_score.setObjectName("StatValue")

    self.scan_threat = QLabel("Threat : LOW")

    right_layout.addWidget(self.scan_score)
    right_layout.addWidget(self.scan_threat)

    stats_card = QFrame()
    stats_card.setObjectName("Card")

    stats = QGridLayout(stats_card)

    self.scan_sensitive = QLabel("📄 Sensitive : 0")
    self.scan_time = QLabel("🕒 Last Scan : --")

    stats.addWidget(self.scan_sensitive,0,0)
    stats.addWidget(self.scan_time,0,1)

    right_layout.addWidget(stats_card)

    # =====================================================
    # AI RECOMMENDATION
    # =====================================================

    recommendation = QFrame()
    recommendation.setObjectName("Card")

    recommendation_layout = QVBoxLayout(recommendation)

    recommendation_title = QLabel("🧠 AI Recommendation")
    recommendation_title.setObjectName("CardTitle")

    self.scan_recommendation = QTextEdit()

    self.scan_recommendation.setReadOnly(True)

    self.scan_recommendation.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Expanding
    )

    self.scan_recommendation.setText(
        "Capture or upload an image to begin the privacy analysis."
    )

    recommendation_layout.addWidget(recommendation_title)
    recommendation_layout.addWidget(self.scan_recommendation)

    right_layout.addWidget(recommendation)

    right_layout.addStretch()

    body.addWidget(right,3)

    scan_layout.addLayout(body)

    # =====================================================
    # CONNECTIONS
    # =====================================================

    self.scan_text_button.clicked.connect(
        self.scan_text
    )

    self.upload_button.clicked.connect(
        self.upload_image
    )

    self.save_button.clicked.connect(
        self.save_safe_image
    )

    self.report_button.clicked.connect(
        self.export_report
    )

def build_activity_page(self):

    activity_layout = QVBoxLayout(self.activity_page)

    activity_layout.setContentsMargins(20, 20, 20, 20)
    activity_layout.setSpacing(20)

    # =====================================================
    # HEADER
    # =====================================================

    header = QFrame()
    header.setObjectName("TopBar")

    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(15, 10, 15, 10)

    title = QLabel(
        "📋 Activity Center   "
        "<span style='font-size:15px;color:#8A8F98;'>"
        ":: Live privacy events and detections"
        "</span>"
    )

    title.setObjectName("Title")
    title.setTextFormat(Qt.RichText)

    header_layout.addWidget(title)
    header_layout.addStretch()

    self.activity_status = QLabel("Monitoring")
    self.activity_status.setObjectName("StatusGood")

    header_layout.addWidget(self.activity_status)

    activity_layout.addWidget(header)

    # =====================================================
    # TOOLBAR
    # =====================================================

    toolbar = QFrame()
    toolbar.setObjectName("Card")

    toolbar_layout = QHBoxLayout(toolbar)
    toolbar_layout.setContentsMargins(12, 12, 12, 12)

    self.activity_search = QLineEdit()
    self.activity_search.setPlaceholderText(
        "Search activity..."
    )

    self.activity_filter = QComboBox()
    self.activity_filter.addItems([
        "All",
        "Faces",
        "Objects",
        "Sensitive Text",
        "Warnings"
    ])

    self.clear_activity_btn = QPushButton("🗑 Clear")
    self.export_activity_btn = QPushButton("💾 Export CSV")
    self.refresh_activity_btn = QPushButton("🔄 Refresh")

    toolbar_layout.addWidget(self.activity_search, 3)
    toolbar_layout.addWidget(self.activity_filter, 1)
    toolbar_layout.addWidget(self.refresh_activity_btn)
    toolbar_layout.addWidget(self.export_activity_btn)
    toolbar_layout.addWidget(self.clear_activity_btn)

    activity_layout.addWidget(toolbar)

    # =====================================================
    # LIVE STATISTICS
    # =====================================================

    stats = QGridLayout()

    def stat_card(title, value):

        card = QFrame()
        card.setObjectName("StatCard")
        card.setMinimumHeight(90)

        layout = QVBoxLayout(card)

        value_label = QLabel(value)
        value_label.setObjectName("StatValue")

        title_label = QLabel(title)
        title_label.setObjectName("StatLabel")

        layout.addWidget(value_label)
        layout.addWidget(title_label)

        return card, value_label

    total_card, self.activity_total = stat_card(
        "Today's Events",
        "0"
    )

    face_card, self.activity_faces = stat_card(
        "Faces",
        "0"
    )

    object_card, self.activity_objects = stat_card(
        "Objects",
        "0"
    )

    text_card, self.activity_text = stat_card(
        "Sensitive Text",
        "0"
    )

    stats.addWidget(total_card, 0, 0)
    stats.addWidget(face_card, 0, 1)
    stats.addWidget(object_card, 0, 2)
    stats.addWidget(text_card, 0, 3)

    activity_layout.addLayout(stats)

    # =====================================================
    # LIVE ACTIVITY LOG
    # =====================================================

    log_card = QFrame()
    log_card.setObjectName("Card")

    log_layout = QVBoxLayout(log_card)

    log_title = QLabel("Recent Activity")
    log_title.setObjectName("CardTitle")

    self.activity_log = QTextEdit()

    self.activity_log.setReadOnly(True)

    self.activity_log.setPlaceholderText(
        "Live detections will appear here..."
    )

    self.activity_log.setMinimumHeight(300)

    log_layout.addWidget(log_title)
    log_layout.addWidget(self.activity_log)

    activity_layout.addWidget(log_card)

    # =====================================================
    # FOOTER
    # =====================================================

    footer = QFrame()
    footer.setObjectName("StatusBar")

    footer_layout = QHBoxLayout(footer)

    self.activity_footer = QLabel(
        "Waiting for detections..."
    )

    footer_layout.addWidget(self.activity_footer)
    footer_layout.addStretch()

    activity_layout.addWidget(footer)

    self.refresh_activity_btn.clicked.connect(
        self.refresh_activity
    )

    self.clear_activity_btn.clicked.connect(
        self.clear_activity
    )

    self.export_activity_btn.clicked.connect(
        self.export_activity
    )

    self.activity_search.textChanged.connect(
        self.search_activity
    )

    self.activity_filter.currentTextChanged.connect(
        self.filter_activity
    )

def build_history_page(self):

    history_layout = QVBoxLayout(self.history_page)

    history_layout.setContentsMargins(20, 20, 20, 20)
    history_layout.setSpacing(20)

    # =====================================================
    # HEADER
    # =====================================================

    header = QFrame()
    header.setObjectName("TopBar")

    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(15, 10, 15, 10)

    title = QLabel(
        "📜 History   "
        "<span style='font-size:15px;color:#8A8F98;'>"
        ":: Detection database"
        "</span>"
    )

    title.setObjectName("Title")
    title.setTextFormat(Qt.RichText)

    header_layout.addWidget(title)
    header_layout.addStretch()

    self.history_status = QLabel("Database Connected")
    self.history_status.setObjectName("StatusGood")

    header_layout.addWidget(self.history_status)

    history_layout.addWidget(header)

    # =====================================================
    # TOOLBAR
    # =====================================================

    toolbar = QFrame()
    toolbar.setObjectName("Card")

    toolbar_layout = QHBoxLayout(toolbar)
    toolbar_layout.setContentsMargins(12,12,12,12)

    self.history_search = QLineEdit()
    self.history_search.setPlaceholderText(
        "Search..."
    )

    self.history_filter = QComboBox()

    self.history_filter.addItems([
        "All",
        "Faces",
        "Objects",
        "Sensitive Text"
    ])

    self.history_refresh = QPushButton("🔄 Refresh")
    self.history_export = QPushButton("💾 Export CSV")
    self.history_delete = QPushButton("🗑 Delete Selected")
    self.history_clear = QPushButton("❌ Clear History")

    toolbar_layout.addWidget(self.history_search,3)
    toolbar_layout.addWidget(self.history_filter,1)
    toolbar_layout.addWidget(self.history_refresh)
    toolbar_layout.addWidget(self.history_export)
    toolbar_layout.addWidget(self.history_delete)
    toolbar_layout.addWidget(self.history_clear)

    history_layout.addWidget(toolbar)

    # =====================================================
    # DATABASE TABLE
    # =====================================================

    table_card = QFrame()
    table_card.setObjectName("Card")

    table_layout = QVBoxLayout(table_card)

    table_title = QLabel("Detection History")
    table_title.setObjectName("CardTitle")

    self.history_table = QTableWidget()

    self.history_table.setColumnCount(5)

    self.history_table.setHorizontalHeaderLabels([
        "Timestamp",
        "Category",
        "Detected Item",
        "Confidence",
        "Action"
    ])

    self.history_table.horizontalHeader().setStretchLastSection(True)

    self.history_table.horizontalHeader().setSectionResizeMode(
        QHeaderView.Stretch
    )

    self.history_table.verticalHeader().setVisible(False)

    self.history_table.setAlternatingRowColors(True)

    self.history_table.setSelectionBehavior(
        QTableWidget.SelectRows
    )

    self.history_table.setEditTriggers(
        QTableWidget.NoEditTriggers
    )

    self.history_table.setMinimumHeight(500)

    table_layout.addWidget(table_title)
    table_layout.addWidget(self.history_table)

    history_layout.addWidget(table_card)

    # =====================================================
    # SUMMARY
    # =====================================================

    summary = QFrame()
    summary.setObjectName("Card")

    summary_layout = QGridLayout(summary)

    summary_layout.setContentsMargins(15,15,15,15)

    self.total_records = QLabel("Total Records : 0")
    self.today_records = QLabel("Today : 0")
    self.high_risk = QLabel("High Risk : 0")
    self.last_detection = QLabel("Last Detection : --")

    summary_layout.addWidget(self.total_records,0,0)
    summary_layout.addWidget(self.today_records,0,1)
    summary_layout.addWidget(self.high_risk,1,0)
    summary_layout.addWidget(self.last_detection,1,1)

    history_layout.addWidget(summary)

    # =====================================================
    # FOOTER
    # =====================================================

    footer = QFrame()
    footer.setObjectName("StatusBar")

    footer_layout = QHBoxLayout(footer)

    self.history_footer = QLabel(
        "Ready"
    )

    footer_layout.addWidget(self.history_footer)
    footer_layout.addStretch()

    history_layout.addWidget(footer)

    self.history_refresh.clicked.connect(
        self.refresh_history
    )

    self.history_export.clicked.connect(
        self.export_history
    )

    self.history_delete.clicked.connect(
        self.delete_history
    )

    self.history_clear.clicked.connect(
        self.clear_history
    )

    self.history_search.textChanged.connect(
        self.search_history
    )

    self.history_filter.currentTextChanged.connect(
        self.filter_history
    )

def build_analytics_page(self):

    analytics_layout = QVBoxLayout(self.analytics_page)

    analytics_layout.setContentsMargins(20, 20, 20, 20)
    analytics_layout.setSpacing(10)

    # =====================================================
    # HEADER
    # =====================================================

    header = QFrame()
    header.setObjectName("TopBar")

    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(15,10,15,10)

    title = QLabel(
        "📈 Analytics   "
        "<span style='font-size:15px;color:#8A8F98;'>"
        ":: AI performance and privacy insights"
        "</span>"
    )

    title.setObjectName("Title")
    title.setTextFormat(Qt.RichText)

    header_layout.addWidget(title)
    header_layout.addStretch()

    self.analytics_status = QLabel("Live")
    self.analytics_status.setObjectName("StatusGood")

    header_layout.addWidget(self.analytics_status)

    analytics_layout.addWidget(header)

    # =====================================================
    # TOP STATISTICS
    # =====================================================

    stats = QGridLayout()
    stats.setHorizontalSpacing(20)
    stats.setVerticalSpacing(20)

    def stat_card(title, value):

        card = QFrame()
        card.setObjectName("StatCard")
        card.setMinimumHeight(85)
        card.setMinimumWidth(140)
        card.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        layout = QVBoxLayout(card)

        layout.setContentsMargins(18,18,18,18)
        layout.setSpacing(10)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName("StatValue")

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("StatLabel")

        layout.addWidget(value_label)
        layout.addWidget(title_label)

        return card, value_label

    total_card, self.analytics_total = stat_card(
        "Total Detections",
        "0"
    )

    faces_card, self.analytics_faces = stat_card(
        "Faces",
        "0"
    )

    objects_card, self.analytics_objects = stat_card(
        "Objects",
        "0"
    )

    text_card, self.analytics_text = stat_card(
        "Sensitive Text",
        "0"
    )

    privacy_card, self.analytics_privacy = stat_card(
        "Privacy Score",
        "100"
    )

    fps_card, self.analytics_fps = stat_card(
        "Average FPS",
        "--"
    )

    stats.addWidget(total_card,0,0)
    stats.addWidget(faces_card,0,1)
    stats.addWidget(objects_card,0,2)

    stats.addWidget(text_card,1,0)
    stats.addWidget(privacy_card,1,1)
    stats.addWidget(fps_card,1,2)

    analytics_layout.addLayout(stats)

    # =====================================================
    # CHART PLACEHOLDERS
    # =====================================================

    charts = QHBoxLayout()
    charts.setSpacing(15)

    # Detection Trend

    trend_card = QFrame()
    trend_card.setMinimumHeight(100)

    trend_card.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Expanding
    )
    trend_card.setObjectName("Card")

    trend_layout = QVBoxLayout(trend_card)

    trend_title = QLabel("Detection Trend")
    trend_title.setObjectName("CardTitle")

    self.trend_chart = QLabel()

    self.trend_chart.setAlignment(Qt.AlignCenter)
    self.trend_chart.setMinimumHeight(250)

    self.trend_chart.setText(
        "Detection Trend Chart\n\n(Matplotlib / QtChart)"
    )

    trend_layout.addWidget(trend_title)
    trend_layout.addWidget(self.trend_chart)

    charts.addWidget(trend_card)

    # Object Distribution

    object_card = QFrame()
    object_card.setMinimumHeight(100)

    object_card.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Expanding
    )
    object_card.setObjectName("Card")

    object_layout = QVBoxLayout(object_card)

    object_title = QLabel("Object Distribution")
    object_title.setObjectName("CardTitle")

    self.object_chart = QLabel()

    self.object_chart.setAlignment(Qt.AlignCenter)
    self.object_chart.setMinimumHeight(250)

    self.object_chart.setText(
        "Object Distribution Chart"
    )

    object_layout.addWidget(object_title)
    object_layout.addWidget(self.object_chart)

    charts.addWidget(object_card)

    analytics_layout.addLayout(charts)

    # =====================================================
    # SYSTEM INFORMATION
    # =====================================================

    system_card = QFrame()
    system_card.setObjectName("Card")

    system_layout = QGridLayout(system_card)

    system_layout.setContentsMargins(20,20,20,20)

    system_layout.setHorizontalSpacing(40)

    system_layout.setVerticalSpacing(18)

    self.device_info = QLabel("AI Device : CUDA")
    self.model_info = QLabel("Model : YOLOv8n")
    self.camera_info = QLabel("Camera : Offline")
    self.database_info = QLabel("Database : Connected")
    self.runtime_info = QLabel("Runtime : PyTorch CUDA")
    self.version_info = QLabel("Version : 1.0")

    system_layout.addWidget(self.device_info,0,0)
    system_layout.addWidget(self.model_info,0,1)

    system_layout.addWidget(self.camera_info,1,0)
    system_layout.addWidget(self.database_info,1,1)

    system_layout.addWidget(self.runtime_info,2,0)
    system_layout.addWidget(self.version_info,2,1)

    analytics_layout.addWidget(system_card)

    # =====================================================
    # INSIGHTS
    # =====================================================

    insights = QFrame()
    insights.setObjectName("Card")

    insights_layout = QVBoxLayout(insights)

    insights_title = QLabel("🧠 AI Insights")
    insights_title.setObjectName("CardTitle")

    self.analytics_insights = QTextEdit()

    self.analytics_insights.setReadOnly(True)

    self.analytics_insights.setMinimumHeight(120)

    self.analytics_insights.setText(
        "AI insights will appear here.\n\n"
        "• Most frequently detected object\n"
        "• Highest privacy risk\n"
        "• Detection trends\n"
        "• Performance summary"
    )

    insights_layout.addWidget(insights_title)
    insights_layout.addWidget(self.analytics_insights)

    analytics_layout.addWidget(insights)

    # =====================================================
    # FOOTER
    # =====================================================

    footer = QFrame()
    footer.setObjectName("StatusBar")

    footer_layout = QHBoxLayout(footer)

    self.analytics_footer = QLabel(
        "Analytics Ready"
    )

    footer_layout.addWidget(self.analytics_footer)
    footer_layout.addStretch()

    analytics_layout.addSpacing(10)

    analytics_layout.addWidget(footer)

def build_settings_page(self):

    settings_layout = QVBoxLayout(self.settings_page)

    settings_layout.setContentsMargins(20,20,20,20)
    settings_layout.setSpacing(20)

    # =====================================================
    # HEADER
    # =====================================================

    header = QFrame()
    header.setObjectName("TopBar")

    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(15,10,15,10)

    title = QLabel(
        "⚙ Settings   "
        "<span style='font-size:15px;color:#8A8F98;'>"
        ":: Configure OMPD"
        "</span>"
    )

    title.setObjectName("Title")
    title.setTextFormat(Qt.RichText)

    header_layout.addWidget(title)
    header_layout.addStretch()

    self.settings_status = QLabel("Ready")
    self.settings_status.setObjectName("StatusGood")

    header_layout.addWidget(self.settings_status)

    settings_layout.addWidget(header)

    # =====================================================
    # SCROLL AREA
    # =====================================================

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)

    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.setSpacing(20)

    # =====================================================
    # CAMERA SETTINGS
    # =====================================================

    camera_card = QFrame()
    camera_card.setObjectName("Card")

    camera_layout = QVBoxLayout(camera_card)

    camera_title = QLabel("📷 Camera")
    camera_title.setObjectName("CardTitle")

    self.settings_camera = QComboBox()
    self.settings_camera.addItems([
        "Camera 0",
        "Camera 1"
    ])

    self.settings_resolution = QComboBox()
    self.settings_resolution.addItems([
        "640 × 480",
        "1280 × 720",
        "1920 × 1080"
    ])

    camera_layout.addWidget(camera_title)
    camera_layout.addWidget(QLabel("Camera"))
    camera_layout.addWidget(self.settings_camera)
    camera_layout.addWidget(QLabel("Resolution"))
    camera_layout.addWidget(self.settings_resolution)

    container_layout.addWidget(camera_card)

    # =====================================================
    # PERFORMANCE
    # =====================================================

    performance_card = QFrame()
    performance_card.setObjectName("Card")

    performance_layout = QVBoxLayout(performance_card)

    performance_title = QLabel("⚡ Performance")
    performance_title.setObjectName("CardTitle")

    self.settings_confidence = QLabel(
        f"YOLO Confidence : {self.yolo_conf:.2f}"
    )

    self.settings_conf_slider = QSlider(Qt.Horizontal)
    self.settings_conf_slider.setRange(0,100)
    self.settings_conf_slider.setValue(
        int(self.yolo_conf*100)
    )
    self.settings_conf_slider.valueChanged.connect(
        self.settings_confidence_changed
    )

    self.settings_blur = QLabel(
        f"Blur Strength : {self.blur_strength}"
    )

    self.settings_blur_slider = QSlider(Qt.Horizontal)
    self.settings_blur_slider.setRange(1,100)
    self.settings_blur_slider.setValue(
        self.blur_strength
    )
    self.settings_blur_slider.valueChanged.connect(
        self.settings_blur_changed
    )

    performance_layout.addWidget(performance_title)
    performance_layout.addWidget(self.settings_confidence)
    performance_layout.addWidget(self.settings_conf_slider)
    performance_layout.addSpacing(10)
    performance_layout.addWidget(self.settings_blur)
    performance_layout.addWidget(self.settings_blur_slider)

    performance_layout.addSpacing(20)

    privacy_group = QGroupBox("Sensitive Objects")

    group_layout = QGridLayout(privacy_group)

    group_layout.setHorizontalSpacing(25)
    group_layout.setVerticalSpacing(8)

    self.settings_object_checkboxes = {}

    row = 0
    col = 0

    for obj in self.yolo.sensitive_objects:

        cb = QCheckBox(obj)

        cb.setChecked(
            self.yolo.sensitive_objects[obj]
        )

        cb.stateChanged.connect(
            lambda state, name=obj:
            self.on_sensitive_class_toggled(
                name,
                state
            )
        )

        self.settings_object_checkboxes[obj] = cb

        group_layout.addWidget(
            cb,
            row,
            col
        )

        col += 1

        if col == 2:

            row += 1
            col = 0

    performance_layout.addWidget(
        privacy_group
    )

    container_layout.addWidget(performance_card)

    # =====================================================
    # DATABASE
    # =====================================================

    db_card = QFrame()
    db_card.setObjectName("Card")

    db_layout = QVBoxLayout(db_card)

    db_title = QLabel("🗄 Database")
    db_title.setObjectName("CardTitle")

    self.export_database = QPushButton(
        "💾 Export Database"
    )

    self.backup_database = QPushButton(
        "📦 Backup Database"
    )

    self.clear_database = QPushButton(
        "🗑 Clear Database"
    )

    db_layout.addWidget(db_title)
    db_layout.addWidget(self.export_database)
    db_layout.addWidget(self.backup_database)
    db_layout.addWidget(self.clear_database)

    container_layout.addWidget(db_card)

    # =====================================================
    # SAVE / RESET
    # =====================================================

    buttons = QHBoxLayout()

    self.save_settings = QPushButton(
        "💾 Save Settings"
    )

    self.reset_settings = QPushButton(
        "🔄 Restore Defaults"
    )

    buttons.addStretch()
    buttons.addWidget(self.reset_settings)
    buttons.addWidget(self.save_settings)

    container_layout.addLayout(buttons)

    scroll.setWidget(container)

    settings_layout.addWidget(scroll)

    self.save_settings.clicked.connect(
        self.save_settings_clicked
    )

    self.reset_settings.clicked.connect(
        self.reset_settings_clicked
    )

    self.export_database.clicked.connect(
        self.export_database_clicked
    )

    self.backup_database.clicked.connect(
        self.backup_database_clicked
    )

    self.clear_database.clicked.connect(
        self.clear_database_clicked
    )

def build_about_page(self):

    about_layout = QVBoxLayout(self.about_page)

    about_layout.setContentsMargins(20, 20, 20, 20)
    about_layout.setSpacing(18)

    # =====================================================
    # HEADER
    # =====================================================

    header = QFrame()
    header.setObjectName("TopBar")

    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(15, 10, 15, 10)

    title = QLabel(
        "ℹ About OMPD   "
        "<span style='font-size:15px;color:#8A8F98;'>"
        ":: On-Device Privacy Monitoring"
        "</span>"
    )

    title.setObjectName("Title")
    title.setTextFormat(Qt.RichText)

    header_layout.addWidget(title)
    header_layout.addStretch()

    self.about_status = QLabel("Version 1.0")
    self.about_status.setObjectName("StatusGood")

    header_layout.addWidget(self.about_status)

    about_layout.addWidget(header)

    # =====================================================
    # TOP SECTION
    # =====================================================

    top = QHBoxLayout()
    top.setSpacing(18)

    # -----------------------------------------------------

    project_card = QFrame()
    project_card.setObjectName("Card")

    project_layout = QVBoxLayout(project_card)
    project_layout.setContentsMargins(18,18,18,18)

    logo = QLabel("🛡")
    logo.setAlignment(Qt.AlignCenter)
    logo.setStyleSheet("font-size:72px;")

    project_name = QLabel("OMPD")
    project_name.setObjectName("Title")
    project_name.setAlignment(Qt.AlignCenter)

    subtitle = QLabel(
        "On-Device Privacy Monitoring & Detection"
    )
    subtitle.setAlignment(Qt.AlignCenter)

    description = QTextEdit()
    description.setReadOnly(True)
    description.setMinimumHeight(210)

    description.setText(
        "OMPD protects user privacy using "
        "completely on-device AI.\n\n"

        "Features include:\n\n"

        "• Face Detection & Blur\n"
        "• Sensitive Object Detection\n"
        "• OCR-Based Privacy Detection\n"
        "• QR Code Detection\n"
        "• Privacy Analytics\n"
        "• Activity Logging\n"
        "• History Management\n\n"

        "No cloud processing.\n"
        "Everything stays on your device."
    )

    project_layout.addWidget(logo)
    project_layout.addWidget(project_name)
    project_layout.addWidget(subtitle)
    project_layout.addSpacing(10)
    project_layout.addWidget(description)

    top.addWidget(project_card,3)

    # -----------------------------------------------------

    tech_card = QFrame()
    tech_card.setObjectName("Card")

    tech_layout = QGridLayout(tech_card)
    tech_layout.setContentsMargins(18,18,18,18)
    tech_layout.setHorizontalSpacing(30)
    tech_layout.setVerticalSpacing(14)

    rows = [
        ("YOLO Model","YOLOv8n"),
        ("OCR Engine","EasyOCR"),
        ("Face Detection","MediaPipe"),
        ("GUI","PySide6"),
        ("Computer Vision","OpenCV"),
        ("AI Runtime","PyTorch CUDA"),
        ("Database","SQLite")
    ]

    for r,(k,v) in enumerate(rows):

        tech_layout.addWidget(QLabel(k),r,0)
        tech_layout.addWidget(QLabel(v),r,1)

    top.addWidget(tech_card,2)

    about_layout.addLayout(top)

    # =====================================================
    # LOWER SECTION
    # =====================================================

    bottom = QHBoxLayout()
    bottom.setSpacing(18)

    # -----------------------------------------------------

    system_card = QFrame()
    system_card.setObjectName("Card")

    system_layout = QGridLayout(system_card)

    system_layout.setContentsMargins(18,18,18,18)
    system_layout.setHorizontalSpacing(35)
    system_layout.setVerticalSpacing(14)

    self.about_gpu = QLabel("GPU : NVIDIA RTX 4050")
    self.about_device = QLabel("Device : CUDA")
    self.about_python = QLabel("Python : 3.11")
    self.about_opencv = QLabel("OpenCV : 4.10")
    self.about_database = QLabel("Database : SQLite")
    self.about_runtime = QLabel("Runtime : Local")

    system_layout.addWidget(self.about_gpu,0,0)
    system_layout.addWidget(self.about_device,0,1)

    system_layout.addWidget(self.about_python,1,0)
    system_layout.addWidget(self.about_opencv,1,1)

    system_layout.addWidget(self.about_database,2,0)
    system_layout.addWidget(self.about_runtime,2,1)

    bottom.addWidget(system_card)

    # -----------------------------------------------------

    feature_card = QFrame()
    feature_card.setObjectName("Card")

    feature_layout = QVBoxLayout(feature_card)
    feature_layout.setContentsMargins(18,18,18,18)

    feature_title = QLabel("Features")
    feature_title.setObjectName("CardTitle")

    features = QTextEdit()
    features.setReadOnly(True)

    features.setText(
        "✓ Real-Time Face Protection\n"
        "✓ Sensitive Object Detection\n"
        "✓ OCR Privacy Protection\n"
        "✓ QR Code Detection\n"
        "✓ GPU Acceleration\n"
        "✓ SQLite Logging\n"
        "✓ Analytics Dashboard\n"
        "✓ Privacy Scan\n"
        "✓ Activity Center\n"
        "✓ History Management\n"
        "✓ Export Reports\n"
        "✓ Fully On-Device AI"
    )

    feature_layout.addWidget(feature_title)
    feature_layout.addWidget(features)

    bottom.addWidget(feature_card)

    about_layout.addLayout(bottom)

    # =====================================================
    # FOOTER
    # =====================================================

    footer = QFrame()
    footer.setObjectName("StatusBar")

    footer_layout = QHBoxLayout(footer)

    copyright = QLabel(
        "© 2026 OMPD • Built for OSDHack 2026"
    )

    github = QPushButton("GitHub")
    license_btn = QPushButton("License")

    footer_layout.addWidget(copyright)
    footer_layout.addStretch()
    footer_layout.addWidget(github)
    footer_layout.addWidget(license_btn)

    about_layout.addWidget(footer)

    github.clicked.connect(self.open_github)
    license_btn.clicked.connect(self.open_license)

def build_right_panel(self):

    self.right_panel = QFrame()
    self.right_panel.setObjectName("RightPanel")
    self.right_panel.setMinimumWidth(420)
    self.right_panel.setMaximumWidth(520)

    right_layout = QVBoxLayout(self.right_panel)
    right_layout.setContentsMargins(10, 10, 10, 10)
    right_layout.setSpacing(15)

    # =====================================================
    # DETECTION
    # =====================================================

    detect_card = QFrame()
    detect_card.setObjectName("Card")

    detect_layout = QVBoxLayout(detect_card)
    detect_layout.setSpacing(8)

    detect_title = QLabel("🎛 Controls")
    detect_title.setObjectName("CardTitle")

    self.camera_button = QPushButton(" Start Camera")

    self.face_blur = QPushButton("Face Blur : ON")
    self.object_blur = QPushButton("Object Blur : ON")
    self.ocr = QPushButton("OCR : ON")
    self.barcode_blur = QPushButton("Barcode : ON")

    self.camera_button.clicked.connect(self.toggle_camera)
    self.face_blur.clicked.connect(self.toggle_face_blur)
    self.object_blur.clicked.connect(self.toggle_object_blur)
    self.ocr.clicked.connect(self.toggle_ocr)
    self.barcode_blur.clicked.connect(self.toggle_barcode_blur)

    # NOTE: The Confidence slider (self.conf_slider /
    # self.conf_slider_label) is still created below so the
    # rest of the app (reset_settings_clicked,
    # save_settings_clicked, on_conf_slider_changed, etc.)
    # keeps working, but it is intentionally NOT added to the
    # Dashboard's Controls card layout anymore, per request.
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

    grid = QGridLayout()
    grid.setHorizontalSpacing(10)
    grid.setVerticalSpacing(10)

    for btn in (
        self.camera_button,
        self.face_blur,
        self.object_blur,
        self.ocr,
        self.barcode_blur,
    ):
        btn.setMinimumHeight(50)
        btn.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

    # Start Camera is now the big, full-width button
    # (same size/role the Barcode button used to have).
    grid.addWidget(self.camera_button,0,0,1,2)

    # Barcode is now a regular half-width button, grouped
    # with the other toggle buttons.
    grid.addWidget(self.face_blur,1,0)
    grid.addWidget(self.object_blur,1,1)
    grid.addWidget(self.ocr,2,0)
    grid.addWidget(self.barcode_blur,2,1)

    detect_layout.addLayout(grid)

    # Confidence slider intentionally removed from the
    # Dashboard page's Controls card.

    right_layout.addWidget(detect_card)
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

    # NOTE: self.fps_value is still created so update_frame()
    # in dashboard.py can keep updating it safely, but the FPS
    # card itself is no longer added to the Dashboard grid
    # below (removed per request).
    fps_card, self.fps_value = stat("FPS", "--")
    face_card, self.faces_value = stat("Faces", "0")
    obj_card, self.objects_value = stat("Objects", "0")
    txt_card, self.text_value = stat("Sensitive", "0")
    privacy_stat, self.privacy_value = stat("Privacy", "100")
    threat_stat, self.threat_value = stat("Threat", "LOW")
    barcode_card, self.barcode_value = stat("Barcodes", "0")

    stats_layout.addWidget(face_card, 0, 0)
    stats_layout.addWidget(obj_card, 0, 1)
    stats_layout.addWidget(txt_card, 1, 0)
    stats_layout.addWidget(privacy_stat, 1, 1)
    stats_layout.addWidget(threat_stat, 2, 0)
    stats_layout.addWidget(barcode_card, 2, 1)

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
    self.refresh_history()
    self.refresh_activity()
    self.update_analytics()