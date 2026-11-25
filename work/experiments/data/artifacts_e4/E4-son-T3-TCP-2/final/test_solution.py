import pathlib

import pytest

from solution import validate_invoice_id

HERE = pathlib.Path(__file__).parent


def _sample_ids():
    lines = (HERE / "samples.txt").read_text(encoding="utf-8").splitlines()
    return [l for l in lines if l.startswith("INV-")]


def test_samples_file_has_four_ids():
    assert len(_sample_ids()) == 4


@pytest.mark.parametrize("v", _sample_ids())
def test_dod1_samples_valid(v):
    assert validate_invoice_id(v) is True


@pytest.mark.parametrize("v", ["INV-202613-0001", "INV-202600-0001"])
def test_dod2_bad_month(v):
    assert validate_invoice_id(v) is False


@pytest.mark.parametrize("v", ["INV-202601-0000", "INV-202601-001", "INV-202601-00001"])
def test_dod3_bad_sequence(v):
    assert validate_invoice_id(v) is False


@pytest.mark.parametrize("v", ["INV-201912-0001", "INV-210001-0001", "INV-20261-0001"])
def test_dod4_bad_year(v):
    assert validate_invoice_id(v) is False


@pytest.mark.parametrize("v", ["INV-202001-0001", "INV-209912-9999", "INV-202601-9999"])
def test_dod4_boundaries_valid(v):
    assert validate_invoice_id(v) is True


@pytest.mark.parametrize(
    "v",
    [
        "inv-202601-0001",
        "INV202601-0001",
        " INV-202601-0001",
        "INV-202601-0001 ",
        "INV-202601-0001\n",
        "INV-２０２６０１-０００１",
        "INV‐202601-0001",
        "INV-202601‐0001",
        "INV_202601_0001",
        "",
    ],
)
def test_dod5_bad_format(v):
    assert validate_invoice_id(v) is False


@pytest.mark.parametrize("v", [None, 202601, 1.5, b"INV-202601-0001", ["INV-202601-0001"], object()])
def test_dod6_non_str_false_no_exception(v):
    assert validate_invoice_id(v) is False


def test_dod7_always_bool():
    cases = _sample_ids() + ["x", "", None, 1, "INV-202601-0000"]
    assert all(type(validate_invoice_id(c)) is bool for c in cases)
