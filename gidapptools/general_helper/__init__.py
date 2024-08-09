import sys
import argparse
from .conversion import bytes2human, human2bytes


def bytes2human_cli():
    _parser = argparse.ArgumentParser()
    _parser.add_argument("value", type=int)

    _arguments = _parser.parse_args()

    _value = getattr(_arguments, "value")

    _calc_value = bytes2human(_value)

    print(_calc_value)


def human2bytes_cli():
    _parser = argparse.ArgumentParser()
    _parser.add_argument("-s", "--strict", action=argparse._StoreTrueAction, required=False)
    _parser.add_argument("value", type=str)

    _arguments = _parser.parse_args()

    _value = getattr(_arguments, "value")

    _strict = getattr(_arguments, "strict", False)

    _calc_value = human2bytes(_value, strict=_strict)

    print(_calc_value)
