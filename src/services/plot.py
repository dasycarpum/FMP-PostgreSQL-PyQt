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
from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView,
     QVBoxLayout)
from PyQt6.QtWebEngineWidgets import QWebEngineView


def plot_boxplots(df: pd.DataFrame, variables: list) -> None:
    """
    Generates boxplots for the specified variables from the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        variables (list of str): A list of strings representing the column 
        names for which boxplots are to be generated.

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

def plot_scatterplot(df: pd.DataFrame, x_var: str, y_var: str,
    hue_var: str) -> None:
    """
    Generates a scatter plot from the specified columns of a DataFrame, using a 
    third column to tint the points.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be visualized.
        x_var (str): The name of the column to be used for the X axis.
        y_var (str): The name of the column to be used for the Y axis.
        hue_var (str): The name of the column to be used to tint points according to their values.

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
    title: str) -> None:
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
    df: pd.DataFrame, x_var: str, y_var:str, title: str) -> None:
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
    title: str) -> None:
    """
    Plots a grouped bar chart from a pandas DataFrame onto a provided canvas.
    Each group (column) will have bars for 'True' and 'False' side by side.

    Args:
        - canvas (FigureCanvasQTAgg): The canvas where the bar chart will be plotted.
        - df (pd.DataFrame): The DataFrame containing the data to plot. Each 
        column represents a group, and each row (True/False) represents sub-categories.
        - title (str): The title of the bar chart.
    
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

def populate_tablewidget_with_df(table_widget: QTableWidget,
    df: pd.DataFrame)  -> None:
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
    table_widget.setVerticalHeaderLabels([str(idx) for idx in df.index])
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    # Populate the QTableWidget with the data
    for row in range(len(df.index)):
        for col in range(len(df.columns)):
            # Use iat for better performance in accessing scalar values
            item_value = df.iat[row, col]
            if isinstance(item_value, float) and item_value.is_integer():
                item_value = int(item_value)
            table_widget.setItem(row, col, QTableWidgetItem(str(item_value)))

def clear_layout(layout) -> None:
    """
    Removes all widgets from a given layout and deletes them.

    Args:
        layout (QLayout): The layout from which to remove all widgets.
    """
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())

def calculate_macd(df: pd.DataFrame, short_span: int=12, long_span: int=26,
    signal_span: int=9) -> (pd.Series, pd.Series):
    """
    Calculate the MACD and Signal line indicators
    
    """
    exp1 = df['close'].ewm(span=short_span, adjust=False).mean()
    exp2 = df['close'].ewm(span=long_span, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_span, adjust=False).mean()

    return macd, signal

def calculate_bollinger_bands(df: pd.DataFrame, window_size: int=20,
    num_std: float=2.0) -> pd.DataFrame:
    """
    Calculate Bollinger Bands for the given DataFrame.
    
    """
    df['rolling_mean'] = df['close'].rolling(window=window_size).mean()
    df['rolling_std'] = df['close'].rolling(window=window_size).std()
    df['upper_band'] = df['rolling_mean'] + (df['rolling_std'] * num_std)
    df['lower_band'] = df['rolling_mean'] - (df['rolling_std'] * num_std)

    return df

def add_bollinger_bands_to_chart(fig: go.Figure, df: pd.DataFrame,
    row: int, col: int) -> None:
    """
    Add Bollinger Bands to the Plotly figure.
    
    """
    # Add the Upper Bollinger Band to the chart
    fig.add_trace(go.Scatter(x=df.index, y=df['upper_band'],
                             line=dict(width=1),
                             name='Upper Band',
                             line_color='rgba(68, 68, 68, 0.75)',
                             showlegend=False),
                  row=row, col=col)

    # Add the Lower Bollinger Band to the chart
    fig.add_trace(go.Scatter(x=df.index, y=df['lower_band'],
                             line=dict(width=1),
                             name='Lower Band',
                             fill='tonexty',
                             fillcolor='rgba(68, 68, 68, 0.1)',
                             line_color='rgba(68, 68, 68, 0.75)',
                             showlegend=False),
                  row=row, col=col)

def add_moving_average_to_chart(fig: go.Figure, df: pd.DataFrame, sma: str,
    row: int, col: int) -> None:
    """
    Add simple moving average to the Plotly figure.
    
    """
    if sma == 'SMA_1':
        color = 'rgba(68, 68, 68, 0.75)'
    else:
        color = 'white'

    fig.add_trace(go.Scatter(x=df.index, y=df[sma],
                             mode='lines',
                             line=dict(color=color, width=2),
                             showlegend=False),
                  row=row, col=col)

def draw_a_plotly_candlestick_chart(vertical_layout: QVBoxLayout,
    df: pd.DataFrame, setting: dict):
    """
    Draws a candlestick chart in a PyQt application using Plotly and displays 
    it within a QWebEngineView.

    This function generates a candlestick chart, along with additional 
    technical indicators, for financial data provided in a DataFrame. The chart 
    is then rendered to HTML and displayed using a QWebEngineView that is added 
    to the given QVBoxLayout.

    Args:
        vertical_layout (QVBoxLayout): The layout where the chart will be displayed.
        df (pd.DataFrame): The data frame containing the stock data with at 
        least the following columns: ['open', 'high', 'low', 'close', 'volume'].
        setting (dict): Configuration settings for the chart, which may include:
            - 'log_scale' (bool): If True, apply logarithmic scale to the y-axis.
            - 'bollinger' (bool): If True, add Bollinger Bands to the chart.
            - 'window_size' (int): Window size for calculating Bollinger Bands.
            - 'num_std' (int): Number of standard deviations for Bollinger width.
            - 'sma' (bool): If True, add Simple Moving Averages to the chart.
            - 'sma_1' (int): Window size for the first SMA.
            - 'sma_2' (int): Window size for the second SMA (only applied if greater than 0).
            - 'interval' (str): Data interval, affects x-axis formatting.

    Raises:
        ValueError: If 'df' is missing any of the required columns.

    """
    # First clear the layout
    clear_layout(vertical_layout)

    # Check if all required columns are present in the DataFrame
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"DataFrame missing one of the required columns: {required_columns}")

    # Calculate MACD and Signal Line
    macd, signal = calculate_macd(df)

    # Create a subplot figure with 2 rows
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_heights=[0.6, 0.15, 0.25])

    # Add the Candlestick chart
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 increasing=dict(line=dict(color='white', width=1)),
                                 decreasing=dict(line=dict(color='black', width=1)),
                                 showlegend=False),
                  row=1, col=1)

    # Add Volume Bar Chart
    fig.add_trace(go.Bar(x=df.index,
                         y=df['volume'],
                         marker_color='lightgrey',
                         showlegend=False),
                  row=2, col=1)

    # Add MACD and Signal Line
    fig.add_trace(go.Scatter(x=df.index, y=macd, mode='lines',
                            name='MACD', line=dict(color='black'),
                            showlegend=False),
                  row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=signal, mode='lines',
                            name='Signal Line', line=dict(color='white'), showlegend=False),
                  row=3, col=1)

    # Option : logarithmic scale
    if setting['log_scale']:
        fig.update_yaxes(type="log", row=1, col=1)

    # Technical indicator : Bollinger bands
    if setting['bollinger']:
        # Calculate Bollinger bands
        df = calculate_bollinger_bands(
            df, window_size=setting['window_size'], num_std=setting['num_std'])

        # Add Bollinger Bands
        add_bollinger_bands_to_chart(fig, df, 1, 1)

    # Technical indicator : simple moving average
    if setting['sma']:
        # Calculate SMA
        df['SMA_1'] = df['close'].rolling(window=setting['sma_1']).mean()
        # Add SMA 1
        add_moving_average_to_chart(fig, df, 'SMA_1', 1, 1)
        if setting['sma_2'] > 0:
            df['SMA_2'] = df['close'].rolling(
                window=setting['sma_2']).mean()
            # Add SMA 2
            add_moving_average_to_chart(fig, df, 'SMA_2', 1, 1)

    # Update layout
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        yaxis_title="Price",
        yaxis2_title="Volume",
        yaxis3_title="MACD",
        paper_bgcolor='lightgrey',
        plot_bgcolor='grey',
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
        yaxis2=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
        yaxis3=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    )

    # Update x axes
    if setting['interval'] == 'daily':
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

    # Generate HTML representation of the Plotly figure
    plot_html = plot(fig, output_type='div', include_plotlyjs='cdn')

    # Create a QWebEngineView to display the HTML
    webview = QWebEngineView()
    webview.setHtml(plot_html)

    # Add the QWebEngineView to the QVBoxLayout
    vertical_layout.addWidget(webview)

def plot_vertical_barchart(canvas: FigureCanvasQTAgg, df: pd.DataFrame,
    x_var: str, y_var: str, title: str) -> None:
    """
    Plots a vertical bar chart on a specified matplotlib canvas with annotations.

    This function takes a pandas DataFrame and plots a vertical bar chart on a 
    given FigureCanvasQTAgg. Each bar in the chart is annotated with its value 
    above the bar. The plot is drawn on a single subplot within the canvas.

    Args:
        canvas (FigureCanvasQTAgg): The canvas on which the bar chart will be 
        drawn. This should be an instance of FigureCanvasQTAgg from the 
        matplotlib backend for Qt.
        df (pd.DataFrame): DataFrame containing the data to plot. Must include 
        specified columns for x-axis and y-axis values.
        x_var (str): The name of the column in DataFrame to be used as the 
        x-axis values. Typically, this is a categorical variable.
        y_var (str): The name of the column in DataFrame to be used for the 
        y-axis values. This is usually a numerical variable representing the 
        height of the bars.
        title (str): The title of the plot.
        
    Raises:
        ValueError: If the specified x_var or y_var columns do not exist in the DataFrame.

    """
    # Ensure the specified columns exist in the DataFrame
    if x_var not in df.columns or y_var not in df.columns:
        raise ValueError(f"The DataFrame must contain the columns '{x_var}' and '{y_var}'.")

    # Clear the existing figure to prepare for a new plot
    canvas.figure.clf()
    ax = canvas.figure.add_subplot(111)  # Create an axes instance in the figure

    # Create the vertical bar chart directly on the provided axes
    bars = ax.bar(df[x_var], df[y_var], color='grey')

    # Annotate each bar with its value
    for bar_ in bars:
        height = bar_.get_height()
        ax.text(bar_.get_x() + bar_.get_width() / 2, height, f'{height:.1f}',
                va='bottom', ha='center', fontsize=6
            )  # Vertically align bottom which is actually above the bar

    ax.set_xlabel(x_var)
    ax.set_ylabel(y_var)
    ax.set_title(title)

    canvas.figure.tight_layout()  # Adjust layout to prevent overlap
    canvas.draw()  # Refresh the canvas with the new plot
