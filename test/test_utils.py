import pytest
from utils import encode,decode

def test_encode():
    testdata = [{'txid':'123456789','amount':0.233}]
    encoded = encode(testdata)
    assert(decode(encoded) == testdata)
    