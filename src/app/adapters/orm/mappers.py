"""Translation between domain entities and SQLAlchemy models.

Kept in one place so the boundary is obvious: if a column is added, exactly one
file has to learn about it.
"""

from app.adapters.orm.models import CheckInModel, HabitModel
from app.domain.entities.check_in import CheckIn
from app.domain.entities.habit import Habit
from app.domain.value_objects.cadence import Cadence, CadencePeriod


def check_in_to_model(check_in: CheckIn) -> CheckInModel:
    return CheckInModel(
        id=check_in.id,
        habit_id=check_in.habit_id,
        recorded_at=check_in.recorded_at,
        note=check_in.note,
    )


def check_in_to_entity(model: CheckInModel) -> CheckIn:
    return CheckIn(
        id=model.id,
        habit_id=model.habit_id,
        recorded_at=model.recorded_at,
        note=model.note,
    )


def habit_to_model(habit: Habit) -> HabitModel:
    return HabitModel(
        id=habit.id,
        name=habit.name,
        cadence_period=habit.cadence.period.value,
        cadence_target=habit.cadence.target,
        created_at=habit.created_at,
        archived_at=habit.archived_at,
        check_ins=[check_in_to_model(c) for c in habit.check_ins],
    )


def habit_to_entity(model: HabitModel) -> Habit:
    return Habit(
        id=model.id,
        name=model.name,
        cadence=Cadence(period=CadencePeriod(model.cadence_period), target=model.cadence_target),
        created_at=model.created_at,
        archived_at=model.archived_at,
        check_ins=[check_in_to_entity(c) for c in model.check_ins],
    )
