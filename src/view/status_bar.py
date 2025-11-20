from PySide6.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout
from PySide6.QtGui import QPalette, QColor

class TokenStatusBar(QStatusBar):
    """
    Custom Status Bar with CENTERED, high-contrast white metrics.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        
        self.setStyleSheet("QStatusBar { background-color: #1e1e1e; border-top: 1px solid #3d3d3d; }")

        # Container widget to hold our labels centrally
        self.container = QWidget()
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Labels
        self.file_count_label = QLabel("Files: 0")
        self.token_count_label = QLabel("Est. Tokens: 0")

        # Styling: White text, slightly bold, larger font
        base_style = "color: #ffffff; font-weight: 600; font-size: 11pt;"
        self.file_count_label.setStyleSheet(base_style)
        self.token_count_label.setStyleSheet(base_style)

        # Layout Strategy: Stretch | Label 1 | Label 2 | Stretch
        # This forces the labels to the center of the bar
        layout.addStretch()
        layout.addWidget(self.file_count_label)
        layout.addWidget(self.token_count_label)
        layout.addStretch()

        # Add the container to the status bar. 
        # '1' is the stretch factor, ensuring it consumes all available space.
        self.addWidget(self.container, 1)

    def update_metrics(self, token_count: int, file_count: int):
        """Updates the displayed metrics."""
        self.file_count_label.setText(f"Files: {file_count}")
        self.token_count_label.setText(f"Est. Tokens: {token_count}")

        # Dynamic Warning Color (Red if tokens > 32k)
        if token_count > 32000:
            self.token_count_label.setStyleSheet("color: #ff5555; font-weight: 700; font-size: 11pt;")
        else:
            self.token_count_label.setStyleSheet("color: #ffffff; font-weight: 600; font-size: 11pt;")
