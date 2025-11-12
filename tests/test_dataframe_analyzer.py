import pandas as pd

from src.data.data_loader import DataFrameAnalyzer


def test_dataframe_analyzer_basic_info_and_types():
    df = pd.DataFrame({'a': [1,2], 'b': ['x','y']})
    analyzer = DataFrameAnalyzer(df)
    info = analyzer.get_basic_info()
    assert info['n_rows'] == 2
    assert info['n_columns'] == 2
    assert 'a' in info['columns'] and 'b' in info['columns']

    numeric = analyzer.get_numeric_columns()
    categorical = analyzer.get_categorical_columns()
    assert numeric == ['a']
    assert categorical == ['b']


def test_dataframe_analyzer_missing_values_summary_empty():
    df = pd.DataFrame({'a': [1,2], 'b': ['x','y']})
    analyzer = DataFrameAnalyzer(df)
    mv = analyzer.get_missing_values_summary()
    assert mv.empty
