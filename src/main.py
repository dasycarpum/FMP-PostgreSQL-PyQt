#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from src.models.base import Session
from src.models.fmp.stock import StockSymbol, CompanyProfile, DailyChartEOD # pylint: disable=unused-import
from src.dal.fmp.database_query import StockQuery
from src.business_logic.fmp.data_analytics import   clean_data_for_company_profiles_clustering
from src.services.plot import plot_scatterplot
from src.services.ml import (detection_and_exclusion_of_outliers_ee,
    normalize_data, detection_and_exclusion_of_outliers_if,
    detection_and_exclusion_of_left_quantile, apply_hierarchical_clustering, apply_pca)


def main():
    """
    Main script entry point.

    This function serves as the entry point for the script. It takes no 
    arguments, returns nothing. It is intended to be called when the script is 
    executed directly.

    Args:
        None.

    Returns:
        None.
    
    Raises:
        No exception is raised by this function.
    """
    db_session = Session()
    stock_query = StockQuery(db_session)

    # Extracting stock data from company profiles table
    data = stock_query.extract_data_for_company_profiles_clustering()

    # Cleaning the data and converting to dataframe
    df = clean_data_for_company_profiles_clustering(data)

    # Outliers management
    variables = ['beta', 'vol_avg', 'mkt_cap']

    df_beta_purged_o = detection_and_exclusion_of_outliers_ee(df,
                    variables[0], 0.02)
    df_mkt_purged_o = detection_and_exclusion_of_outliers_if(df_beta_purged_o,
                    variables[2], 0.0001)

    # First quantile management
    df_mkt_purged_q = detection_and_exclusion_of_left_quantile(df_mkt_purged_o, 'mkt_cap', 0.25)

    df_vol_purged_q = detection_and_exclusion_of_left_quantile(df_mkt_purged_q, 'vol_avg', 0.25)

    print(df_vol_purged_q.head())
    print(df_vol_purged_q.info())
    print(df_vol_purged_q.describe())

    # Normalizing the numerical columns
    df_normalized = normalize_data(df_vol_purged_q, variables)

    print(df_normalized.head())
    print(df_normalized.info())
    print(df_normalized.describe())

    # Clustering
    df_result = apply_hierarchical_clustering(df_normalized, variables)

    print(df_result.head())
    print(df_result['cluster'].value_counts())
    print(df_result[df_result['stock_id']==21395])  # Total Energie

    # Scatter plot
    df_pca = apply_pca(df_result, variables, 2)
    df_pca = df_pca[df_pca['cluster'].isin([4, 5, 6, 9])]
    plot_scatterplot(df_pca, 'PC1', 'PC2', 'cluster')


if __name__ == "__main__":
    main()
