from typing import TYPE_CHECKING, TypedDict


class RawColorDataItem(TypedDict):
    name: str
    alpha: float
    rgb: tuple[float, float, float]
    rgb_int: tuple[int, int, int]
    hsl: tuple[float, float, float]
    hsv: tuple[float, float, float]
    hex: str


COLOR_DATA: list[RawColorDataItem] = [
    RawColorDataItem(name="black",
                     alpha=1.0,
                     rgb=(0.0, 0.0, 0.0),
                     rgb_int=(0, 0, 0),
                     hsl=(0.0, 0.0, 0.0),
                     hsv=(0.0, 0.0, 0.0),
                     hex="#000000"),

    RawColorDataItem(name="white",
                     alpha=1.0,
                     rgb=(1.0, 1.0, 1.0),
                     rgb_int=(255, 255, 255),
                     hsl=(0.0, 0.0, 1.0),
                     hsv=(0.0, 0.0, 1.0),
                     hex="#FFFFFF"),

    RawColorDataItem(name="green",
                     alpha=1.0,
                     rgb=(0.0, 1.0, 0.0),
                     rgb_int=(0, 255, 0),
                     hsl=(120 / 360, 1.0, 0.5),
                     hsv=(120 / 360, 1.0, 1.0),
                     hex="#00FF00"),

    RawColorDataItem(name="red",
                     alpha=1.0,
                     rgb=(1.0, 0.0, 0.0),
                     rgb_int=(255, 0, 0),
                     hsl=(0.0, 1.0, 0.5),
                     hsv=(0.0, 1.0, 1.0),
                     hex="#FF0000"),

    RawColorDataItem(name="blue",
                     alpha=1.0,
                     rgb=(0.0, 0.0, 1.0),
                     rgb_int=(0, 0, 255),
                     hsl=(240 / 360, 1.0, 0.5),
                     hsv=(240 / 360, 1.0, 1.0),
                     hex="#0000FF"),

    RawColorDataItem(name="yellow",
                     alpha=1.0,
                     rgb=(1.0, 1.0, 0.0),
                     rgb_int=(255, 255, 0),
                     hsl=(60 / 360, 1.0, 0.5),
                     hsv=(60 / 360, 1.0, 1.0),
                     hex="#FFFF00"),

    RawColorDataItem(name="cyan",
                     alpha=1.0,
                     rgb=(0.0, 1.0, 1.0),
                     rgb_int=(0, 255, 255),
                     hsl=(0.5, 1.0, 0.5),
                     hsv=(0.5, 1.0, 1.0),
                     hex="#00FFFF"),

    RawColorDataItem(name="gray",
                     alpha=1.0,
                     rgb=(0.5, 0.5, 0.5),
                     rgb_int=(128, 128, 128),
                     hsl=(0.0, 0.0, 0.5),
                     hsv=(0.0, 0.0, 0.5),
                     hex="#808080"),

    RawColorDataItem(name="purple",
                     alpha=1.0,
                     rgb=(0.5, 0.0, 0.5),
                     rgb_int=(128, 0, 128),
                     hsl=(300 / 360, 1.0, 0.25),
                     hsv=(300 / 360, 1.0, 0.5),
                     hex="#800080"),


]
