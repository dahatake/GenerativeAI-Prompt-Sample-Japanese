import os
import tempfile

from solution import monthly_work_hours

HERE = os.path.dirname(os.path.abspath(__file__))


def run(text):
    with tempfile.TemporaryDirectory(dir=HERE) as d:
        p = os.path.join(d, "t.csv")
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write("employee,date,type,start,end\n" + text)
        return monthly_work_hours(p)


def test_sample_csv():
    assert monthly_work_hours(os.path.join(HERE, "shifts.csv")) == {
        "E001": 21.25,
        "E002": 13.0,
        "E003": 8.25,
    }


def test_break_threshold():
    assert run("A,2026-10-01,work,09:00,15:00\n") == {"A": 6.0}  # exactly 6h: no break
    assert run("A,2026-10-01,work,09:00,15:15\n") == {"A": 5.25}  # 6h15 -> 5h15
    assert run("A,2026-10-01,work,09:00,15:01\n") == {"A": 5.0}  # 5h01 -> 5h00


def test_floor_15_minutes_per_shift():
    assert run("A,2026-10-01,work,09:00,14:50\n") == {"A": 5.75}
    # per-shift floor: 2 x 5h50 -> 2 x 5.75, not floor of the sum
    assert run("A,2026-10-01,work,09:00,14:50\nA,2026-10-02,work,09:00,14:50\n") == {"A": 11.5}


def test_overnight():
    assert run("A,2026-10-01,work,22:00,06:00\n") == {"A": 7.0}
    assert run("A,2026-10-01,work,22:00,02:00\n") == {"A": 4.0}


def test_paid_leave():
    assert run("A,2026-10-01,paid_leave,,\n") == {"A": 7.5}
    assert run("A,2026-10-01,paid_leave,,\nA,2026-10-02,work,09:00,15:00\n") == {"A": 13.5}


def test_header_only_and_invalid_rows():
    assert run("") == {}
    assert run("A,2026-10-01,work,,\nA,2026-10-02,absent,09:00,18:00\n") == {"A": 0.0}
