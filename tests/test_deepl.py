import pytest

from deepl import DeepLCLI, DeepLCLIError


@pytest.mark.xfail(reason="timeout")
def test1() -> None:
    t = DeepLCLI("en", "ja", 100000)
    assert t.translate("hello") == "ハロー"


@pytest.mark.xfail(reason="timeout")
def test2() -> None:
    t = DeepLCLI("en", "ja", 100000)
    with pytest.raises(DeepLCLIError):
        t.translate("\n")


@pytest.mark.xfail(reason="timeout")
def test3() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("en", "jaa", 100000)


@pytest.mark.xfail(reason="timeout")
def test4() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("enn", "ja", 100000)


@pytest.mark.xfail(reason="timeout")
def test5() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("", "ja", 100000)


@pytest.mark.xfail(reason="timeout")
def test6() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("enn", "jaa", 100000)


@pytest.mark.xfail(reason="timeout")
def test7() -> None:
    t = DeepLCLI("auto", "ja", 100000)
    with pytest.raises(DeepLCLIError):
        t.translate("test" * 10000)


@pytest.mark.xfail(reason="timeout")
def test8() -> None:
    t = DeepLCLI("ja", "de", 100000)
    assert t.translate("今日は2022/2/22です。") == "Heute ist der 22.2.2022."


@pytest.mark.xfail(reason="timeout")
def test9() -> None:
    t = DeepLCLI("auto", "ja", 100000)
    assert t.translate("test") == "試練"
    assert t.translated_fr_lang == "en"
    assert t.translated_to_lang == "ja"

@pytest.mark.xfail(reason="timeout")
def test10() -> None:
    t = DeepLCLI("en", "ja", 100000, use_dom_submit=True)
    assert t.translate("hello") == "ハロー"
