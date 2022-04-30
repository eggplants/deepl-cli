import pytest

from deepl import DeepLCLI, DeepLCLIError


def test1() -> None:
    t = DeepLCLI("en", "ja")
    assert t.translate("hello") == "こんにちわ"


def test2() -> None:
    t = DeepLCLI("en", "ja")
    with pytest.raises(DeepLCLIError):
        t.translate("\n")


def test3() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("en", "jaa")


def test4() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("enn", "ja")


def test5() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("", "ja")


def test6() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("enn", "jaa")


def test7() -> None:
    t = DeepLCLI("auto", "ja")
    with pytest.raises(DeepLCLIError):
        t.translate("test" * 10000)


def test8() -> None:
    t = DeepLCLI("ja", "de")
    assert t.translate("今日は2022/2/22です。") == "Heute ist der 22.2.2022."

@pytest.mark.xfail
def test9() -> None:
    t = DeepLCLI("auto", "ja")
    assert t.translate("test") == "テスト"
    assert t.translated_fr_lang == "en"
    assert t.translated_to_lang == "ja"
