import pytest

from solution import monthly_work_hours


def write(tmp_path, text, encoding="utf-8"):
    p = tmp_path / "s.csv"
    p.write_bytes(text.encode(encoding))
    return p


HEADER = "employee,date,type,start,end\n"


def test_sample_shifts_csv():
    r = monthly_work_hours("shifts.csv")
    assert set(r) == {"E001", "E002", "E003"}
    assert all(isinstance(v, float) for v in r.values())
    assert r["E001"] == pytest.approx(9 + 5 + 50 / 60, abs=1e-6)
    assert r["E002"] == pytest.approx(14.0, abs=1e-6)
    assert r["E003"] == pytest.approx(9.25, abs=1e-6)


def test_overnight(tmp_path):
    p = write(tmp_path, HEADER + "A,2026-10-01,work,22:00,06:00\n")
    assert monthly_work_hours(p) == {"A": pytest.approx(8.0)}


def test_paid_leave_is_zero_but_key_kept(tmp_path):
    p = write(tmp_path, HEADER + "A,2026-10-01,paid_leave,,\n")
    assert monthly_work_hours(p) == {"A": 0.0}


def test_bom_blank_lines_and_spaces(tmp_path):
    p = write(tmp_path, "\ufeff" + HEADER + "\n A ,2026-10-01,work, 09:00 ,10:30\n\n", "utf-8")
    assert monthly_work_hours(p) == {"A": pytest.approx(1.5)}


def test_multiple_months_summed(tmp_path):
    p = write(tmp_path, HEADER + "A,2026-10-01,work,09:00,10:00\nA,2026-11-01,work,09:00,11:00\n")
    assert monthly_work_hours(p) == {"A": pytest.approx(3.0)}


@pytest.mark.parametrize(
    "row",
    [
        "A,2026-10-01,work,9am,18:00",
        "A,2026-10-01,work,25:00,18:00",
        "A,2026-10-01,work,,",
        "A,2026-10-01,work,09:00,09:00",
        ",2026-10-01,work,09:00,10:00",
    ],
)
def test_invalid_rows_raise(tmp_path, row):
    p = write(tmp_path, HEADER + row + "\n")
    with pytest.raises(ValueError):
        monthly_work_hours(p)


def test_empty_file(tmp_path):
    assert monthly_work_hours(write(tmp_path, "")) == {}
    assert monthly_work_hours(write(tmp_path, HEADER)) == {}
