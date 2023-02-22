from dataclasses import dataclass
from typing import Callable

@dataclass
class TextInfo:
    editable: bool
    InfoType: str
    get_text_fn: Callable
    prefix: str
    postfix: str
