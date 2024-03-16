#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: the entry point of the program.

"""

from scipy import stats
from src.models.base import Session
from src.models.fmp.stock import StockSymbol, CompanyProfile, DailyChartEOD # pylint: disable=unused-import
from src.dal.fmp.database_query import StockQuery
from src.business_logic.fmp.data_analytics import   clean_data_for_company_profiles_clustering
from src.services.plot import (plot_boxplots, plot_distributions,
    display_correlation_matrix)
from src.services.ml import (detection_and_exclusion_of_outliers_ee,
    detection_and_exclusion_of_outliers_if, normalize_data,
    determine_cluster_numbers_with_kmeans, apply_kmeans_clustering)


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

    df_beta_purged = detection_and_exclusion_of_outliers_ee(df,
                    variables[0], 0.02)
    df_mkt_purged = detection_and_exclusion_of_outliers_if(df_beta_purged,
                    variables[2], 0.0001)

    # Normalizing the numerical columns
    df_normalized = normalize_data(df_mkt_purged, variables)

    plot_boxplots(df_normalized, variables)
    plot_distributions(df_normalized, variables)

    print(df_normalized.head())
    print(df_normalized.info())
    print(df_normalized.describe())

    # Correlation analysis
    display_correlation_matrix(df_normalized, variables)
    print(stats.pearsonr(df_normalized['vol_avg'],df_normalized['mkt_cap']))
    print(stats.pearsonr(df_normalized['beta'],df_normalized['mkt_cap']))
    print(stats.pearsonr(df_normalized['vol_avg'],df_normalized['beta']))

    # Determining the number of clusters
    scores = determine_cluster_numbers_with_kmeans(df_normalized)
    print(scores)

    # Running the KMeans clustering algorithm
    df_result = apply_kmeans_clustering(df_normalized, scores)
    print(df_result.head())
    print(df_result['cluster'].value_counts())
    print(df_result[df_result['stock_id']==21395])  # Total Energie


if __name__ == "__main__":
    main()
