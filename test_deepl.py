import pytest

from deepl import deepl
import json

T = deepl.DeepLCLI()

def test1():
    T = deepl.DeepLCLI()
    assert T.translate('hello', 'en', 'ja') == 'こんにちわ'


def test2():
    T = deepl.DeepLCLI()
    with pytest.raises(deepl.DeepLCLIArgCheckingError):
        T.translate('\n', 'en', 'ja')


def test3():
    T = deepl.DeepLCLI()
    with pytest.raises(TypeError):
        T.translate('test')


def test4():
    T = deepl.DeepLCLI()
    with pytest.raises(deepl.DeepLCLIArgCheckingError):
        T.translate('test', 'en', 'jaa')


def test5():
    T = deepl.DeepLCLI()
    with pytest.raises(deepl.DeepLCLIArgCheckingError):
        T.translate('test', 'enn', 'ja')


def test6():
    T = deepl.DeepLCLI()
    with pytest.raises(deepl.DeepLCLIArgCheckingError):
        assert T.translate('test', '', 'ja') == 'test'
