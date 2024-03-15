#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-15

@author: Roland VANDE MAELE

@abstract: this file contains functions for generating various plots.

"""

import matplotlib.pyplot as plt


def plot_boxplots(df, variables):
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
