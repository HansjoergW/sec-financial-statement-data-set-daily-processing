from abc import ABC, abstractmethod

import pandas as pd

class SecXmlParserBase(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def parse(self, data: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def clean_for_financial_statement_dataset(self, df: pd.DataFrame, adsh: str = None) -> pd.DataFrame:
        pass