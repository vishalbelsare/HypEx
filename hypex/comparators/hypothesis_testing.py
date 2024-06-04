from typing import Union, Optional

from scipy.stats import ttest_ind, ks_2samp, mannwhitneyu  # type: ignore

from .abstract import StatHypothesisTesting
from ..dataset import Dataset, ABCRole
from ..extensions.hypothesis_testing import (
    TTestExtension,
    KSTestExtension,
    UTestExtension,
)
from ..utils import SpaceEnum
from ..utils.typings import NumberTypes, CategoricalTypes


class TTest(StatHypothesisTesting):
    def __init__(
        self,
        grouping_role: Union[ABCRole, None] = None,
        space: SpaceEnum = SpaceEnum.auto,
        reliability: float = 0.05,
    ):
        super().__init__(
            grouping_role=grouping_role,
            space=space,
            search_types=NumberTypes,
            reliability=reliability,
        )

    @classmethod
    def _inner_function(
        cls, data: Dataset, test_data: Optional[Dataset] = None, **kwargs
    ) -> Dataset:
        return TTestExtension(kwargs.get("reliability", 0.05)).calc(
            data, test_data=test_data, **kwargs
        )


class KSTest(StatHypothesisTesting):
    def __init__(
        self,
        grouping_role: Union[ABCRole, None] = None,
        space: SpaceEnum = SpaceEnum.auto,
        reliability: float = 0.05,
    ):
        super().__init__(
            grouping_role=grouping_role,
            space=space,
            search_types=NumberTypes,
            reliability=reliability,
        )

    @classmethod
    def _inner_function(
        cls, data: Dataset, test_data: Optional[Dataset] = None, **kwargs
    ) -> Dataset:
        return KSTestExtension(kwargs.get("reliability", 0.05)).calc(
            data, test_data=test_data, **kwargs
        )


class UTest(StatHypothesisTesting):
    def __init__(
        self,
        grouping_role: Union[ABCRole, None] = None,
        space: SpaceEnum = SpaceEnum.auto,
        reliability: float = 0.05,
    ):
        super().__init__(
            grouping_role=grouping_role,
            space=space,
            search_types=NumberTypes,
            reliability=reliability,
        )

    @classmethod
    def _inner_function(
        cls, data: Dataset, test_data: Optional[Dataset] = None, **kwargs
    ) -> Dataset:
        return UTestExtension(kwargs.get("reliability", 0.05)).calc(
            data, test_data=test_data, **kwargs
        )


class Chi2Test(StatHypothesisTesting):
    def __init__(
        self,
        grouping_role: Union[ABCRole, None] = None,
        space: SpaceEnum = SpaceEnum.auto,
        reliability: float = 0.05,
    ):
        super().__init__(
            grouping_role=grouping_role,
            space=space,
            search_types=CategoricalTypes,
            reliability=reliability,
        )

    @classmethod
    def _inner_function(
        cls, data: Dataset, test_data: Optional[Dataset] = None, **kwargs
    ) -> Dataset:
        return UTestExtension(kwargs.get("reliability", 0.05)).calc(
            data, test_data=test_data, **kwargs
        )
