#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-15

@author: Roland VANDE MAELE

@abstract: this file contains functions for generating various plots.

"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_boxplots(df: pd.DataFrame, variables: list) -> None:
    """
    Generates boxplots for the specified variables from the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        variables (list of str): A list of strings representing the column 
        names for which boxplots are to be generated.

    Returns:
        None. Displays the boxplots of the specified variables.

    Raises:
        ValueError: If any of the specified variables are not found in the DataFrame.

    Examples:
        >>> plot_boxplots(df, ['beta', 'vol_avg', 'mkt_cap'])
        This will display boxplots for the 'beta', 'vol_avg', and 'mkt_cap' 
        columns from the DataFrame df.

    """
    # Check if all specified variables exist in the DataFrame
    for var in variables:
        if var not in df.columns:
            raise ValueError(f"Variable '{var}' not found in the DataFrame.")

    # Number of variables
    n_vars = len(variables)

    # Create figure and axes for boxplots
    fig, axes = plt.subplots(1, n_vars, figsize=(n_vars * 5, 4), squeeze=False) # pylint: disable=unused-variable
    axes = axes.flatten()  # Flatten axis table if necessary

    # Display boxplots for each variable
    for i, var in enumerate(variables):
        axes[i].boxplot(df[var].dropna(), patch_artist=True)
        axes[i].set_title(var)

    # Automatically adjusts subplots to fit within the figure area
    plt.tight_layout()

    plt.savefig('figure/boxplots.png')


def plot_distributions(df: pd.DataFrame, variables: list) -> None:
    """
    Generates histograms for the specified variables from the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        variables (list of str): A list of strings representing the column 
        names for which distributions are to be generated.

    Returns:
        None. Displays the distributions of the specified variables.

    Raises:
        ValueError: If any of the specified variables are not found in the DataFrame.

    """
    # Check if all specified variables exist in the DataFrame
    for var in variables:
        if var not in df.columns:
            raise ValueError(f"Variable '{var}' not found in the DataFrame.")

    # Number of variables
    n_vars = len(variables)

    # Create figure and axes for boxplots
    fig, axes = plt.subplots(1, n_vars, figsize=(n_vars * 5, 4), squeeze=False) # pylint: disable=unused-variable
    axes = axes.flatten()  # Flatten axis table if necessary

    # Display distributions for each variable
    for i, var in enumerate(variables):
        data = df[var].dropna()
        axes[i].hist(data, bins=30, alpha=0.7, label=var, color='skyblue', edgecolor='black')
        axes[i].set_title(var)

    # Automatically adjusts subplots to fit within the figure area
    plt.tight_layout()

    plt.savefig('figure/distributions.png')

def display_correlation_matrix(df: pd.DataFrame, variables: list) -> None:
    """
    Displays the correlation matrix between the specified columns of a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        variables (list of str): A list of strings representing the names of 
        the columns for which the correlation matrix is calculated.

    Returns:
        None. Displays the correlation matrix.

    Raises:
        ValueError: If one of the specified columns is not found in the DataFrame.

    """
    # Check if all specified variables exist in the DataFrame
    missing_columns = [column for column in variables if column not in df.columns]
    if missing_columns:
        raise ValueError(
            f"The following columns were not found in the DataFrame: {missing_columns}")

    # Calculate correlation matrix for specified columns
    correlation_matrix = df[variables].corr()

    # Display correlation matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm",
        square=True, cbar_kws={"shrink": .75})
    plt.title("Correlation matrix")

    plt.savefig('figure/correlation_matrix.png')
