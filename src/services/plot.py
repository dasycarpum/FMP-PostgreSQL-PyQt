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

def plot_scatterplot(df: pd.DataFrame, x_var: str, y_var: str, hue_var: str):
    """
    Generates a scatter plot from the specified columns of a DataFrame, using a 
    third column to tint the points.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be visualized.
        x_var (str): The name of the column to be used for the X axis.
        y_var (str): The name of the column to be used for the Y axis.
        hue_var (str): The name of the column to be used to tint points according to their values.

    Returns:
        None. Displays the scatter plot.

    """
    # Check existence of columns in DataFrame
    for var in [x_var, y_var, hue_var]:
        if var not in df.columns:
            raise ValueError(f"Column '{var}' does not exist in the DataFrame")

    # Scatter plot creation
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=df, x=x_var, y=y_var, hue=hue_var, alpha=0.6, palette='bright')

    # Customize graphics
    plt.title(f'Scatter Plot of {y_var} vs {x_var}', fontsize=15)
    plt.xlabel(x_var, fontsize=12)
    plt.ylabel(y_var, fontsize=12)
    plt.legend(title=hue_var, bbox_to_anchor=(1.05, 1), loc='upper left')

    # Graph display
    plt.savefig('figure/scatterplot.png')

def plot_horizontal_barchart(df: pd.DataFrame, x_var: str, y_var:str,
    title: str):
    """
    Plots a horizontal bar chart from a pandas DataFrame with annotations for each bar.

    This function generates a horizontal bar chart for the specified columns in 
    a pandas DataFrame. It ensures the specified columns exist in the 
    DataFrame, creates the chart, and annotates each bar with its value. The 
    chart is saved as a PNG file.

    Args:
        - df (pd.DataFrame): The DataFrame containing the data to plot.
        - x_var (str): The name of the column in df to be plotted on the 
        x-axis. Represents the variable values of each bar.
        - y_var (str): The name of the column in df to be plotted on the 
        y-axis. Represents the labels of each bar.
        - title (str): The title of the bar chart.
    
    Returns:
        None

    Raises:
        - ValueError: If the specified columns (x_var or y_var) do not exist in the DataFrame.

    """
    # Ensure the 'exchange' and 'count_symbols' columns exist in the DataFrame
    if x_var not in df.columns or y_var not in df.columns:
        raise ValueError(f"The DataFrame must contain the columns '{x_var}' and '{y_var}'.")

    # Create the horizontal bar chart
    plt.figure(figsize=(10, 17))
    bars = plt.barh(df[y_var], df[x_var], color='skyblue')

     # Annotate each bar with its value
    for bar_value in bars:
        width = bar_value.get_width()
        plt.text(width, bar_value.get_y() + bar_value.get_height()/2,
                 f'{width}',  # Text to display
                 va='center',  # Center vertically in the bar
                 ha='left')    # Align text to the left (inside the bar)

    plt.xlabel(x_var)
    plt.ylabel(y_var)
    plt.title(title)
    plt.tight_layout()

    # Save the graph display
    plt.savefig('figure/horizontal_barchart.png')
