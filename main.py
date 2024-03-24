import json
from pathlib import Path
from typing import Any, Literal, NamedTuple


class SVRange(NamedTuple):
    min: int
    max: int


class BaseFishData:
    id: str
    name: str
    size: SVRange

    def __init__(self, id: str, name: str, size: SVRange) -> None:
        self.id = id
        self.name = name
        self.size = size

    def str_no_leading_zero(self, num: str) -> str:
        return num[1:] if num.startswith("0.") else num


class FishData(BaseFishData):
    chance_to_dart: int
    darting_randomness: Literal["mixed", "smooth", "floater", "sinker", "dart"]
    time_ranges: list[SVRange]
    weather: Literal["sunny", "rainy", "both"]
    max_depth: int
    spawn_multiplier: float
    depth_multiplier: float
    fishing_level: int
    tutorial_catch: bool

    def __init__(
        self,
        id: str,
        name: str,
        size: SVRange,
        chance_to_dart: int,
        darting_randomness: Literal["mixed", "smooth", "floater", "sinker", "dart"],
        time_ranges: list[SVRange],
        weather: Literal["sunny", "rainy", "both"],
        max_depth: int,
        spawn_multiplier: float,
        depth_multiplier: float,
        fishing_level: int,
        tutorial_catch: bool,
    ) -> None:
        super().__init__(id, name, size)
        valid_darting_randomness_values: list[str] = [
            "mixed",
            "smooth",
            "floater",
            "sinker",
            "dart",
        ]
        if darting_randomness not in valid_darting_randomness_values:
            raise ValueError(
                f"Incorrect value given for DartingRandomness in {self.id}.\nExpected one of the following values: {", ".join(valid_darting_randomness_values)}"
            )

        valid_weather_values: list[str] = ["sunny", "rainy", "both"]
        if weather not in valid_weather_values:
            raise ValueError(
                f"Incorrect value given for Weather in {self.id}.\nExpected one of the following values: {", ".join(valid_weather_values)}"
            )

        self.chance_to_dart = chance_to_dart
        self.darting_randomness = darting_randomness
        self.time_ranges = time_ranges
        self.weather = weather
        self.max_depth = max_depth
        self.spawn_multiplier = spawn_multiplier
        self.depth_multiplier = depth_multiplier
        self.fishing_level = fishing_level
        self.tutorial_catch = tutorial_catch

    def convert(self) -> str:
        time_data: str = "".join(
            f"{time.min} {time.max} " for time in self.time_ranges
        ).strip()

        return f"{self.name}/{self.chance_to_dart}/{self.darting_randomness}/{self.size.min}/{self.size.max}/{time_data}/spring summer fall winter/{self.weather}/690 .4 685 .1/{self.max_depth}/{self.str_no_leading_zero(str(self.spawn_multiplier))}/{self.str_no_leading_zero(str(self.depth_multiplier))}/{self.fishing_level}/{str(self.tutorial_catch).lower()}"


class CrabpotData(BaseFishData):
    chance: float
    water_type: Literal["freshwater", "ocean"]

    def __init__(
        self,
        id: str,
        name: str,
        size: SVRange,
        chance: float,
        water_type: Literal["freshwater", "ocean"],
    ) -> None:
        super().__init__(id, name, size)

        valid_water_types: list[str] = ["freshwater", "ocean"]
        if water_type not in valid_water_types:
            raise ValueError(
                f"Incorrect value given for WaterType in {self.id}.\nExpected one of the following values: {", ".join(valid_water_types)}"
            )

        self.chance = chance
        self.water_type = water_type

    def convert(self) -> str:
        return f"{self.name}/trap/{self.str_no_leading_zero(str(self.chance))}/684 .45/{self.water_type}/{self.size.min}/{self.size.max}/false"


def convert_input_files() -> None:
    input_path = Path("./input")
    input_files = input_path.glob("*.json")

    for file in input_files:
        convert_input_file(file)


def convert_input_file(file: Path) -> None:
    with open(file, "r") as fr:
        data: dict[str, dict[str, Any]] = json.load(fr)

    mod_id = str(data.get("ModId", "{{ModId}}"))

    parsed_data: dict[str, str] = {}

    for unique_id, unparsed_fish_data in data.items():
        if unique_id == "ModId":
            continue

        is_fish: bool = True if unparsed_fish_data.get("Chance") is None else False
        parsed_id: str = unique_id.replace("{{ModId}}", mod_id)

        if is_fish:
            try:
                size = SVRange(
                    int(unparsed_fish_data["Size"]["Min"]), int(unparsed_fish_data["Size"]["Max"])
                )
                time_ranges: list[SVRange] = [
                    SVRange(int(time_data["Min"]), int(time_data["Max"]))
                    for time_data in unparsed_fish_data["TimeRanges"]
                ]

                parsed_data[parsed_id] = FishData(
                    id=parsed_id,
                    name=unparsed_fish_data["Name"],
                    size=size,
                    chance_to_dart=int(unparsed_fish_data["ChanceToDart"]),
                    darting_randomness=unparsed_fish_data["DartingRandomness"],
                    time_ranges=time_ranges,
                    weather=unparsed_fish_data["Weather"],
                    max_depth=int(unparsed_fish_data["MaxDepth"]),
                    spawn_multiplier=float(unparsed_fish_data["SpawnMultiplier"]),
                    depth_multiplier=float(unparsed_fish_data["DepthMultiplier"]),
                    fishing_level=int(unparsed_fish_data["FishingLevel"]),
                    tutorial_catch=bool(unparsed_fish_data["TutorialCatch"]),
                ).convert()
            except KeyError as e:
                print(f"One of the values is missing for {unique_id}: {e}")
            except ValueError as e:
                print(f"An incorrect value type was given for {unique_id}: {e}")
        else:
            try:
                size = SVRange(
                    int(unparsed_fish_data["Size"]["Min"]), int(unparsed_fish_data["Size"]["Max"])
                )

                parsed_data[unique_id.replace("{{ModId}}", mod_id)] = CrabpotData(
                    id=parsed_id,
                    name=unparsed_fish_data["Name"],
                    size=size,
                    chance=float(unparsed_fish_data["Chance"]),
                    water_type=unparsed_fish_data["WaterType"],
                ).convert()
            except KeyError as e:
                print(f"One of the values is missing for {unique_id}: {e}")
            except ValueError as e:
                print(f"An incorrect value type was given for {unique_id}: {e}")

    Path("./output").mkdir(parents=True, exist_ok=True)
    Path(f"./output/{file.name}").touch(exist_ok=True)
    with open(Path(f"./output/{file.name}"), "w") as fw:
        json.dump(parsed_data, fw)


if __name__ == "__main__":
    convert_input_files()
