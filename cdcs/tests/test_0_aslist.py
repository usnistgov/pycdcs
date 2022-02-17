
import pandas as pd

from cdcs import aslist, iaslist

def test_aslist():

    # Test single values become lists
    assert aslist('a') == ['a']

    # Test long strings remain together
    assert aslist('abba') == ['abba']

    # Test long bytes remain together
    assert aslist(b'ac/dc') == [b'ac/dc']

    # Test pandas.Series() remain together
    series = pd.Series({'a':'value', 'b': 4})
    assert aslist(series) == [series]

    # Test collections become lists
    assert aslist(('a','b','c')) == ['a', 'b', 'c']
    assert sorted(aslist({'a','b','c'})) == ['a', 'b', 'c']
    assert aslist(['a','b','c']) == ['a', 'b', 'c']

def test_iaslist():

    # Test single values
    for given, expected in zip(iaslist('a'), ['a']):
        assert given == expected

    # Test long strings remain together
    for given, expected in zip(iaslist('abba'), ['abba']):
        assert given == expected

    # Test long bytes remain together
    for given, expected in zip(iaslist(b'ac/dc'), [b'ac/dc']):
        assert given == expected

    # Test pandas.Series() remain together
    series = pd.Series({'a':'value', 'b': 4})
    for given, expected in zip(iaslist(series), [series]):
        assert all(given == expected)

    # Test collections become lists
    for given1, given2, given3, expected in zip(iaslist(('a','b','c')),
                                                sorted(iaslist({'a','b','c'})),
                                                iaslist(['a','b','c']),
                                                ['a', 'b', 'c']):
        assert given1 == expected
        assert given2 == expected
        assert given3 == expected