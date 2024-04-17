#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-12

@author: Roland VANDE MAELE

@abstract: this file contains functions for prepare and run machine learning.

"""

import pandas as pd
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, fcluster


def detection_and_exclusion_of_outliers_ee(df: pd.DataFrame, variable: str,
    contamination: float = 0.01) -> pd.DataFrame:
    """
    Identifies and excludes outliers for a specified variable in the DataFrame 
    using the EllipticEnvelope method (models that assume a normal distribution of data).

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        variable (str): The name of the column for which outliers should be 
        detected and excluded.
        contamination (float, optional): The proportion of observations to be 
        considered as outliers. Defaults to 0.01.

    Returns:
        pandas.DataFrame: A new DataFrame with outliers excluded from the 
        specified variable.

    Raises:
        ValueError: If the specified variable is not found in the DataFrame.
    """

    if variable not in df.columns:
        raise ValueError(f"Variable '{variable}' not found in the DataFrame.")

    # Initialize and fit the EllipticEnvelope
    envelope = EllipticEnvelope(contamination=contamination)
    envelope.fit(df[[variable]])

    # Predict the outliers (-1 for outliers, 1 for inliers)
    outliers = envelope.predict(df[[variable]])

    # Create a mask for inliers (non-outliers)
    inliers_mask = outliers == 1

    # Return a new DataFrame without the outliers
    return df[inliers_mask]

def detection_and_exclusion_of_outliers_if(df: pd.DataFrame, variable: str,
    contamination: float = 0.01) -> pd.DataFrame:
    """
    Identifies and excludes outliers for a specified variable in the DataFrame 
    using the IsolationForest method (works well on data with asymmetric distributions)

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        variable (str): The name of the column for which outliers should be 
        detected and excluded.
        contamination (float, optional): The proportion of observations to be 
        considered as outliers. Defaults to 0.01.

    Returns:
        pandas.DataFrame: A new DataFrame with outliers excluded from the 
        specified variable.

    Raises:
        ValueError: If the specified variable is not found in the DataFrame.
    """

    if variable not in df.columns:
        raise ValueError(f"Variable '{variable}' not found in the DataFrame.")

    # Initialize, fit and predict the IsolationForest
    iso_forest = IsolationForest(contamination=contamination)
    outliers = iso_forest.fit_predict(df[[variable]])

    # Filter outliers (considered -1 by Isolation Forest)
    df_filtered = df[outliers != -1]

    # Return a new DataFrame without the outliers
    return df_filtered

def detection_and_exclusion_of_left_quantile(df: pd.DataFrame, variable: str,
                                             quantile: float = 0.1) -> pd.DataFrame:
    """
    Removes records from a DataFrame that fall below a specified quantile
    for a given variable. This can be useful for excluding outliers or 
    anomalies in the lower part of a distribution, potentially helping to 
    normalize the data or reduce skewness.

    Args:
        df (pd.DataFrame): The input DataFrame from which records will be filtered.
        variable (str): The name of the column in `df` based on which the 
        filtering will be performed. This column should contain numerical data.
        quantile (float, optional): The quantile below which records will be 
        removed. Must be a float between 0 and 1, exclusive. Defaults to 0.1, 
        representing the 1st decile.

    Returns:
        pd.DataFrame: A DataFrame with records below the specified quantile of 
        the `variable` column excluded.

    Raises:
        ValueError: If the `variable` is not found in the DataFrame's columns.

    """
    if variable not in df.columns:
        raise ValueError(f"Variable '{variable}' not found in the DataFrame.")

    # Step 1: Calculate the quantile value for the targeted column
    left_quantile = df[variable].quantile(quantile)

    # Step 2: Filter the DataFrame to exclude records in the specified quantile
    df_filtered = df[df[variable] > left_quantile]

    return df_filtered


def normalize_data(df: pd.DataFrame, columns_to_normalize: list) -> pd.DataFrame:
    """
    Normalizes the numerical columns of DataFrame.

    This function applies standard normalization to the numerical columns of 
    the DataFrame, which re-scales the features to have a mean of 0 and a 
    standard deviation of 1. This step is crucial for many machine learning 
    algorithms to perform correctly.

    Args:
        df (pd.DataFrame): The DataFrame containing data.
        columns_to_normalize (list): A list of column names to be normalized.

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input, where the 
        numerical data has been normalized.

    Raises:
        ValueError: If any of the columns to normalize are not found in the DataFrame.

    """
    # Check if all specified variables exist in the DataFrame
    missing_cols = [col for col in columns_to_normalize if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Variables {missing_cols} not found in the DataFrame.")

    # Work on a copy of the DataFrame to avoid SettingWithCopyWarning
    df_copy = df.copy()

    # Initialize the scaler
    scaler = StandardScaler()

    # Fit the scaler to the data and transform it
    df_copy[columns_to_normalize] = scaler.fit_transform(
                                    df_copy[columns_to_normalize])

    return df_copy

def determine_cluster_numbers_with_kmeans(df: pd.DataFrame, columns: list) -> dict:
    """
    Determines the optimal number of clusters for KMeans clustering.

    This function evaluates the silhouette score for a range of cluster numbers 
    to determine the optimal number of clusters for KMeans clustering. The 
    silhouette score is used as a metric to judge the distance between the 
    resulting clusters. The function iterates over a predefined range of 
    cluster numbers, computes the KMeans clustering for each, and calculates 
    the silhouette score.

    Args:
        df (pd.DataFrame): The normalized dataset used for clustering. This 
        should be a 2D array or DataFrame where rows represent samples and 
        columns represent features.
        columns (list): List of column names to be used for determining cluster numbers.

    Returns:
        dict: A dictionary with the number of clusters as keys and the 
        corresponding silhouette scores as values. This allows for easy 
        identification of the cluster number with the highest silhouette score, 
        which is considered the optimal number of clusters.

    Example:
        >>> data_normalized = np.array([[0.1, 0.2], [0.4, 0.2], [0.1, 0.5], [0.3, 0.3]])
        >>> determine_optimal_number_of_clusters_kmeans(data_normalized)
        {2: 0.5, 3: 0.45, 4: 0.35, 5: 0.3}
    
    Raises:
        ValueError: If any of the columns to be used for clustering are not found in the DataFrame.

    """
    # Check if all specified variables exist in the DataFrame
    for var in columns:
        if var not in df.columns:
            raise ValueError(f"Variable '{var}' not found in the DataFrame.")

    scores = {}

    # Define the range of cluster numbers to evaluate
    range_values = range(2, 7)

    # Select the specified columns for determining cluster numbers
    df_for_clustering = df[columns]

    for i in range_values:
        kmeans = KMeans(n_clusters=i, random_state=0)  # Initialize KMeans with i clusters
        kmeans.fit(df_for_clustering)  # Fit KMeans model to the normalized data
        score = silhouette_score(df_for_clustering, kmeans.labels_)
        scores[i] = score  # Store the score in the dictionary

    return scores

def apply_kmeans_clustering(df: pd.DataFrame, columns: list, scores: dict) -> pd.DataFrame:
    """
    Applies KMeans clustering to the normalized data and adds a cluster label.

    This function finds the optimal number of clusters based on the given 
    silhouette scores, applies KMeans clustering to the normalized dataset with 
    this optimal number of clusters, and assigns the cluster labels to the data.

    Args:
        df (pd.DataFrame): The normalized dataset on which clustering will be 
        applied. It should be a DataFrame for this function to work correctly.
        columns (list): List of column names to be used for KMeans clustering.
        scores (dict): A dictionary containing the number of clusters as keys 
        and the corresponding silhouette scores as values.

    Returns:
        pd.DataFrame: The original normalized dataset with an additional column 
        'cluster' that contains the cluster labels for each data point.
    
    Raises:
        ValueError: If any of the columns to be used for clustering are not found in the DataFrame.

    """
    # Check if all specified variables exist in the DataFrame
    for var in columns:
        if var not in df.columns:
            raise ValueError(f"Variable '{var}' not found in the DataFrame.")

    # Determine the optimal number of clusters
    n_clusters_optimal = max(scores, key=scores.get)

    # Select the specified columns for DBSCAN clustering
    df_for_clustering = df[columns]

    # Apply KMeans clustering with the optimal number of clusters
    kmeans = KMeans(n_clusters=n_clusters_optimal, random_state=0)
    clusters = kmeans.fit_predict(df_for_clustering)

    # Add the cluster labels to the DataFrame
    df['cluster'] = clusters

    return df

def apply_dbscan_clustering(df: pd.DataFrame, columns: list, eps: float,
    min_samples: int) -> pd.DataFrame:
    """
    Applies DBSCAN clustering to the specified columns of the dataset and adds 
    a cluster label, returning the original DataFrame with an additional 
    'cluster' column.

    This function applies DBSCAN clustering to the specified columns of the 
    dataset with the provided `eps` and `min_samples` parameters, and assigns 
    the cluster labels to the data.

    Args:
        df (pd.DataFrame): The dataset on which clustering will be applied. It 
        should be a DataFrame with numerical features for clustering.
        columns (list): List of column names to be used for DBSCAN clustering.
        eps (float): The maximum distance between two samples for them to be 
        considered as in the same neighborhood.
        min_samples (int): The number of samples in a neighborhood for a point 
        to be considered as a core point.

    Returns:
        pd.DataFrame: The original dataset with an additional column 'cluster' 
        that contains the cluster labels for each data point.

    Raises:
        ValueError: If any of the columns to be used for clustering are not found in the DataFrame.
    
    """
    # Check if all specified variables exist in the DataFrame
    for var in columns:
        if var not in df.columns:
            raise ValueError(f"Variable '{var}' not found in the DataFrame.")

    # Select the specified columns for DBSCAN clustering
    df_for_clustering = df[columns]

    # Apply DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(df_for_clustering)

    # Add the cluster labels to the original DataFrame
    df['cluster'] = clusters

    return df

def apply_hierarchical_clustering(df: pd.DataFrame, columns: list,
    method: str = 'ward', max_d: float = 25.0) -> pd.DataFrame:
    """
    Applies hierarchical clustering to the dataset on specified columns and 
    adds a cluster label, while retaining the original DataFrame structure and 
    all initial columns.

    This function applies hierarchical agglomerative clustering to the 
    specified columns of the dataset and assigns cluster labels to the data 
    based on the specified method and max distance (`max_d`) criteria for 
    cutting the dendrogram.

    Args:
        df (pd.DataFrame): The dataset on which clustering will be applied. 
        It should be a normalized DataFrame with numerical features for clustering.
        columns (list): List of column names to be used for clustering.
        method (str): The linkage criterion determines which distance to use
        between sets of observation. The algorithm will merge the pairs of 
        cluster that minimize this criterion. 'ward', 'complete', 'average', 
        'single' are accepted. Defaults to 'ward'.
        max_d (float): The maximum distance between two clusters for them to be 
        considered as in the same cluster. This value determines the cut-off 
        for the dendrogram and thus the number of clusters. Defaults to 25.0.

    Returns:
        pd.DataFrame: The original dataset with an additional column 'cluster' 
        that contains the cluster labels for each data point.
    
    Raises:
        ValueError: If any of the columns to be used for clustering are not found in the DataFrame.

    """
    # Check if all specified variables exist in the DataFrame
    for var in columns:
        if var not in df.columns:
            raise ValueError(f"Variable '{var}' not found in the DataFrame.")

    # Perform hierarchical/agglomerative clustering on the scaled data
    z = linkage(df[columns], method=method)

    # Assign cluster labels based on the max distance criteria to the original DataFrame
    df['cluster'] = fcluster(z, max_d, criterion='distance')

    return df

def apply_pca(df: pd.DataFrame, variables: list, n_components: int) -> pd.DataFrame:
    """
    Applies PCA to reduce a given DataFrame to n dimensions over the specified 
    columns, and returns a DataFrame with the reduced dimensions and the other 
    columns unchanged.

    Args:
        df (pd.DataFrame): The original DataFrame.
        variables (list of str): The list of column names on which to apply PCA.
        n_components (int): The number of principal components to retain.

    Returns:
        pd.DataFrame: A DataFrame containing the new principal components and 
        other columns not affected by PCA.
    
    Raises:
        ValueError: If any of the columns to be used for clustering are not found in the DataFrame.

    """
    # Check if all specified variables exist in the DataFrame
    for var in variables:
        if var not in df.columns:
            raise ValueError(f"Variable '{var}' not found in the DataFrame.")

    # Separate variables for PCA and other variables
    pca_data = df[variables]
    other_data = df.drop(columns=variables)

    # Initialize and apply PCA
    pca = PCA(n_components=n_components)
    pca_transformed_data = pca.fit_transform(pca_data)

    # Create a DataFrame with PCA results
    pca_df = pd.DataFrame(data=pca_transformed_data,
                          columns=[f"PC{i+1}" for i in range(n_components)])

    # Reset index to allow concatenation
    other_data.reset_index(drop=True, inplace=True)
    pca_df.reset_index(drop=True, inplace=True)

    # Concatenate PCA components and other data
    result_df = pd.concat([other_data, pca_df], axis=1)

    return result_df
