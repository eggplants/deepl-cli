import pytest

from deepl import DeepLCLI, DeepLCLIError


def test1() -> None:
    t = DeepLCLI("en", "ja", 100000)
    assert t.translate("hello") == "こんにちわ"


def test2() -> None:
    t = DeepLCLI("en", "ja", 100000)
    with pytest.raises(DeepLCLIError):
        t.translate("\n")


def test3() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("en", "jaa", 100000)


def test4() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("enn", "ja", 100000)


def test5() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("", "ja", 100000)


def test6() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("enn", "jaa", 100000)


def test7() -> None:
    t = DeepLCLI("auto", "ja", 100000)
    with pytest.raises(DeepLCLIError):
        t.translate("test" * 10000)


def test8() -> None:
    t = DeepLCLI("ja", "de", 100000)
    assert t.translate("今日は2022/2/22です。") == "Heute ist der 22.2.2022."


def test9() -> None:
    t = DeepLCLI("auto", "ja", 100000)
    assert t.translate("test") == "テスト"
    assert t.translated_fr_lang == "en"
    assert t.translated_to_lang == "ja"
