from hypex.experiment.experiment import Experiment, OnRoleExperiment
from hypex.splitters.aa_splitter import AASplitter
from hypex.comparators.hypothesis_testing import TTest, KSTest
from hypex.comparators.comparators import GroupDifference
from hypex.dataset.roles import TargetRole, TreatmentRole
from hypex.analyzer.aa import OneAASplitAnalyzer
from hypex.utils.enums import SpaceEnum

AA_TEST = Experiment(
    executors=[
        AASplitter(),
        OnRoleExperiment(
            executors=[
                GroupDifference(
                    grouping_role=TreatmentRole(), space=SpaceEnum.additional
                ),
                TTest(grouping_role=TreatmentRole(), space=SpaceEnum.additional),
                KSTest(grouping_role=TreatmentRole(), space=SpaceEnum.additional),
            ],
            role=TargetRole(),
        ),
        OneAASplitAnalyzer(),
    ]
)
