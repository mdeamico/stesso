from PySide2.QtGui import QFont, QFontMetrics

class GUIConfig:
    FONT_NAME = "consolas"
    FONT_SIZE = 8
    
    # Derived settings set by calling init() function
    QFONT = None
    QFONTMETRICS = None
    FONT_HEIGHT = 0
    CHAR_WIDTH = 0
    CAP_HEIGHT = 0

# _config = {
#     "FONT_NAME": "consolas",
#     "FONT_SIZE": 8
# }

# TODO: Need a more elegant way of handling settings.
# As another hack, try adding module-level names:
# https://stackoverflow.com/questions/1429814/how-to-programmatically-set-a-global-module-variable

# Derived settings set by calling init() function
def init():
    GUIConfig.QFONT = QFont(GUIConfig.FONT_NAME, GUIConfig.FONT_SIZE)
    GUIConfig.QFONTMETRICS = QFontMetrics(GUIConfig.QFONT)

    GUIConfig.FONT_HEIGHT = GUIConfig.QFONTMETRICS.height()
    GUIConfig.CHAR_WIDTH = GUIConfig.QFONTMETRICS.averageCharWidth()
    GUIConfig.CAP_HEIGHT = GUIConfig.QFONTMETRICS.capHeight()