from abc import ABC, abstractmethod
from typing import List, Tuple

import pandas as pd

from secdaily._00_common.ProcessBase import ErrorEntry


class SecXmlParserBase(ABC):

    def __init__(self, type: str):
        self.type = type

    def get_type(self):
        return self.type

    @abstractmethod
    def parse(self, adsh: str, data: str) -> Tuple[pd.DataFrame, List[ErrorEntry]]:
        pass
