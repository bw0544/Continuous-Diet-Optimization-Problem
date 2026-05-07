from dataclasses import dataclass


@dataclass
class Subject:
    age: int
    daily_calories: float

TEST_SUBJECT_JOHN = Subject(30, 2567.85)