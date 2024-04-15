#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-15

@author: Roland VANDE MAELE

@abstract: this file contains functions for generating various plots.

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import seaborn as sns
import squarify
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView


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

def plot_distributions_png(df: pd.DataFrame, variables: list,
    title: str = "") -> None:
    """
    Generates histograms for the specified variables from the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        variables (list of str): A list of strings representing the column 
        names for which distributions are to be generated.
        title (str) : : The title of the histogram chart.

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

    # Set a single title for the entire figure
    fig.suptitle(title)

    # Adjust layout to make room for the figure title and ensure plots are not overlapping
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Save the figure to a file
    plt.savefig('figure/distributions.png')

def plot_distributions_widget(canvas: FigureCanvasQTAgg, df: pd.DataFrame,
    variables: list, title: str = "") -> None:
    """
    Generates histograms for the specified variables from the given DataFrame 
    on the provided canvas.

    Args:
        canvas (FigureCanvasQTAgg): The canvas where the histograms will be plotted.
        df (pandas.DataFrame): The DataFrame containing the data.
        variables (list of str): A list of strings representing the column 
        names for which distributions are to be generated.
        title (str): The title of the histogram chart.

    Returns:
        None. Plots the distributions of the specified variables on the canvas.

    Raises:
        ValueError: If any of the specified variables are not found in the DataFrame.
    """
    # Clear the existing figure to prepare for a new plot
    canvas.figure.clf()

    # Number of variables
    n_vars = len(variables)

    # Check if all specified variables exist in the DataFrame
    for var in variables:
        if var not in df.columns:
            raise ValueError(f"Variable '{var}' not found in the DataFrame.")

    # Create a subplot for each variable
    axes = canvas.figure.subplots(1, n_vars, squeeze=False).flatten()

    # Display distributions for each variable
    for i, var in enumerate(variables):
        data = df[var].dropna()
        axes[i].hist(data, bins=30, alpha=0.7, label=var, color='skyblue', edgecolor='black')
        axes[i].set_ylabel("frequency")
        axes[i].set_xlabel(var)

    # Set a single title for the entire figure if there's a title provided
    if title:
        canvas.figure.suptitle(title)

    # Adjust layout to make room for the figure title and ensure plots are not overlapping
    canvas.figure.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Refresh the canvas with the new plot
    canvas.draw()

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

def plot_horizontal_barchart_png(df: pd.DataFrame, x_var: str, y_var:str,
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

def plot_horizontal_barchart_widget(canvas: FigureCanvasQTAgg,
    df: pd.DataFrame, x_var: str, y_var:str, title: str):
    """
    Plots a horizontal bar chart from a pandas DataFrame with annotations for 
    each bar onto a provided canvas.

    This function generates a horizontal bar chart for the specified columns in 
    a pandas DataFrame directly on the given canvas. It ensures the specified 
    columns exist in the DataFrame, creates the chart on the canvas, and 
    annotates each bar with its value.

    Args:
        - canvas (FigureCanvasQTAgg): The canvas where the bar chart will be plotted.
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
    # Ensure the specified columns exist in the DataFrame
    if x_var not in df.columns or y_var not in df.columns:
        raise ValueError(f"The DataFrame must contain the columns '{x_var}' and '{y_var}'.")

    # Clear the existing figure to prepare for a new plot
    canvas.figure.clf()
    ax = canvas.figure.add_subplot(111)  # Create an axes instance in the figure

    # Sort DataFrame based on x_var in descending order
    df_sorted = df.sort_values(by=x_var, ascending=False)

    # Limit and group data
    if len(df_sorted) > 25:
        top_df = df_sorted.head(24)  # Get the top 19 entries
        # Sum other entries and add as 'Miscellaneous'
        misc_sum = df_sorted[x_var][24:].sum()
        misc_row = pd.DataFrame({y_var: ['Miscellaneous'], x_var: [misc_sum]})
        df_final = pd.concat([top_df, misc_row], ignore_index=True)
    else:
        df_final = df_sorted

    # Create the horizontal bar chart directly on the provided axes
    bars = ax.barh(df_final[y_var], df_final[x_var], color='skyblue')

    # Annotate each bar with its value
    for bar_ in bars:
        width = bar_.get_width()
        ax.text(width, bar_.get_y() + bar_.get_height() / 2, f'{width:.0f}',
                va='center', ha='left')  # Align text to the left (inside the bar)

    ax.set_xlabel(x_var)
    ax.set_ylabel(y_var)
    ax.set_title(title)

    canvas.figure.tight_layout()  # Adjust layout to prevent overlap
    canvas.draw()  # Refresh the canvas with the new plot

def plot_treemap_png(df: pd.DataFrame, title: str) -> None:
    """
    Generates and saves a treemap visualization from a pandas DataFrame.

    The function assumes the DataFrame has two specific columns: the second 
    column for counts (numeric values) and the first column for labels (text 
    values). The treemap plot visualizes the proportion of counts associated 
    with each label. The plot is saved as a PNG file in a directory named 
    'figure'.

    Args:
        - df (pd.DataFrame): A DataFrame with two columns, where one contains 
        numeric values (counts) and the other contains corresponding labels.
        - title (str): The title of the treemap plot.

    Returns:
        None

    """
    # Ensure the DataFrame has exactly two columns
    if df.shape[1] != 2:
        raise ValueError("DataFrame must have exactly two columns.")

    # Assuming the first column contains counts and the second contains labels
    counts = df.iloc[:, 1].tolist()
    labels = df.iloc[:, 0].tolist()

    # Concatenate labels and counts
    labels_with_counts = [f"{label}: {count}" for label, count in zip(labels, counts)]

    # Choosing a color palette with Matplotlib
    palette = plt.cm.viridis # pylint: disable=no-member
    color = [palette(i / len(labels)) for i in range(len(labels))]

    plt.figure(figsize=(10, 8))
    squarify.plot(sizes=counts, label=labels_with_counts,
                  color=color, alpha=0.7)
    plt.title(title)
    plt.axis('off')  # Removes the axes for a cleaner look

    # Save the graph display
    plt.savefig('figure/treemap.png')

def plot_treemap_widget(canvas: FigureCanvasQTAgg, df: pd.DataFrame,
    title: str) -> None:
    """
    Generates a treemap visualization on a provided canvas from a pandas DataFrame.

    The function assumes the DataFrame has two specific columns: the second
    column for counts (numeric values) and the first column for labels (text
    values). The treemap plot visualizes the proportion of counts associated
    with each label on the specified canvas.

    Args:
        - canvas (FigureCanvasQTAgg): The canvas where the treemap will be plotted.
        - df (pd.DataFrame): A DataFrame with two columns, where one contains
          numeric values (counts) and the other contains corresponding labels.
        - title (str): The title of the treemap plot.

    Returns:
        None
    """
    # Ensure the DataFrame has exactly two columns
    if df.shape[1] != 2:
        raise ValueError("DataFrame must have exactly two columns.")

    # Assuming the first column contains labels and the second contains counts
    labels = df.iloc[:, 0].tolist()
    counts = df.iloc[:, 1].tolist()

    # Concatenate labels and counts
    labels_with_counts = [f"{label}: {count}" for label, count in zip(labels, counts)]

    # Choosing a color palette with Matplotlib
    palette = plt.cm.viridis # pylint: disable=no-member
    colors = [palette(i / len(labels)) for i in range(len(labels))]

    # Clear the existing figure to prepare for a new plot
    canvas.figure.clf()

    ax = canvas.figure.add_subplot(111)  # Create an axes instance in the figure

    # Plotting the treemap
    squarify.plot(sizes=counts, label=labels_with_counts, color=colors, alpha=0.7, ax=ax)

    ax.set_title(title)
    ax.axis('off')  # Removes the axes for a cleaner look

    # Refresh the canvas with the new plot
    canvas.draw()

def plot_grouped_barchart_widget(canvas: FigureCanvasQTAgg, df: pd.DataFrame,
    title: str):
    """
    Plots a grouped bar chart from a pandas DataFrame onto a provided canvas.
    Each group (column) will have bars for 'True' and 'False' side by side.

    Args:
        - canvas (FigureCanvasQTAgg): The canvas where the bar chart will be plotted.
        - df (pd.DataFrame): The DataFrame containing the data to plot. Each 
        column represents a group, and each row (True/False) represents sub-categories.
        - title (str): The title of the bar chart.
    
    Returns:
        None
    """
    # Clear any existing plot on the canvas
    canvas.figure.clf()

    # Create an axes instance in the figure
    ax = canvas.figure.add_subplot(111)

    # Number of groups and categories
    n_groups = len(df.columns)
    n_categories = len(df.index)  # True and False

    # Width of each bar
    bar_width = 0.35

    # Create an index for each tick position
    indices = np.arange(n_groups)

    # Plot each category
    for i, category in enumerate(df.index):
        # Offset index depending on the category ('True' or 'False')
        offset = (i - n_categories / 2) * bar_width + bar_width / 2
        values = df.loc[category]  # Extract row values for True or False
        bars = ax.bar(indices + offset, values, width=bar_width, label=str(category))

        # Annotate each bar with its value
        for bar_ in bars:
            height = bar_.get_height()
            ax.annotate(f"{format(height)}",
                        xy=(bar_.get_x() + bar_.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    # Set chart titles and labels
    ax.set_xlabel('Categories')
    ax.set_ylabel('Counts')
    ax.set_title(title)
    ax.set_xticks(indices)
    ax.set_xticklabels(df.columns)
    ax.legend(title="Boolean Value")

    # Adjust layout and refresh the canvas
    canvas.figure.tight_layout()
    canvas.draw()

def populate_tablewidget_with_df(table_widget: QTableWidget, df: pd.DataFrame):
    """
    Populates a QTableWidget with data from a Pandas DataFrame using the 
    DataFrame's column indices as headers. It ensures all data displayed are 
    appropriately formatted as strings and checks if numeric values can be 
    represented as integers to avoid displaying unnecessary decimal points.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to display. 
        Assumes that the DataFrame has appropriately named columns that will be 
        used as headers for the QTableWidget.
        table_widget (QTableWidget): The QTableWidget instance to be populated 
        with data from the DataFrame.

    Returns:
        None: This function does not return anything but directly modifies the
            QTableWidget passed as an argument.

    Raises:
        This function currently does not raise exceptions but will fail if df 
        or table_widget are not correctly specified or if the df contains data 
        types that cannot be directly converted to strings.

    """
    # Set the number of columns and rows in the QTableWidget
    table_widget.setColumnCount(len(df.columns))
    table_widget.setRowCount(len(df.index))

    # Set the headers in the QTableWidget using the column names of the DataFrame
    table_widget.setHorizontalHeaderLabels([str(col) for col in df.columns])
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    # Populate the QTableWidget with the data
    for row in range(len(df.index)):
        for col in range(len(df.columns)):
            # Use iat for better performance in accessing scalar values
            item_value = df.iat[row, col]
            if isinstance(item_value, float) and item_value.is_integer():
                item_value = int(item_value)
            table_widget.setItem(row, col, QTableWidgetItem(str(item_value)))
    