from typing import Any, Optional, List

from hypex.dataset import Dataset, ExperimentData, FeatureRole
from hypex.executor import Calculator
from hypex.utils import (
    AbstractMethodError,
    FieldKeyTypes,
    CategoricalTypes,
    NAME_BORDER_SYMBOL,
    ExperimentDataEnum,
)

class Encoder(Calculator):

    def __init__(self, target_roles: Optional[FieldKeyTypes] = None, key: Any = ""):
        self.target_roles = target_roles
        self._key = key
        super().__init__(key)

    @property
    def __is_encoder(self):
        return True

    def _get_ids(self, col_name):
        self.key = NAME_BORDER_SYMBOL + col_name + NAME_BORDER_SYMBOL
        return self.id

    def _ids_to_names(self, col_names: List[str]):
        return {col_name: self._get_ids(col_name) for col_name in col_names}

    @staticmethod
    def _inner_function(data: Dataset, **kwargs) -> Dataset:
        raise AbstractMethodError

    def _set_value(
        self, data: ExperimentData, value: Dataset, key=None
    ) -> ExperimentData:
        return data.set_value(
            ExperimentDataEnum.additional_fields,
            self._ids_to_names(value.columns),
            str(self.__class__.__name__),
            value,
            role=value.roles,
        )

    def execute(self, data: ExperimentData) -> ExperimentData:
        target_cols = data.ds.search_columns(
            roles=self.target_roles or [FeatureRole()], search_types=[CategoricalTypes]
        )
        return self._set_value(
            data=data,
            value=self.calc(data=data.ds, target_cols=target_cols),
            key=self.key,
        )