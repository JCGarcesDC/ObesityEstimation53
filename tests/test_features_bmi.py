import pandas as pd
import pytest

from src.features.feature_engineering import BMICalculator, FeatureEngineeringPipeline


def test_bmi_calculator_computes_imc():
    df = pd.DataFrame({'weight': [70.0, 80.0], 'height': [1.75, 1.60]})
    bmi = BMICalculator(weight_col='weight', height_col='height', output_col='imc')

    df_out = bmi.fit_transform(df)
    expected = [70.0 / (1.75**2), 80.0 / (1.60**2)]

    assert 'imc' in df_out.columns
    assert pytest.approx(df_out['imc'].tolist(), rel=1e-6) == expected


def test_bmi_calculator_missing_columns_raises():
    df = pd.DataFrame({'weight': [70.0]})
    bmi = BMICalculator()
    with pytest.raises(ValueError):
        bmi.fit(df)


def test_feature_engineering_pipeline_sequence():
    df = pd.DataFrame({'weight': [70.0], 'height': [1.75]})
    pipeline = FeatureEngineeringPipeline([BMICalculator()])
    out = pipeline.fit_transform(df)
    assert 'imc' in out.columns
