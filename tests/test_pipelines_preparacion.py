import pandas as pd
import numpy as np

from src.pipelines import preparar_datos_para_modelado


def test_preparar_datos_para_modelado_returns_expected_shapes():
    # Synthetic small dataset with mixed types and simple target
    df = pd.DataFrame({
        'num1': [1, 2, 3, 4, 5, 6],
        'num2': [10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
        'cat': ['a', 'b', 'a', 'b', 'a', 'b'],
        'target': [0, 1, 0, 1, 0, 1]
    })

    X_train, X_test, y_train, y_test, pre = preparar_datos_para_modelado(df, target_column='target', test_size=0.33, random_state=1)

    # Splits sizes
    assert len(X_train) + len(X_test) == len(df)
    assert len(y_train) + len(y_test) == len(df)

    # ColumnTransformer fitted on train
    # Check it has transformers_ attribute after fit
    assert hasattr(pre, 'transformers_')
