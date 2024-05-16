from pathlib import Path
from typing import (
    Sequence,
    Union,
    Iterable,
    List,
    Dict,
    Tuple,
    Sized,
    Callable,
    Optional,
    Any,
)

import pandas as pd  # type: ignore
import numpy as np

from hypex.dataset.backends.abstract import DatasetBackendCalc
from hypex.utils import FromDictType, MergeOnError, FieldsType, ScalarType


class PandasDataset(DatasetBackendCalc):
    @staticmethod
    def _read_file(filename: Union[str, Path]) -> pd.DataFrame:
        file_extension = Path(filename).suffix
        if file_extension == ".csv":
            return pd.read_csv(filename)
        elif file_extension == ".xlsx":
            return pd.read_excel(filename)
        else:
            raise ValueError(f"Unsupported file extension {file_extension}")

    def __init__(self, data: Union[pd.DataFrame, Dict, str, pd.Series] = None):
        if isinstance(data, pd.DataFrame):
            self.data = data
        elif isinstance(data, pd.Series):
            self.data = pd.DataFrame(data)
        elif isinstance(data, Dict):
            if "index" in data.keys():
                self.data = pd.DataFrame(data=data["data"], index=data["index"])
            else:
                self.data = pd.DataFrame(data=data["data"])
        elif isinstance(data, str):
            self.data = self._read_file(data)
        else:
            self.data = None

    def __getitem__(self, item):
        if isinstance(item, (slice, int)):
            return self.data.iloc[item]
        if isinstance(item, (str, list)):
            return self.data[item]
        raise KeyError("No such column or row")

    def __len__(self):
        return len(self.data)

    @staticmethod
    def __magic_determine_other(other) -> Any:
        if isinstance(other, PandasDataset):
            return other.data
        else:
            return other

    # comparison operators:
    def __eq__(self, other) -> Any:
        return self.data == PandasDataset.__magic_determine_other(other)

    def __ne__(self, other) -> Any:
        return self.data != PandasDataset.__magic_determine_other(other)

    def __le__(self, other) -> Any:
        return self.data <= PandasDataset.__magic_determine_other(other)

    def __lt__(self, other) -> Any:
        return self.data < PandasDataset.__magic_determine_other(other)

    def __ge__(self, other) -> Any:
        return self.data >= PandasDataset.__magic_determine_other(other)

    def __gt__(self, other) -> Any:
        return self.data > PandasDataset.__magic_determine_other(other)

    # Unary operations:
    def __pos__(self) -> Any:
        return +self.data

    def __neg__(self) -> Any:
        return -self.data

    def __abs__(self) -> Any:
        return abs(self.data)

    def __invert__(self) -> Any:
        return ~self.data

    def __round__(self, ndigits: int = 0) -> Any:
        return round(self.data)

    # Binary operations:
    def __add__(self, other) -> Any:
        return self.data + PandasDataset.__magic_determine_other(other)

    def __sub__(self, other) -> Any:
        return self.data - PandasDataset.__magic_determine_other(other)

    def __mul__(self, other) -> Any:
        return self.data * PandasDataset.__magic_determine_other(other)

    def __floordiv__(self, other) -> Any:
        return self.data // PandasDataset.__magic_determine_other(other)

    def __div__(self, other) -> Any:
        return self.data / PandasDataset.__magic_determine_other(other)

    def __truediv__(self, other) -> Any:
        return self.data / PandasDataset.__magic_determine_other(other)

    def __mod__(self, other) -> Any:
        return self.data % PandasDataset.__magic_determine_other(other)

    def __pow__(self, other) -> Any:
        return self.data ** PandasDataset.__magic_determine_other(other)

    def __and__(self, other) -> Any:
        return self.data & PandasDataset.__magic_determine_other(other)

    def __or__(self, other) -> Any:
        return self.data | PandasDataset.__magic_determine_other(other)

    # Right arithmetic operators:
    def __radd__(self, other) -> Any:
        return PandasDataset.__magic_determine_other(other) + self.data

    def __rsub__(self, other) -> Any:
        return PandasDataset.__magic_determine_other(other) - self.data

    def __rmul__(self, other) -> Any:
        return PandasDataset.__magic_determine_other(other) * self.data

    def __rfloordiv__(self, other) -> Any:
        return PandasDataset.__magic_determine_other(other) // self.data

    def __rdiv__(self, other) -> Any:
        return PandasDataset.__magic_determine_other(other) / self.data

    def __rtruediv__(self, other) -> Any:
        return PandasDataset.__magic_determine_other(other) / self.data

    def __rmod__(self, other) -> Any:
        return PandasDataset.__magic_determine_other(other) % self.data

    def __rpow__(self, other) -> Any:
        return PandasDataset.__magic_determine_other(other) ** self.data

    def __repr__(self):
        return self.data.__repr__()

    def _create_empty(
        self,
        index: Optional[Iterable] = None,
        columns: Optional[Iterable[str]] = None,
    ):
        self.data = pd.DataFrame(index=index, columns=columns)
        return self

    def _get_column_index(
        self, column_name: Union[Sequence[str], str]
    ) -> Union[int, Sequence[int]]:
        return (
            self.data.columns.get_loc(column_name)
            if isinstance(column_name, str)
            else self.data.columns.get_indexer(column_name)
        )[0]

    def _get_column_type(self, column_name: str) -> str:
        return str(self.data.dtypes[column_name])

    def _update_column_type(self, column_name: str, type_name: str):
        self.data[column_name] = self.data[column_name].astype(type_name)
        return self

    def add_column(
        self,
        data: Union[Sequence],
        name: str,
        index: Optional[Sequence] = None,
    ):
        if index:
            self.data = self.data.join(
                pd.DataFrame(data, columns=[name], index=list(index))
            )
        else:
            self.data.loc[:, name] = data

    def append(self, other, index: bool = False) -> pd.DataFrame:
        new_data = pd.concat([self.data, other.data])
        if index:
            new_data.reset_index()
        return new_data

    @property
    def index(self):
        return self.data.index

    @property
    def columns(self):
        return self.data.columns

    def from_dict(self, data: FromDictType, index: Union[Iterable, Sized, None] = None):
        self.data = pd.DataFrame().from_records(data)
        if index:
            self.data.index = index
        return self

    def to_dict(self) -> Dict[str, Any]:
        data = self.data.to_dict()
        for key, value in data.items():
            data[key] = list(data[key].values())
        index = list(self.index)
        return {"data": data, "index": index}

    def apply(self, func: Callable, **kwargs) -> pd.DataFrame:
        return self.data.apply(func, **kwargs)

    def map(self, func: Callable, **kwargs) -> pd.DataFrame:
        return self.data.map(func, **kwargs)

    def is_empty(self) -> bool:
        return self.data.empty

    def unique(self):
        return {column: self.data[column].unique() for column in self.data.columns}

    def nunique(self, dropna: bool = True):
        return {column: self.data[column].nunique() for column in self.data.columns}

    def isin(self, values: Iterable) -> Iterable[bool]:
        return self.data.isin(values)

    def groupby(self, by: Union[str, Iterable[str]], **kwargs) -> List[Tuple]:
        groups = self.data.groupby(by, **kwargs)
        return list(groups)

    def loc(self, items: Iterable) -> Iterable:
        data = self.data.loc[items]
        return pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data

    def iloc(self, items: Iterable) -> Iterable:
        data = self.data.iloc[items]
        return pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data

    def agg(self, func: Union[str, List], **kwargs) -> Union[pd.DataFrame, float]:
        func = func if isinstance(func, List) else [func]
        result = self.data.agg(func, **kwargs)
        if result.shape[0] == 1 and result.shape[1] == 1:
            return float(result.loc[result.index[0], result.columns[0]])
        return result if isinstance(result, pd.DataFrame) else pd.DataFrame(result)

    def mean(self) -> Union[pd.DataFrame, float]:
        return self.agg(["mean"])

    def mode(
        self, numeric_only: bool = False, dropna: bool = True
    ) -> Union[pd.DataFrame, float]:
        return self.agg(["mode"])

    def var(
        self, skipna: bool = True, ddof: int = 1, numeric_only: bool = False
    ) -> Union[pd.DataFrame, float]:
        return self.agg(["var"])

    def max(self) -> Union[pd.DataFrame, float]:
        return self.agg(["max"])

    def min(self) -> Union[pd.DataFrame, float]:
        return self.agg(["min"])

    def count(self) -> Union[pd.DataFrame, float]:
        return self.agg(["count"])

    def sum(self) -> Union[pd.DataFrame, float]:
        return self.agg(["sum"])

    def log(self) -> pd.DataFrame:
        np_data = np.log(self.data.to_numpy())
        return pd.DataFrame(np_data, columns=self.data.columns)

    def std(self) -> Union[pd.DataFrame, float]:
        return self.agg(["std"])

    def coefficient_of_variation(self) -> Union[pd.DataFrame, float]:
        data = (self.data.std() / self.data.mean()).to_frame().T
        data.index = ["cv"]
        if data.shape[0] == 1 and data.shape[1] == 1:
            return float(data.loc[data.index[0], data.columns[0]])
        return data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)

    def corr(self, method="pearson", numeric_only=False) -> Union[pd.DataFrame, float]:
        return self.data.corr(method="pearson", numeric_only=False)

    def value_counts(
        self,
        normalize: bool = False,
        sort: bool = True,
        ascending: bool = False,
        dropna: bool = True,
    ) -> pd.DataFrame:
        return self.data.value_counts(
            normalize=normalize, sort=sort, ascending=ascending, dropna=dropna
        ).reset_index()

    def na_counts(self) -> Union[pd.DataFrame, int]:
        data = self.data.isna().sum().to_frame().T
        data.index = ["na_counts"]
        if data.shape[0] == 1 and data.shape[1] == 1:
            return int(data.loc[data.index[0], data.columns[0]])
        return data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)

    def dropna(
        self, how: str = "any", subset: Union[str, Iterable[str]] = None
    ) -> pd.DataFrame:
        return self.data.dropna(how=how, subset=subset)

    def isna(self) -> pd.DataFrame:
        return self.data.isna()

    def quantile(self, q: float = 0.5) -> pd.DataFrame:
        return self.agg(func="quantile", q=q)

    def select_dtypes(
        self, include: FieldsType = "", exclude: FieldsType = ""
    ) -> pd.DataFrame:
        return self.data.select_dtypes(include=include, exclude=exclude)

    def merge(
        self,
        right: pd.DataFrame,  # should be PandasDataset.
        on: FieldsType = "",
        left_on: FieldsType = "",
        right_on: FieldsType = "",
        left_index: bool = False,
        right_index: bool = False,
        suffixes: tuple[str, str] = ("_x", "_y"),
    ) -> pd.DataFrame:
        for on_ in [on, left_on, right_on]:
            if on_ and (on_ not in [*self.columns, *right.columns]):
                raise MergeOnError(on_)
        return self.data.merge(
            right=right.data,
            on=on,
            left_on=left_on,
            right_on=right_on,
            left_index=left_index,
            right_index=right_index,
            suffixes=suffixes,
        )

    def drop(self, labels: FieldsType = "", axis: int = 1) -> pd.DataFrame:
        return self.data.drop(labels=labels, axis=axis)
