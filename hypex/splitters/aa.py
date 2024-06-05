from typing import Any, List, Optional

from hypex.dataset import Dataset, ExperimentData, TreatmentRole
from hypex.executor import Calculator
from hypex.utils import ExperimentDataEnum


class AASplitter(Calculator):
    def __init__(
        self,
        control_size: float = 0.5,
        random_state: Optional[int] = None,
        constant_key: bool = False,
        save_groups: bool = True,
        key: Any = "",
    ):
        self.control_size = control_size
        self.random_state = random_state
        self._key = key
        self.constant_key = constant_key
        self.save_groups = save_groups
        super().__init__(key)

    @property
    def key(self) -> Any:
        return self._key

    @key.setter
    def key(self, value: Any):
        if not self.constant_key:
            self._key = value
            self._generate_id()

    def generate_params_hash(self) -> str:
        return f"{self.random_state}"

    def _set_value(self, data: ExperimentData, value, key=None) -> ExperimentData:
        data = data.set_value(
            ExperimentDataEnum.additional_fields,
            self._id,
            str(self.__class__.__name__),
            value,
            role=TreatmentRole(),
        )

        if self.save_groups:
            data.groups[self.id] = {
                group: data.ds.loc[group_data.index]
                for group, group_data in data.additional_fields.groupby(self.id)
            }
        return data

    @staticmethod
    def _inner_function(
        data: Dataset,
        random_state: Optional[int] = None,
        control_size: float = 0.5,
        **kwargs,
    ) -> List[str]:
        experiment_data = data.shuffle(random_state)
        addition_indexes = list(experiment_data.index)
        edge = int(len(addition_indexes) * control_size)

        return ["control" if i < edge else "test" for i in addition_indexes]

    def execute(self, data: ExperimentData) -> ExperimentData:
        return self._set_value(
            data,
            self.calc(
                data.ds, random_state=self.random_state, control_size=self.control_size
            ),
        )


# class AASplitterWithGrouping(AASplitter):
#     @staticmethod
#     def calc(data: Dataset):
#         group_field = data.get_columns_by_roles(GroupingRole())
#         groups = list(data.groupby(group_field))
#         edge = len(groups) // 2
#         result: Dataset = Dataset._create_empty()
#         for i, group in enumerate(groups):
#             group_ds = Dataset.from_dict(
#                 [{"group_for_split": group[0], "group": "A" if i < edge else "B"}]
#                 * len(group[1]),
#                 roles={"group_for_split": GroupingRole(), "group": TreatmentRole()},
#                 index=group[1].index,
#             )
#             result = group_ds if result is None else result.append(group_ds)
#         return result["group"]
#
#
# class AASplitterWithStratification(AASplitter):
#     def __init__(
#         self,
#         control_size: float = 0.5,
#         random_state: Optional[int] = None,
# #         key: Any = "",
#     ):
#         super().__init__(control_size, random_state,  key)
#
#     def calc(self, data: Dataset):
#         stratification_columns = data.get_columns_by_roles(StratificationRole())
#
#         groups = data.groupby(stratification_columns)
#         result = Dataset._create_empty()
#         for _, gd in groups:
#             ged = ExperimentData(gd)
#             ged = super().execute(ged)
#
#             result = ged if result is None else result.append(ged)
#         return result["group"]


# As idea
# class SplitterAAMulti(ExperimentMulti):
#     def execute(self, data):
#         raise NotImplementedError