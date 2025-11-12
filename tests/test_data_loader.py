import pandas as pd
import os

from src.data.data_loader import CSVDataLoader


def test_csv_data_loader_loads(tmp_path):
    csv_path = tmp_path / 'sample.csv'
    pd.DataFrame({'a': [1,2], 'b': ['x','y']}).to_csv(csv_path, index=False)

    loader = CSVDataLoader(str(csv_path))
    df = loader.load_with_validation()

    assert df is not None
    assert df.shape == (2,2)
    assert set(df.columns) == {'a','b'}


def test_csv_data_loader_invalid_path_returns_none(tmp_path):
    loader = CSVDataLoader(str(tmp_path / 'missing.csv'))
    assert loader.load_with_validation() is None
