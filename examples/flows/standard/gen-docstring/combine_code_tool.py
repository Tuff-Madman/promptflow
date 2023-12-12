from promptflow import tool
from divider import Divider
from typing import List


@tool
def combine_code(divided: List[str]):
    return Divider.combine(divided)
