from core.day_planner import DayPlanner
from models import DayProgram, TimeSlot


def test_day_planner_keeps_geocoded_coordinates_for_map_markers():
    class FakeAIService:
        def enrich_activities(self, activities, *, city):
            assert activities == [
                {"time": "10:00", "activity": "Visiter un musée"}
            ]
            assert city == "Angers"
            return [
                {
                    "time": "10:00",
                    "location": "Musée",
                    "address": "Centre-ville",
                    "lat": 47.4784,
                    "lon": -0.5632,
                }
            ]

    planner = DayPlanner.__new__(DayPlanner)
    planner.ai = FakeAIService()
    program = DayProgram(
        slots=[
            TimeSlot(time="10:00", activity="Visiter un musée"),
            TimeSlot(time="12:00", activity="Déjeuner"),
        ]
    )

    result = planner._enrich_with_ai(program, city="Angers")

    assert result is program
    assert program.slots[0].lat == 47.4784
    assert program.slots[0].lon == -0.5632
    assert program.slots[1].lat is None
    assert program.slots[1].lon is None
