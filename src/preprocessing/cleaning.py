"""
Data Cleaning and Preprocessing Module - Refactored with OOP.

This module provides concrete implementations for data cleaning,
outlier detection, and missing value imputation.

Role Assignments:
- Data Engineer: Primary owner - implements data quality pipelines
- ML Engineer: Integrates preprocessing into ML pipelines
- Data Scientist: Configures cleaning parameters
- Software Engineer: Maintains class architecture
"""

from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import numpy as np
import logging

from src.base.base_preprocessor import BasePreprocessor

logger = logging.getLogger(__name__)


class DataCleaner(BasePreprocessor):
    """
    Comprehensive data cleaning preprocessor.
    
    Responsibilities:
    - Data Engineer: Primary owner - maintains data quality logic
    - Data Scientist: Configures cleaning strategies
    
    This class handles:
    - Column standardization (naming)
    - Duplicate removal
    - Missing value imputation
    - Categorical value standardization
    - Target encoding
    
    Example:
        >>> cleaner = DataCleaner(
        ...     target_col='NObeyesdad',
        ...     cols_to_drop=['mixed_type_col']
        ... )
        >>> df_clean = cleaner.fit_transform(df)
    """
    
    # Obesity level mapping (ordinal encoding)
    OBESITY_MAPPING = {
        'insufficient_weight': 0,
        'normal_weight': 1,
        'overweight_level_i': 2,
        'overweight_level_ii': 3,
        'obesity_type_i': 4,
        'obesity_type_ii': 5,
        'obesity_type_iii': 6
    }
    
    def __init__(
        self,
        target_col: str = 'NObeyesdad',
        cols_to_drop: Optional[List[str]] = None,
        numeric_impute_strategy: str = 'median',
        categorical_impute_strategy: str = 'most_frequent',
        standardize_columns: bool = True,
        standardize_values: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize data cleaner.
        
        Args:
            target_col: Name of target column
            cols_to_drop: List of columns to drop
            numeric_impute_strategy: Strategy for numeric imputation ('mean', 'median', 'mode')
            categorical_impute_strategy: Strategy for categorical imputation ('most_frequent', 'constant')
            standardize_columns: Whether to standardize column names
            standardize_values: Whether to standardize categorical values
            config: Additional configuration
        """
        super().__init__(config)
        self.target_col = target_col.lower() if standardize_columns else target_col
        self.cols_to_drop = cols_to_drop or []
        self.numeric_impute_strategy = numeric_impute_strategy
        self.categorical_impute_strategy = categorical_impute_strategy
        self.standardize_columns = standardize_columns
        self.standardize_values = standardize_values
        
        # Will be fitted
        self._numeric_impute_values = {}
        self._categorical_impute_values = {}
        self._numeric_cols = []
        self._categorical_cols = []
    
    def fit(self, df: pd.DataFrame, target_col: Optional[str] = None) -> 'DataCleaner':
        """
        Fit the cleaner to training data.
        
        Learns imputation values and column types from training data.
        
        Args:
            df: Training DataFrame
            target_col: Optional override for target column
            
        Returns:
            self: Fitted cleaner
        """
        if target_col:
            self.target_col = target_col
        
        logger.info("Fitting DataCleaner...")
        
        # Standardize column names if requested
        df_work = df.copy()
        if self.standardize_columns:
            df_work = self._standardize_column_names(df_work)
        
        # Identify column types
        self._numeric_cols = df_work.select_dtypes(include=[np.number]).columns.tolist()
        self._categorical_cols = df_work.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Remove target from feature lists if present
        if self.target_col in self._numeric_cols:
            self._numeric_cols.remove(self.target_col)
        if self.target_col in self._categorical_cols:
            self._categorical_cols.remove(self.target_col)
        
        # Learn imputation values
        for col in self._numeric_cols:
            if col in self.cols_to_drop:
                continue
            
            if self.numeric_impute_strategy == 'mean':
                self._numeric_impute_values[col] = df_work[col].mean()
            elif self.numeric_impute_strategy == 'median':
                self._numeric_impute_values[col] = df_work[col].median()
            elif self.numeric_impute_strategy == 'mode':
                self._numeric_impute_values[col] = df_work[col].mode()[0]
        
        for col in self._categorical_cols:
            if self.categorical_impute_strategy == 'most_frequent':
                self._categorical_impute_values[col] = df_work[col].mode()[0]
            # 'constant' strategy doesn't need fitting
        
        self._fitted_params = {
            'numeric_impute_values': self._numeric_impute_values.copy(),
            'categorical_impute_values': self._categorical_impute_values.copy(),
            'numeric_cols': self._numeric_cols.copy(),
            'categorical_cols': self._categorical_cols.copy()
        }
        
        self.is_fitted = True
        logger.info("DataCleaner fitted successfully")
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data using fitted parameters.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        self._check_is_fitted()
        
        logger.info("Transforming data with DataCleaner...")
        df_clean = df.copy()
        
        # 1. Standardize column names
        if self.standardize_columns:
            df_clean = self._standardize_column_names(df_clean)
        
        # 2. Drop specified columns
        cols_present = [col for col in self.cols_to_drop if col in df_clean.columns]
        if cols_present:
            df_clean = df_clean.drop(columns=cols_present)
            logger.info(f"Dropped columns: {cols_present}")
        
        # 3. Remove duplicates
        n_duplicates = df_clean.duplicated().sum()
        if n_duplicates > 0:
            df_clean = df_clean.drop_duplicates()
            logger.info(f"Removed {n_duplicates} duplicate rows")
        
        # 4. Handle target column nulls
        if self.target_col in df_clean.columns:
            n_target_nulls = df_clean[self.target_col].isnull().sum()
            if n_target_nulls > 0:
                df_clean = df_clean.dropna(subset=[self.target_col])
                logger.info(f"Dropped {n_target_nulls} rows with null target")
        
        # 5. Standardize categorical values
        if self.standardize_values:
            for col in self._categorical_cols:
                if col in df_clean.columns:
                    df_clean[col] = (
                        df_clean[col]
                        .astype(str)
                        .str.strip()
                        .str.replace(' ', '_')
                        .str.lower()
                    )
        
        # 6. Ensure numeric types
        for col in self._numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # 7. Impute missing values
        for col, value in self._numeric_impute_values.items():
            if col in df_clean.columns:
                n_missing = df_clean[col].isnull().sum()
                if n_missing > 0:
                    df_clean[col] = df_clean[col].fillna(value)
                    logger.debug(f"Imputed {n_missing} values in {col} with {value:.2f}")
        
        for col, value in self._categorical_impute_values.items():
            if col in df_clean.columns:
                n_missing = df_clean[col].isnull().sum()
                if n_missing > 0:
                    df_clean[col] = df_clean[col].fillna(value)
                    logger.debug(f"Imputed {n_missing} values in {col} with {value}")
        
        # 8. Encode target if present
        if self.target_col in df_clean.columns:
            df_clean = self._encode_target(df_clean)
        
        logger.info(f"Data cleaned: {df_clean.shape}")
        return df_clean
    
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to lowercase with underscores."""
        df_new = df.copy()
        df_new.columns = (
            df_new.columns
            .str.strip()
            .str.replace(' ', '_')
            .str.lower()
        )
        return df_new
    
    def _encode_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode target variable using ordinal mapping."""
        df_new = df.copy()
        df_new[self.target_col] = df_new[self.target_col].map(self.OBESITY_MAPPING)
        
        # Log any unmapped values
        n_unmapped = df_new[self.target_col].isnull().sum()
        if n_unmapped > 0:
            logger.warning(f"{n_unmapped} target values could not be mapped")
        
        return df_new


class OutlierDetector(BasePreprocessor):
    """
    Outlier detection and handling preprocessor.
    
    Responsibilities:
    - Data Scientist: Defines outlier detection strategies
    - Data Engineer: Implements outlier handling logic
    
    Supports multiple outlier detection methods:
    - IQR (Interquartile Range)
    - Z-score
    - Business rules
    
    Example:
        >>> detector = OutlierDetector(method='iqr', iqr_factor=1.5)
        >>> df_no_outliers = detector.fit_transform(df)
    """
    
    def __init__(
        self,
        method: str = 'iqr',
        iqr_factor: float = 1.5,
        z_threshold: float = 3.0,
        business_rules: Optional[Dict[str, Tuple[float, float]]] = None,
        action: str = 'remove',  # 'remove', 'cap', or 'flag'
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize outlier detector.
        
        Args:
            method: Detection method ('iqr', 'zscore', 'business_rules')
            iqr_factor: IQR multiplier (typically 1.5 or 3.0)
            z_threshold: Z-score threshold
            business_rules: Dict mapping column names to (min, max) tuples
            action: What to do with outliers ('remove', 'cap', 'flag')
            config: Additional configuration
        """
        super().__init__(config)
        self.method = method
        self.iqr_factor = iqr_factor
        self.z_threshold = z_threshold
        self.business_rules = business_rules or {}
        self.action = action
        
        # Will be fitted
        self._bounds = {}
    
    def fit(self, df: pd.DataFrame, target_col: Optional[str] = None) -> 'OutlierDetector':
        """
        Fit the detector to training data.
        
        Learns outlier bounds from training data.
        
        Args:
            df: Training DataFrame
            target_col: Optional target column to exclude
            
        Returns:
            self: Fitted detector
        """
        logger.info(f"Fitting OutlierDetector with method={self.method}...")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col and target_col in numeric_cols:
            numeric_cols.remove(target_col)
        
        if self.method == 'iqr':
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - self.iqr_factor * IQR
                upper = Q3 + self.iqr_factor * IQR
                self._bounds[col] = (lower, upper)
        
        elif self.method == 'zscore':
            for col in numeric_cols:
                mean = df[col].mean()
                std = df[col].std()
                lower = mean - self.z_threshold * std
                upper = mean + self.z_threshold * std
                self._bounds[col] = (lower, upper)
        
        elif self.method == 'business_rules':
            self._bounds = self.business_rules.copy()
        
        self._fitted_params = {'bounds': self._bounds.copy()}
        self.is_fitted = True
        logger.info("OutlierDetector fitted successfully")
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data by handling outliers.
        
        Args:
            df: DataFrame to process
            
        Returns:
            pd.DataFrame: DataFrame with outliers handled
        """
        self._check_is_fitted()
        
        logger.info(f"Detecting outliers with action={self.action}...")
        df_out = df.copy()
        
        total_outliers = 0
        
        for col, (lower, upper) in self._bounds.items():
            if col not in df_out.columns:
                continue
            
            outlier_mask = (df_out[col] < lower) | (df_out[col] > upper)
            n_outliers = outlier_mask.sum()
            
            if n_outliers > 0:
                total_outliers += n_outliers
                
                if self.action == 'remove':
                    df_out = df_out[~outlier_mask]
                    logger.info(
                        f"{col}: removed {n_outliers} outliers "
                        f"(bounds: [{lower:.2f}, {upper:.2f}])"
                    )
                
                elif self.action == 'cap':
                    # Usar clip() para evitar FutureWarning de incompatibilidad de dtype
                    df_out[col] = df_out[col].clip(lower=lower, upper=upper)
                    logger.info(
                        f"{col}: capped {n_outliers} outliers "
                        f"(bounds: [{lower:.2f}, {upper:.2f}])"
                    )
                
                elif self.action == 'flag':
                    df_out[f'{col}_is_outlier'] = outlier_mask
                    logger.info(f"{col}: flagged {n_outliers} outliers")
        
        logger.info(f"Total outliers detected: {total_outliers}")
        return df_out
    
    def detect_outliers(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Detect outliers without modifying the data.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dict mapping column names to boolean Series indicating outliers
        """
        self._check_is_fitted()
        
        outlier_masks = {}
        for col, (lower, upper) in self._bounds.items():
            if col in df.columns:
                outlier_masks[col] = (df[col] < lower) | (df[col] > upper)
        
        return outlier_masks
    
    def get_outlier_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get a summary of outliers in the dataset.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            pd.DataFrame: Summary with columns: column, n_outliers, percentage, bounds
        """
        self._check_is_fitted()
        
        outlier_masks = self.detect_outliers(df)
        
        summary_data = []
        for col, mask in outlier_masks.items():
            n_outliers = mask.sum()
            percentage = (n_outliers / len(df)) * 100
            lower, upper = self._bounds[col]
            
            summary_data.append({
                'column': col,
                'n_outliers': int(n_outliers),
                'percentage': round(percentage, 2),
                'lower_bound': round(lower, 2),
                'upper_bound': round(upper, 2)
            })
        
        return pd.DataFrame(summary_data).sort_values('n_outliers', ascending=False)
