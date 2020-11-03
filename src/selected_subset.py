import pandas as pd
from src.dataset_gateway import Singleton


class SelectedSubset:
    class __SelectedSubset:
        def __init__(self):
            self.data = pd.DataFrame()

    instance = None

    def __init__(self):
        if not SelectedSubset.instance:
            SelectedSubset.instance = SelectedSubset.__SelectedSubset()

    def update(self, new_dataframe):
        self.instance.data = new_dataframe

    def is_empty(self):
        return self.instance.data.empty
