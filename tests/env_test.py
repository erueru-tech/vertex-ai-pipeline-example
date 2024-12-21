from src.env import strtobool


def test_strtobool1() -> None:
    """.strtoboolが引数に対して意図した真偽値を返す"""
    assert strtobool("True") and strtobool("true")
    assert not (strtobool("False") or strtobool("false"))
    assert strtobool(None) is None and strtobool("test") is None
