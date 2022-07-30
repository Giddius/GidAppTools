import pytest
from pytest import param
import pp
from gidapptools.gid_config.conversion.converter_grammar import parse_specification
from gidapptools.errors import InvalidConverterValue

parse_specification_params = [param("list", "list", {}, None, id="list no kwargs"),
                              param("list(sub_typus=integer)", "list", {"sub_typus": "integer"}, None, id="list with sub_typus"),
                              param("list(sub_typus=integer, split_char=;)", "list", {"sub_typus": "integer", "split_char": ";"}, None, id="list with sub_typus and split_char"),
                              param("list(sub_typus=integer, split_char=$comma$)", "list", {"sub_typus": "integer", "split_char": ","}, None, id="list with sub_typus and split_char_var"),
                              param("path(resolve=true, is_file=False)", "path", {"resolve": True, "is_file": False}, None, id="path with boolean argument"),
                              param("float(round_to=3)", "float", {"round_to": 3}, None, id="float with integer argument"),
                              param("list()", "list", {}, None, id="list no kw but brackets"),
                              param("", "", {}, InvalidConverterValue, id="not valid converter")]


@pytest.mark.parametrize(["raw_specification", "result_typus", "result_kw_arguments", "error"], parse_specification_params)
def test_parse_specification(raw_specification: str,
                             result_typus: str,
                             result_kw_arguments: dict[str, object],
                             error: type[BaseException]):

    if error is not None:
        with pytest.raises(error):
            parsing_result = parse_specification(raw_specification=raw_specification)
    else:
        parsing_result = parse_specification(raw_specification=raw_specification)

        assert parsing_result["typus"] == result_typus
        assert parsing_result["kw_arguments"] == result_kw_arguments
