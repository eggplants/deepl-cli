from textwrap import dedent

import pytest

from deepl import DeepLCLI, DeepLCLIError


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


@pytest.mark.skip(reason="auto language detection by path param does not work")
def test_input_too_long() -> None:
    t = DeepLCLI("auto", "ja", 100000)
    with pytest.raises(DeepLCLIError):
        t.translate("test" * 10000)


@pytest.mark.skip(reason="auto language detection by path param does not work")
def test_auto_to_de() -> None:
    t = DeepLCLI("auto", "de", 100000)
    assert t.translate("今日は2022/2/22です。") == "Heute ist der 22.2.2022."


@pytest.mark.skip(reason="auto language detection by path param does not work")
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
    assert (
        res
        == dedent(
            """
        我ら日本国民は、国会において正当に選出された代表を通じて行動し、自ら及び子孫のために、あらゆる国家との平和的協力の成果と、我が国全体の自由の恩恵を確保し、政府の行為による新たな戦争の恐怖を再び招くことのないよう決意し、国民が主権を有することを宣言し、 本憲法を制定する。
        国家の統治は、国民の揺るぎない信頼に基づくものであり、その権威は国民から発し、その権限は国民の代表によって行使され、その恩恵は国民が享受する。
        この人類共通の原則が、本憲法の基礎である。我々は、本憲法に反するすべての憲法、法律、法令、および勅令を廃止する。
        """
        )
        .replace("\n", "")
        .strip()
    )
