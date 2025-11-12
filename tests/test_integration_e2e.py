import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline

from src.preprocessing.cleaning import DataCleaner
from src.features.feature_engineering import BMICalculator
from src.pipelines import preparar_datos_para_modelado


def test_e2e_pipeline_simple():
    # Minimal, separable synthetic data resembling BMI influence
    rng = np.random.RandomState(0)
    n = 60
    height = rng.normal(1.70, 0.05, size=n)
    weight = rng.normal(70, 8, size=n)
    imc = weight / (height**2)
    # Label as standardized strings expected by DataCleaner.OBESITY_MAPPING
    target = np.where(imc > 25, 'overweight_level_i', 'normal_weight')

    df = pd.DataFrame({
        'Height': height,
        'Weight': weight,
        'Gender': rng.choice(['male','female'], size=n),
        'NObeyesdad': target  # standardized labels for mapping
    })

    # Clean and feature engineer
    cleaner = DataCleaner(target_col='NObeyesdad', standardize_columns=True, standardize_values=True)
    df_clean = cleaner.fit_transform(df)

    bmi = BMICalculator(weight_col='weight', height_col='height', output_col='imc')
    df_feat = bmi.fit_transform(df_clean)

    X_train, X_test, y_train, y_test, pre = preparar_datos_para_modelado(
        df_feat.rename(columns={'nobeyesdad': 'target'}), target_column='target', test_size=0.25, random_state=42
    )

    # Train a simple model with the preprocessor
    clf = Pipeline([('pre', pre), ('clf', LogisticRegression(max_iter=500))])
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    # Basic sanity metrics
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    assert acc >= 0.6
    assert f1 >= 0.6
