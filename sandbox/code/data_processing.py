"""
Data Processing Utilities

Common data processing functions for ETL pipelines.
"""

import pandas as pd
from typing import List, Dict, Any


def clean_dataframe(df: pd.DataFrame, drop_na_columns: List[str] = None) -> pd.DataFrame:
    """
    Clean a pandas DataFrame by handling missing values and duplicates.

    Args:
        df: Input DataFrame
        drop_na_columns: List of columns to drop rows if NA

    Returns:
        Cleaned DataFrame
    """
    # Remove duplicates
    df = df.drop_duplicates()

    # Drop rows with NA in specified columns
    if drop_na_columns:
        df = df.dropna(subset=drop_na_columns)

    # Convert column names to lowercase and replace spaces with underscores
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]

    return df


def aggregate_by_group(df: pd.DataFrame, group_col: str, agg_dict: Dict[str, Any]) -> pd.DataFrame:
    """
    Aggregate DataFrame by group with custom aggregation functions.

    Args:
        df: Input DataFrame
        group_col: Column to group by
        agg_dict: Dictionary mapping column names to aggregation functions

    Returns:
        Aggregated DataFrame
    """
    return df.groupby(group_col).agg(agg_dict).reset_index()


def extract_date_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Extract date features from a datetime column.

    Args:
        df: Input DataFrame
        date_col: Name of datetime column

    Returns:
        DataFrame with additional date feature columns
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    df[f'{date_col}_year'] = df[date_col].dt.year
    df[f'{date_col}_month'] = df[date_col].dt.month
    df[f'{date_col}_day'] = df[date_col].dt.day
    df[f'{date_col}_dayofweek'] = df[date_col].dt.dayofweek
    df[f'{date_col}_quarter'] = df[date_col].dt.quarter

    return df
