from typing import Dict, Optional, Union, List, Iterable

import pandas as pd
from pandas import DataFrame

from hypex.dataset.backends.pandas_backend import PandasDataset
from hypex.dataset.base import DatasetBase
from hypex.dataset.roles import ABCRole
from hypex.dataset.utils import parse_roles

BACKENDS = ["pandas", "numpy"]


def select_backend(data):
    if isinstance(data, pd.DataFrame):
        return PandasDataset(data)
    if isinstance(data, str):
        if data in BACKENDS:
            return select_from_backend(data)
        check_data = check_file_extension(data)
        if check_data is not None:
            return PandasDataset(check_data)
    return None


def select_from_backend(backend: str):
    if backend == "pandas":
        return PandasDataset()


def check_file_extension(file_path):
    read_functions = {"csv": pd.read_csv, "xlsx": pd.read_excel, "json": pd.read_json}
    extension = file_path.split(".")[-1].lower()
    if extension in read_functions:
        read_function = read_functions[extension]
        return read_function(file_path)


class Dataset(DatasetBase):
    def set_data(self, data: Union[DataFrame, str] = None, roles=None):
        self.roles = parse_roles(roles)
        self.backend = select_backend(data)
        self.data = self.backend.data if self.backend is not None else None
        self._columns = list(self.roles.keys())

    def __init__(
        self,
        data: Union[DataFrame, str, None] = None,
        roles: Optional[Dict[ABCRole, Union[List[str], str]]] = None,
    ):
        self.roles = None
        self.backend = None
        self.data = None
        self.columns = None
        self.set_data(data, roles)

    def __repr__(self):
        return self.data.__repr__()

    def __len__(self):
        return self.backend.__len__()

    def __getitem__(self, item):
        return self.backend.__getitem__(item)

    def __setitem__(self, key, value):
        self.backend.__setitem__(key, value)

    def get_columns_by_roles(
        self, roles: Union[ABCRole, Iterable[ABCRole]]
    ) -> List[str]:
        roles = roles if isinstance(roles, Iterable) else [roles]
        return [
            column
            for column, role in self.roles.items()
            if any(isinstance(role, r) for r in roles)
        ]

    def create_empty(self, indexes=None, columns=None):
        indexes = [] if indexes is None else indexes
        columns = [] if columns is None else columns
        self.backend = self.backend.create_empty(indexes, columns)
        self.data = self.backend.data
        return self

    def apply(self, func, axis=0, raw=False, result_type=None, by_row="compat"):
        return self.backend.apply(
            func=func, axis=axis, raw=raw, result_type=result_type, by_row=by_row
        )

    def map(self, func, na_action=None, **kwargs):
        return self.backend.map(func=func, na_action=na_action)

    def unique(self):
        return self.backend.unique()

    def isin(self, values: Iterable) -> Iterable[bool]:
        raise NotImplementedError

    def groupby(self):
        raise NotImplementedError

    @property
    def index(self):
        return self.backend.index

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value


class ExperimentData(Dataset):
    def __init__(self, data: Union[Dataset, str]):
        if isinstance(data, Dataset):
            backend = "pandas" if data.backend == PandasDataset else "numpy"
            self.additional_fields = Dataset(backend).create_empty(
                data.index, data.columns
            )
            self.stats_fields = Dataset(backend).create_empty(data.index, data.columns)
            self.analysis_tables = {}
        else:
            self.additional_fields = Dataset(data)
            self.stats_fields = Dataset(data)
            self.analysis_tables = {}

    def create_empty(self, indexes=None, columns=None):
        self.additional_fields.create_empty(indexes, columns)
        self.stats_fields.create_empty(indexes, columns)
        return self

    # TODO переделать: обновление данных + обновление ролей
    def add_to_additional_fields(self, data: pd.DataFrame):
        self.additional_fields.data = self.additional_fields.data.join(data, how="left")

    # TODO переделать: обновление данных + обновление ролей
    def add_to_stats_fields(self, data: pd.DataFrame):
        self.stats_fields = self.stats_fields.data.join(data, how="left")

    def add_to_analysis_tables(
        self,
        key: str,
        data: pd.DataFrame,
        roles: Optional[Dict[ABCRole, Union[List[str], str]]] = None,
    ):
        self.analysis_tables[key] = Dataset(data, roles)
