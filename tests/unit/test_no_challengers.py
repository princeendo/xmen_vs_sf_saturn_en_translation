from __future__ import annotations

import pytest

from tools.disc.build_english import (
    NO_CHALLENGERS,
    no_challengers_patches,
    with_extra,
    with_names,
)
from tools.disc.names import REGION_READ, US_REGION, US_SITES


def test_the_sign_is_one_region_read_taken_as_us() -> None:
    assert no_challengers_patches() == [(NO_CHALLENGERS, REGION_READ, US_REGION)]
    assert NO_CHALLENGERS not in US_SITES


def test_it_combines_with_the_american_names_and_refuses_overlaps() -> None:
    patches = with_extra(with_names([], "us"), no_challengers_patches(), "x")
    assert len(patches) == len(US_SITES) + 1
    with pytest.raises(ValueError, match="overlaps"):
        with_extra(patches, no_challengers_patches(), "x")
