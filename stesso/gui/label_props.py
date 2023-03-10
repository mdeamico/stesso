from dataclasses import dataclass
from typing import Callable, Any

# TODO: turn data_name into an enum?

@dataclass
class LabelProps:
    editable: bool
    data_name: str
    prefix: str
    postfix: str
    formatted: Callable[[Any], str] = lambda x: f'{x}'

def target_volume(editable: bool=False) -> LabelProps:
    return(
        LabelProps(
            editable=editable,
            data_name='target_volume',
            prefix="",
            postfix="",
            formatted=lambda x: f'{x:.0f}'))

def assigned_volume(editable: bool=False) -> LabelProps:
    return(
        LabelProps(
            editable=editable,
            data_name='assigned_volume',
            prefix="<",
            postfix=">",
            formatted=lambda x: f'{x:.0f}'))

def imbalance(editable: bool=False) -> LabelProps:
    return(
        LabelProps(
            editable=editable,
            data_name='imbalance',
            prefix="[",
            postfix="]",
            formatted=lambda x: f'{x:.0f}'))