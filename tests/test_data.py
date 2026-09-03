import pytest

from src.data import validate_columns


def test_missing_schema_raises():
    with pytest.raises(ValueError):
        validate_columns(["AGENCY", "TRANSACTION_AMOUNT"])
