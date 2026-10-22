"""Pytest fixtures shared across the V-UNIVERSAL test-suite."""

from __future__ import annotations

import random

import numpy as np
import pytest


@pytest.fixture(autouse=True)
def _seed_everything() -> None:
    random.seed(42)
    np.random.seed(42)
