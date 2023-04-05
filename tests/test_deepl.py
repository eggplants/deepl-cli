import pytest

from deepl import DeepLCLI, DeepLCLIError


def test_en_to_ja() -> None:
    t = DeepLCLI("en", "ja", 100000)
    assert t.translate("hello.") == "こんにちは"


def test_blank_script() -> None:
    t = DeepLCLI("en", "ja", 100000)
    with pytest.raises(DeepLCLIError):
        t.translate("\n")


def test_invalid_input_lang() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("enn", "ja", 100000)


def test_invalid_output_lang() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("en", "jaa", 100000)


def test_blank_input_lang() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("", "ja", 100000)


def test_invalid_input_and_output_lang() -> None:
    with pytest.raises(DeepLCLIError):
        DeepLCLI("enn", "jaa", 100000)


def test_input_language_auto() -> None:
    t = DeepLCLI("auto", "ja", 100000)
    with pytest.raises(DeepLCLIError):
        t.translate("test" * 10000)


def test_ja_to_de() -> None:
    t = DeepLCLI("ja", "de", 100000)
    assert t.translate("今日は2022/2/22です。") == "Heute ist der 22.2.2022."


def test_lang_attrs() -> None:
    t = DeepLCLI("auto", "ja", 100000)
    assert t.translate("test") == "試練"
    assert t.translated_fr_lang == "en"
    assert t.translated_to_lang == "ja"


def test10() -> None:
    t = DeepLCLI("en", "ja", 100000, use_dom_submit=True)
    assert t.translate("hello.") == "こんにちは"
