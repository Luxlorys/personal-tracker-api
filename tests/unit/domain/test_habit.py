from datetime import timedelta

import pytest

from app.domain.exceptions import (
    CadenceAlreadyMetError,
    HabitArchivedError,
    InvalidCadenceTargetError,
    InvalidHabitNameError,
    InvalidNoteError,
)
from app.domain.value_objects.cadence import Cadence, CadencePeriod
from tests.factories import NOW, create_habit


def test_name_is_trimmed():
    assert create_habit(name="  Morning run  ").name == "Morning run"


@pytest.mark.parametrize("name", ["", "   ", "x" * 121])
def test_invalid_name_is_rejected(name: str):
    with pytest.raises(InvalidHabitNameError):
        create_habit(name=name)


@pytest.mark.parametrize("target", [0, -1, 101])
def test_invalid_cadence_target_is_rejected(target: int):
    with pytest.raises(InvalidCadenceTargetError):
        Cadence(period=CadencePeriod.daily, target=target)


def test_check_in_is_recorded():
    habit = create_habit()
    check_in = habit.check_in(at=NOW, note="felt good")
    assert habit.check_ins == [check_in]
    assert check_in.habit_id == habit.id


def test_note_longer_than_the_limit_is_rejected():
    habit = create_habit()
    with pytest.raises(InvalidNoteError):
        habit.check_in(at=NOW, note="x" * 501)


def test_second_check_in_in_the_same_day_is_rejected():
    habit = create_habit(period=CadencePeriod.daily, target=1)
    habit.check_in(at=NOW)
    with pytest.raises(CadenceAlreadyMetError):
        habit.check_in(at=NOW + timedelta(hours=3))


def test_check_in_is_allowed_until_the_weekly_target_is_met():
    habit = create_habit(period=CadencePeriod.weekly, target=3)
    for day in range(3):
        habit.check_in(at=NOW + timedelta(days=day))
    assert habit.is_completed_for(NOW)
    with pytest.raises(CadenceAlreadyMetError):
        habit.check_in(at=NOW + timedelta(days=3))


def test_archived_habit_rejects_check_ins():
    habit = create_habit()
    habit.archive(at=NOW)
    assert not habit.is_active
    with pytest.raises(HabitArchivedError):
        habit.check_in(at=NOW)


def test_streak_counts_consecutive_completed_days():
    habit = create_habit(period=CadencePeriod.daily)
    for days_ago in range(1, 4):
        habit.check_in(at=NOW - timedelta(days=days_ago))
    assert habit.current_streak(as_of=NOW) == 3


def test_streak_survives_an_in_progress_period():
    habit = create_habit(period=CadencePeriod.daily)
    habit.check_in(at=NOW - timedelta(days=1))
    assert not habit.is_completed_for(NOW)
    assert habit.current_streak(as_of=NOW) == 1


def test_streak_breaks_on_a_missed_period():
    habit = create_habit(period=CadencePeriod.daily)
    habit.check_in(at=NOW - timedelta(days=1))
    habit.check_in(at=NOW - timedelta(days=3))
    assert habit.current_streak(as_of=NOW) == 1


def test_partially_completed_period_does_not_count_towards_the_streak():
    habit = create_habit(period=CadencePeriod.weekly, target=2)
    habit.check_in(at=NOW - timedelta(weeks=1))
    assert habit.current_streak(as_of=NOW) == 0
