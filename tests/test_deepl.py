from textwrap import dedent

import pytest

from deepl import DeepLCLI, DeepLCLIError

# The Russian source below is ~700 chars; a complete Japanese rendering is well over this.
MIN_LONG_TRANSLATION_LEN = 200


def test_en_to_ja() -> None:
    t = DeepLCLI("en", "ja", 100000)
    assert t.translate("hello.") in ("こんにちは", "こんにちは。")


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


def test_input_too_long() -> None:
    t = DeepLCLI("auto", "ja", 100000)
    with pytest.raises(DeepLCLIError):
        t.translate("test" * 10000)


def test_auto_to_de() -> None:
    t = DeepLCLI("auto", "de", 100000)
    # DeepL words the date either way, so both spellings count as the same translation.
    assert t.translate("今日は2022/2/22です。") in (
        "Heute ist der 22.2.2022.",
        "Heute ist der 22. Februar 2022.",
    )


def test_lang_attrs() -> None:
    t = DeepLCLI("auto", "ja", 100000)
    assert t.translate("test") in ("試練", "テスト")
    assert t.translated_fr_lang == "en"
    assert t.translated_to_lang == "ja"


@pytest.mark.asyncio
async def test_translate_async() -> None:
    t = DeepLCLI("en", "ja", 100000)
    res = await t.translate_async("hello.")
    assert res in ("こんにちは", "こんにちは。")


@pytest.mark.asyncio
async def test_translate_async_long_text() -> None:
    t = DeepLCLI("ru", "ja", 100000)
    res = await t.translate_async(
        dedent(
            """
            Мы, японский народ, действуя через посредство наших должным образом избранных представителей в Парламенте и исполнены решимости обеспечить для себя и для своих потомков плоды мирного сотрудничества со всеми нациями и благословение свободы для всей нашей страны, не допустить ужасов новой войны в результате действий правительств, провозглашаем, что народ облечён суверенитетом, и устанавливаем настоящую Конституцию.
            Государственное правление основывается на непоколебимом доверии народа, его авторитет исходит от народа, его полномочия осуществляются представителями народа, а благами его пользуется народ.
            Этот принцип, общий для всего человечества, и на нём основана настоящая Конституция.
            Мы отменяем все конституции, законы и подзаконные акты, а также рескрипты, противоречащие настоящей Конституции.
            """,
        )
        .strip()
        .replace("\n", " "),
    )
    # DeepL rewords its output over time, so assert the translation is complete
    # rather than pinning one exact rendering.
    assert "[...]" not in res
    assert res.endswith("。")
    assert len(res) > MIN_LONG_TRANSLATION_LEN
    for keyword in ("日本国民", "憲法", "主権", "代表", "自由"):
        assert keyword in res
