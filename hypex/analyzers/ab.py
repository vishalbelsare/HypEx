from typing import Dict, List

from hypex.analyzers.analyzer import Analyzer
from hypex.comparators.hypothesis_testing import TTest, MannWhitney
from hypex.dataset.dataset import ExperimentData, Dataset
from hypex.dataset.roles import StatisticRole
from hypex.experiments.base import (
    Executor,
)
from hypex.stats.descriptive import Mean
from hypex.utils.enums import ExperimentDataEnum, BackendsEnum


class ABAnalyzer(Analyzer):
    default_inner_executors: Dict[str, Executor] = {"mean": Mean()}

    def _set_value(self, data: ExperimentData, value=None, key=None) -> ExperimentData:
        return data.set_value(
            ExperimentDataEnum.analysis_tables,
            self.id,
            str(self.full_name),
            value,
        )

    def execute(self, data: ExperimentData) -> ExperimentData:
        analysis_tests: List[type] = [TTest, MannWhitney]
        executor_ids = data.get_ids(analysis_tests)

        analysis_data = {}
        mean_operator: Mean = self.inner_executors["mean"]
        for c, spaces in executor_ids.items():
            analysis_ids = spaces.get("analysis_tables", [])
            if len(analysis_ids) == 0:
                continue
            t_data = data.analysis_tables[analysis_ids[0]]
            for aid in analysis_ids[1:]:
                t_data = t_data.append(data.analysis_tables[aid])
            t_data.data.index = analysis_ids

            for f in ["p-value", "pass"]:
                analysis_data[f"{c.__name__} {f}"] = mean_operator.calc(t_data[f]).iloc[
                    0
                ]
        analysis_data = Dataset.from_dict(
            [analysis_data],
            {f: StatisticRole() for f in analysis_data},
            BackendsEnum.pandas,
        )

        return self._set_value(data, analysis_data)
