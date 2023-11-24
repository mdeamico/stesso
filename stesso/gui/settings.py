from PySide2.QtGui import QFont, QFontMetrics

class GUIConfig:
    """Class holds configuration variables.
    
    Call module-level init() function to import user-defined config dictionary.
    
    List all class variables, user-supplied and derived, to show them 
    in the IDE auto-complete.
    """
    FONT_NAME = "consolas"
    FONT_SIZE = 9
    FONT_ANTIALIAS = 2.0
    
    # Derived config variables
    QFONT = None
    QFONTMETRICS = None
    FONT_HEIGHT = 0
    CHAR_WIDTH = 0
    CAP_HEIGHT = 0
    AA_CHAR_WIDTH = 0
    AA_CAP_HEIGHT = 0

# TODO: Need a more elegant way of handling settings.
# As another hack, try adding module-level names:
# https://stackoverflow.com/questions/1429814/how-to-programmatically-set-a-global-module-variable


def init():
    """Function sets values for the GUIConfig class-level variables."""
    GUIConfig.QFONT = QFont(GUIConfig.FONT_NAME, GUIConfig.FONT_SIZE)

    # Derived config
    GUIConfig.QFONTMETRICS = QFontMetrics(GUIConfig.QFONT)
    GUIConfig.FONT_HEIGHT = GUIConfig.QFONTMETRICS.height()
    GUIConfig.CHAR_WIDTH = GUIConfig.QFONTMETRICS.averageCharWidth()
    GUIConfig.CAP_HEIGHT = GUIConfig.QFONTMETRICS.capHeight()

    # Font Properties for scaled (Anti-Aliased) font
    aa_font = QFont(GUIConfig.FONT_NAME, GUIConfig.FONT_SIZE * GUIConfig.FONT_ANTIALIAS)
    aa_fm = QFontMetrics(aa_font)
    GUIConfig.AA_CHAR_WIDTH = aa_fm.averageCharWidth()
    GUIConfig.AA_CAP_HEIGHT = aa_fm.capHeight()
