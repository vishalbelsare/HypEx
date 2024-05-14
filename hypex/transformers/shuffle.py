from typing import Any, Optional

from hypex.dataset import Dataset, ExperimentData
from hypex.experiments.base import Executor, Calculator


class Shuffle(Calculator):
    def __init__(
        self,
        random_state: Optional[int] = None,
        full_name: Optional[str] = None,
        key: Any = "",
    ):
        super().__init__(full_name, key)
        self.random_state = random_state

    def generate_params_hash(self):
        return f"{self.random_state}"

    @property
    def __is_transformer(self):
        return True

    def calc(self, data: Dataset) -> Dataset:
        data.data = data.data.sample(frac=1, random_state=self.random_state)
        return data

    def execute(self, data: ExperimentData):
        return self.calc(data)
