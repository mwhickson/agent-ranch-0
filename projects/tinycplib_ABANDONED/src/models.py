import random
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Union, Dict

class Location(Enum):
    BATHROOM = "Bathroom"
    BEDROOM = "Bedroom"
    KITCHEN = "Kitchen"
    LIVING_ROOM = "Living Room"
    OFFICE = "Office"
    ANY = "Any"

@dataclass(frozen=True)
class MetricValue:
    name: str
    value: int
    is_inverted: bool = False

    def is_good(self) -> bool:
        if self.is_inverted:
            return self.value <= 100
        return self.value >= 200

    def is_bad(self) -> bool:
        if self.is_inverted:
            return self.value >= 200
        return self.value <= 100

class Status(Enum):
    CONTENT = "Content"
    COMFORTABLE = "Comfortable"
    NEUTRAL = "Neutral"
    UNCOMFORTABLE = "Uncomfortable"
    MISERABLE = "Miserable"

@dataclass
class Activity:
    name: str
    purpose: str
    required_location: Location
    energy_change: Union[int, Tuple[int, ...]]
    happiness_change: Union[int, Tuple[int, ...]]
    hunger_change: Union[int, Tuple[int, ...]]
    hygiene_change: Union[int, Tuple[int, ...]]
    thirst_change: Union[int, Tuple[int, ...]]

    def get_change(self, param: Union[int, Tuple[int, ...]]) -> int:
        if isinstance(param, tuple):
            return random.choice(param)
        return param

class TinyComputerPerson:
    def __init__(self, name: str):
        self.name = name
        self.metrics = {
            "Energy": 255,
            "Happiness": 255,
            "Hunger": 0,
            "Hygiene": 255,
            "Thirst": 0
        }
        self.location = Location.LIVING_ROOM
        self.activity = None
        self.status = Status.NEUTRAL

    def update_metric(self, name: str, delta: int):
        current = self.metrics[name]
        # Clamp logic
        new_val = max(0, min(255, current + delta))
        self.metrics[name] = new_val

    def calculate_status(self):
        # Metric definitions for status evaluation
        # Energy: Good >= 200, Bad <= 100
        # Happiness: Good >= 200, Bad <= 100
        # Hunger: Good <= 100, Bad >= 200 (Inverted)
        # Hygiene: Good >= 200, Bad <= 100
        # Thirst: Good <= 100, Bad >= 200 (Inverted)
        
        good_count = 0
        bad_count = 0
        
        # Check Energy
        if self.metrics["Energy"] >= 200: good_count += 1
        elif self.metrics["Energy"] <= 100: bad_count += 1
        
        # Check Happiness
        if self.metrics["Happiness"] >= 200: good_count += 1
        elif self.metrics["Happiness"] <= 100: bad_count += 1
        
        # Check Hunger (Inverted)
        if self.metrics["Hunger"] <= 100: good_count += 1
        elif self.metrics["Hunger"] >= 200: bad_count += 1
        
        # Check Hygiene
        if self.metrics["Hygiene"] >= 200: good_count += 1
        elif self.metrics["Hygiene"] <= 100: bad_count += 1
        
        # Check Thirst (Inverted)
        if self.metrics["Thirst"] <= 100: good_count += 1
        elif self.metrics["Thirst"] >= 200: bad_count += 1

        if good_count >= 3 and bad_count == 0:
            self.status = Status.CONTENT
        elif bad_count == 0:
            self.status = Status.COMFORTABLE
        elif bad_count >= 3 and good_count == 0:
            self.status = Status.MISERABLE
        elif good_count == 0:
            self.status = Status.UNCOMFORTABLE
        else:
            self.status = Status.NEUTRAL

# Predefined Activities
ACTIVITIES = {
    "Cleaning": Activity("Cleaning (themselves)", "Improve Hygiene Score", Location.BATHROOM, -5, (0, 5), 0, (5, 10, 15, 20), 0),
    "Doing Nothing": Activity("Doing Nothing", "Default State", Location.ANY, (-5, 0), (-5, 0, 5), (-5, 0), 0, (-5, 0)),
    "Drinking": Activity("Drinking", "Improve Thirst Score", Location.KITCHEN, -5, (0, 5, 10), (-5, 0, 5), (-5, 0, 5), (-15, -10, -5)),
    "Eating": Activity("Eating", "Improve Hunger Score", Location.KITCHEN, -5, (0, 5, 10), (-15, -10, -5), (-10, -5, 0), (-5, 0, 5)),
    "Housework": Activity("Housework", "Improve Hygiene Score", Location.ANY, (-20, -10, -5), (0, 5, 10), (0, 5), (5, 10, 20), (0, 5)),
    "Listening to Music": Activity("Listening to Music", "Improve Happiness Score", Location.LIVING_ROOM, -5, (0, 5, 10), 0, 0, 0),
    "Playing a Game": Activity("Playing a Game", "Improve Happiness Score", Location.LIVING_ROOM, (-5, 5), (-15, -10, -5), (0, 5, 10, 15), (0, 5), (-5, 0), (0, 5)),
    "Reading a Book": Activity("Reading a Book", "Improve Happiness Score", Location.LIVING_ROOM, -5, (0, 5, 10), (0, 5), 0, (0, 5)),
    "Sleeping": Activity("Sleeping", "Improve Energy Score", Location.BEDROOM, (-5, 0, 10, 20, 30), (-5, 0, 5), (5, 10), (-10, -5, 0), (5, 10)),
    "Thinking": Activity("Thinking", "Select Next Activity", Location.ANY, (-10, -5, 0, 5, 10), (-5, 0, 5), (0, 5), 0, (0, 5)),
    "Watching Videos": Activity("Watching Videos", "Improve Happiness Score", Location.LIVING_ROOM, -5, (-10, -5, 5, 10), (0, 5), 0, (0, 5)),
    "Working": Activity("Working", "Improve or Lower Happiness Score", Location.OFFICE, (-30, -15, -5), (-15, -10, -5, 0, 5, 10, 15), (0, 5, 10), (-10, -5, 0), (0, 5, 10)),
}
