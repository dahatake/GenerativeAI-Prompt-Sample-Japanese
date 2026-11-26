import csv
import re
from datetime import date, time


_COLUMNS = ('employee', 'date', 'type', 'start', 'end')
_MINUTES_PER_DAY = 24 * 60
_BREAK_THRESHOLD_MINUTES = 6 * 60
_BREAK_MINUTES = 60
_ROUNDING_MINUTES = 15
_PAID_LEAVE_MINUTES = 450


def _clock_minutes(value: str) -> int:
    if not re.fullmatch(r'[0-9]{2}:[0-9]{2}', value):
        raise ValueError(f'invalid time: {value!r} (expected HH:MM)')
    clock = time.fromisoformat(value)
    return clock.hour * 60 + clock.minute


def monthly_work_hours(path) -> dict[str, float]:
    """Sum work and credited paid leave hours per employee for one month."""
    totals: dict[str, int] = {}
    month = None

    with open(path, encoding='utf-8-sig', newline='') as source:
        rows = csv.reader(source, strict=True)
        header = next(rows, None)
        if header is None:
            return {}
        if len(set(header)) != len(header) or not set(_COLUMNS).issubset(header):
            raise ValueError('CSV requires distinct column names and the columns ' + ', '.join(_COLUMNS))
        indices = tuple(header.index(column) for column in _COLUMNS)

        for row in rows:
            if not row:
                continue
            try:
                if len(row) != len(header):
                    raise ValueError('column count does not match the header')
                employee, day, kind, start, end = (row[i].strip() for i in indices)
                if not employee:
                    raise ValueError('employee is required')
                if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', day):
                    raise ValueError(f'invalid date: {day!r} (expected YYYY-MM-DD)')
                shift_date = date.fromisoformat(day)
                shift_month = (shift_date.year, shift_date.month)
                if month is None:
                    month = shift_month
                elif month != shift_month:
                    raise ValueError('CSV contains records from more than one calendar month')

                if kind == 'work':
                    minutes = (_clock_minutes(end) - _clock_minutes(start)) % _MINUTES_PER_DAY
                    if minutes > _BREAK_THRESHOLD_MINUTES:
                        minutes -= _BREAK_MINUTES
                    minutes -= minutes % _ROUNDING_MINUTES
                elif kind == 'paid_leave':
                    minutes = _PAID_LEAVE_MINUTES
                else:
                    raise ValueError(f'unknown shift type: {kind!r}')
                totals[employee] = totals.get(employee, 0) + minutes
            except ValueError as exc:
                raise ValueError(f'CSV line {rows.line_num}: {exc}') from exc

    return {employee: minutes / 60 for employee, minutes in totals.items()}
