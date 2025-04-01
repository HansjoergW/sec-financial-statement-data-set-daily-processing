from abc import ABC, abstractmethod
from typing import List, Tuple

import pandas as pd


class SecError:
    def __init__(self, adsh: str, report_role: str, error: str):
        self.adsh = adsh
        self.report_role = report_role
        self.error = error

    def printentry(self):
        print(self.adsh, " - ", self.report_role, " - ", self.error)


class SecXmlParserBase(ABC):

    def __init__(self, type: str):
        self.type = type

    def get_type(self):
        return self.type

    @abstractmethod
    def parse(self, adsh: str, data: str) -> Tuple[pd.DataFrame, List[SecError]]:
        pass


