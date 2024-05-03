#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-09

@author: Roland VANDE MAELE

@abstract: this ORM (Object-Relational Mapping) model represents the FMP stock
tables in the PostgreSQL database.

"""

from sqlalchemy import (Column, Integer, BigInteger, String, Float, Boolean,
                        Date, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from src.models.base import Base


class StockSymbol(Base):
    """
    Represents a stock symbol entity within the database.
    
    Attributes:
        id (int): The unique identifier for the stock symbol. This is the 
        primary key in the database.
        symbol (str): The ticker symbol of the stock, e.g., 'AAPL' for Apple 
        Inc. This field is required, unique and cannot be null.
        exchange (str): The name of the stock exchange where the stock is 
        traded, e.g., 'NASDAQ'.
        exchangeShortName (str): A shorter or abbreviated name for the 
        exchange, e.g., 'NYSE' for New York Stock Exchange.
        price (float): The current price of the stock. This field can store 
        floating-point numbers to accommodate stock prices with cents.
        name (str): The official name of the company that the stock symbol 
        represents. This field is required and cannot be null.
        type_ (str): Stock, ETF or Trust
        
    The `__tablename__` attribute specifies the name of the database table to 
    which this class is mapped.

    FMP comments: 
        Find symbols for traded and non-traded stocks with our Symbol List. 
        This comprehensive list includes over 25,000 stocks, making it the 
        perfect resource for investors and traders of all levels.

    """
    __tablename__ = 'stocksymbol'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False)
    exchange = Column(String(35))
    exchangeshortname = Column(String(10))
    price = Column(Float)
    name = Column(String(180))
    type_ = Column(String(5))

    company = relationship("CompanyProfile", back_populates="stocksymbol")
    daily_charts = relationship("DailyChartEOD", back_populates="stocksymbol")
    dividends = relationship("HistoricalDividend", back_populates="stocksymbol")
    keymetrics = relationship("HistoricalKeyMetrics",
                               back_populates="stocksymbol")
    stoxx600 = relationship("STOXXEurope600", back_populates='stocksymbol')


class CompanyProfile(Base):
    """
    Represents the profile of a company associated with a stock symbol.

    Attributes:
        id (int): Primary key.
        stock_id (int): Foreign key linking to the StockSymbol table, ensuring
         a one-to-one relationship.
        beta (Float): measure of an asset's volatility relative to a reference 
         market or index.
        vol_avg (BigInteger): volume average.
        mkt_cap (BigInteger): market capitalization.
        currency (str): The currency in which the company operates.
        cik (str): The Central Index Key (CIK) assigned by the SEC.
        isin (str): The International Securities Identification Number.
        cusip (str): The Committee on Uniform Securities Identification Procedures number.
        industry (str): The industry sector the company belongs to.
        website (str): The official website of the company.
        description (str): A brief description of the company's operations.
        sector (str): The sector of the economy to which the company contributes.
        country (str): The country where the company is headquartered.
        image (str): A URL to an image or logo of the company.
        ipo_date (datetime.date): The initial public offering date for the company's stock.
        is_etf (bool): Indicates whether the company is an ETF (Exchange-Traded Fund).
        is_actively_trading (bool): Indicates whether the company's stock is
         currently being actively traded.
        is_adr (bool): Indicates whether the company is an ADR (American Depository Receipt).
        isf_und (bool): Indicates whether the company is a fund.

    The CompanyProfile model is designed to hold detailed information about 
    companies associated with stock symbols. It has a one-to-one relationship 
    with the StockSymbol model, allowing for easy access to stock-related data 
    alongside company profiles.

    """
    __tablename__ = 'companyprofile'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey(StockSymbol.id), unique=True, nullable=False)
    beta = Column(Float)
    vol_avg = Column(BigInteger)
    mkt_cap = Column(BigInteger)
    currency = Column(String(3))
    cik = Column(String(10))
    isin = Column(String(12))
    cusip = Column(String(9))
    industry = Column(String(60))
    website = Column(String(255))
    description = Column(String)
    sector = Column(String(60))
    country = Column(String(5))
    image = Column(String(255))
    ipo_date = Column(Date)
    is_etf = Column(Boolean)
    is_actively_trading = Column(Boolean)
    is_adr = Column(Boolean)
    is_fund = Column(Boolean)

    stocksymbol = relationship("StockSymbol", back_populates="company")

class DailyChartEOD(Base):
    """
    Represents daily quote data for a stock symbol.

    Each instance of this class corresponds to a single daily quotation record
    for a specific stock symbol, including information such as opening price
    opening price, closing price, volume, etc.

    Attributes:
        id (BigInteger): Unique record identifier.
        stock_id (Integer): Foreign key to the associated stock symbol.
        date (Date): Date of quotation.
        open (Float): Quotation opening price.
        high (Float): Highest price reached during the day.
        low (Float): Lowest price reached during the day.
        close (Float): Quotation closing price.
        adjclose (Float): Adjusted closing price, taking into account corporate
            such as splits.
        volume (BigInteger): Total volume of shares traded during the day.
        unadjusted_volume (BigInteger): Total volume of shares traded without adjustments.
        change (Float): Change in price from previous day.
        change_percent (Float): Percentage change in price from previous day.
        vwap (Float): Volume-weighted average price.
    
    Relationships:
        stocksymbol (relationship): SQLAlchemy `relationship` to the 
        corresponding `StockSymbol` instance, providing access to the stock 
        symbol associated with this quotation.
    
    Constraints:
        __table_args__: A unique constraint (`_char_stockid_date_uc`) ensuring 
        that there can be only one quotation entry per stock per day, combining 
        `stock_id` and `date`.

    """
    __tablename__ = 'dailychart'

    id = Column(BigInteger, primary_key=True)
    stock_id = Column(Integer, ForeignKey(StockSymbol.id), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(BigInteger)
    unadjusted_volume = Column(BigInteger)
    change = Column(Float)
    change_percent = Column(Float)
    vwap = Column(Float)
    dividend_signature = Column(String(255))

    stocksymbol = relationship("StockSymbol", back_populates="daily_charts")

    # Add a unique constraint for stock_id and date
    __table_args__ = (UniqueConstraint('stock_id', 'date',
                      name='_chart_stockid_date_uc'),)

class HistoricalDividend(Base):
    """
    Represents historical dividend data for a given stock.

    This class is mapped to a table in a database that stores the dividend 
    information for stocks over time. It includes both adjusted and unadjusted 
    dividend values, as well as the dates relevant to dividend payments.

    Attributes:
        id (int): Unique identifier for each record.
        stock_id (int): The ID of the stock, which is a foreign key that 
        references the StockSymbol table.
        date (datetime.date): The date when the dividend was announced.
        adj_dividend (float, optional): The adjusted dividend value, which 
        accounts for any corporate actions that may affect the dividend amount. 
        Defaults to None.
        dividend (float, optional): The original, unadjusted dividend value. 
        Defaults to None.
        payment_date (datetime.date, optional): The date when the dividend is 
        actually paid to shareholders. Defaults to None.

    Relationships:
        stocksymbol (relationship): SQLAlchemy `relationship` to the 
        corresponding `StockSymbol` instance, providing access to the stock 
        symbol associated with this dividend.

    Constraints:
        __table_args__ : A unique constraint (_dividend_stockid_date_uc) is 
        applied to the `stock_id` and `date` fields to ensure there are no 
        duplicate entries for the same stock on the same date.

    """
    __tablename__ = 'dividend'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey(StockSymbol.id), nullable=False)
    date = Column(Date, nullable=False)
    adj_dividend = Column(Float)
    dividend = Column(Float)
    payment_date = Column(Date)

    stocksymbol = relationship("StockSymbol", back_populates="dividends")

    # Add a unique constraint for stock_id and date
    __table_args__ = (UniqueConstraint('stock_id', 'date',
                      name='_dividend_stockid_date_uc'),)

class HistoricalKeyMetrics(Base):
    """
    A database model class that represents the historical key financial metrics for a stock.

    Attributes:
        __tablename__ (str): The name of the table in the database, set to 'keymetrics'.
        id (Column): The primary key, an integer ID uniquely identifying each entry.
        stock_id (Column): An integer foreign key linking to the StockSymbol table, cannot be null.
        date (Column): The date for the metrics, cannot be null.
        calendar_year (Column): The calendar year as a string in YYYY format, cannot be null.
        period (Column): The fiscal period of the report as a string (e.g., 
        'Q1', 'Q2', 'H1'), cannot be null.
        revenue_per_share (Column): Revenue per share, a floating-point number.
        net_income_per_share (Column): Net income per share, a floating-point number.
        operating_cash_flow_per_share (Column): Operating cash flow per share, 
        a floating-point number.
        free_cash_flow_per_share (Column): Free cash flow per share, a floating-point number.
        cash_per_share (Column): Cash per share, a floating-point number.
        book_value_per_share (Column): Book value per share, a floating-point number.
        tangible_book_value_per_share (Column): Tangible book value per share, 
        a floating-point number.
        shareholders_equity_per_share (Column): Shareholder's equity per share, 
        a floating-point number.
        interest_debt_per_share (Column): Interest debt per share, a floating-point number.
        market_cap (Column): Market capitalization, a big integer.
        enterprise_value (Column): Enterprise value, a big integer.
        pe_ratio (Column): Price to earnings ratio, a floating-point number.
        price_to_sales_ratio (Column): Price to sales ratio, a floating-point number.
        pocf_ratio (Column): Price to operating cash flow ratio, a floating-point number.
        pfcf_ratio (Column): Price to free cash flow ratio, a floating-point number.
        pb_ratio (Column): Price to book ratio, a floating-point number.
        ptb_ratio (Column): Price to tangible book ratio, a floating-point number.
        ev_to_sales (Column): Enterprise value to sales ratio, a floating-point number.
        enterprise_value_over_ebitda (Column): Enterprise value over EBITDA 
        ratio, a floating-point number.
        ev_to_operating_cash_flow (Column): EV to operating cash flow ratio, a 
        floating-point number.
        ev_to_free_cash_flow (Column): EV to free cash flow ratio, a floating-point number.
        earnings_yield (Column): Earnings yield, a floating-point number.
        free_cash_flow_yield (Column): Free cash flow yield, a floating-point number.
        debt_to_equity (Column): Debt to equity ratio, a floating-point number.
        debt_to_assets (Column): Debt to assets ratio, a floating-point number.
        net_debt_to_ebitda (Column): Net debt to EBITDA ratio, a floating-point number.
        current_ratio (Column): Current ratio, a floating-point number.
        interest_coverage (Column): Interest coverage ratio, a floating-point number.
        income_quality (Column): Income quality, a floating-point number.
        dividend_yield (Column): Dividend yield, a floating-point number.
        payout_ratio (Column): Payout ratio, a floating-point number.
        sales_general_and_administrative_to_revenue (Column): SG&A to revenue 
        ratio, a floating-point number.
        research_and_development_to_revenue (Column): R&D to revenue ratio, a floating-point number.
        intangibles_to_total_assets (Column): Intangibles to total assets 
        ratio, a floating-point number.
        capex_to_operating_cash_flow (Column): CapEx to operating cash flow 
        ratio, a floating-point number.
        capex_to_revenue (Column): CapEx to revenue ratio, a floating-point number.
        capex_to_depreciation (Column): CapEx to depreciation ratio, a floating-point number.
        stock_based_compensation_to_revenue (Column): Stock-based compensation 
        to revenue ratio, a floating-point number.
        graham_number (Column): Graham number, a floating-point number.
        roic (Column): Return on invested capital, a floating-point number.
        return_on_tangible_assets (Column): Return on tangible assets, a floating-point number.
        graham_net_net (Column): Graham net-net, a floating-point number.
        working_capital (Column): Working capital, a big integer.
        tangible_asset_value (Column): Tangible asset value, a big integer.
        net_current_asset_value (Column): Net current asset value, a big integer.
        invested_capital (Column): Invested capital, a floating-point number.
        average_receivables (Column): Average receivables, a big integer.
        average_payables (Column): Average payables, a big integer.
        average_inventory (Column): Average inventory, a big integer.
        days_sales_outstanding (Column): Days sales outstanding, a floating-point number.
        days_payables_outstanding (Column): Days payables outstanding, a floating-point number.
        days_of_inventory_on_hand (Column): Days of inventory on hand, a floating-point number.
        receivables_turnover (Column): Receivables turnover, a floating-point number.
        payables_turnover (Column): Payables turnover, a floating-point number.
        inventory_turnover (Column): Inventory turnover, a floating-point number.
        roe (Column): Return on equity, a floating-point number.
        capex_per_share (Column): CapEx per share, a floating-point number.
        
    Relationships:
        stocksymbol (relationship): SQLAlchemy `relationship` to the 
        corresponding `StockSymbol` instance, providing access to the stock 
        symbol associated with the key metrics.

    Constraints:
        __table_args__ : A unique constraint is applied to the `stock_id`, `date` and `period` fields to ensure there are no duplicate entries for the same stock on the same date.

    """
    __tablename__ = 'keymetrics'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey(StockSymbol.id), nullable=False)
    date = Column(Date, nullable=False)
    calendar_year = Column(String(4), nullable=False)
    period = Column(String(6), nullable=False)
    revenue_per_share = Column(Float)
    net_income_per_share = Column(Float)
    operating_cash_flow_per_share = Column(Float)
    free_cash_flow_per_share = Column(Float)
    cash_per_share = Column(Float)
    book_value_per_share = Column(Float)
    tangible_book_value_per_share = Column(Float)
    shareholders_equity_per_share = Column(Float)
    interest_debt_per_share = Column(Float)
    market_cap = Column(BigInteger)
    enterprise_value = Column(BigInteger)
    pe_ratio = Column(Float)
    price_to_sales_ratio = Column(Float)
    pocf_ratio = Column(Float)
    pfcf_ratio = Column(Float)
    pb_ratio = Column(Float)
    ptb_ratio = Column(Float)
    ev_to_sales = Column(Float)
    enterprise_value_over_ebitda = Column(Float)
    ev_to_operating_cash_flow = Column(Float)
    ev_to_free_cash_flow = Column(Float)
    earnings_yield = Column(Float)
    free_cash_flow_yield = Column(Float)
    debt_to_equity = Column(Float)
    debt_to_assets = Column(Float)
    net_debt_to_ebitda = Column(Float)
    current_ratio = Column(Float)
    interest_coverage = Column(Float)
    income_quality = Column(Float)
    dividend_yield = Column(Float)
    payout_ratio = Column(Float)
    sales_general_and_administrative_to_revenue = Column(Float)
    research_and_development_to_revenue = Column(Float)
    intangibles_to_total_assets = Column(Float)
    capex_to_operating_cash_flow = Column(Float)
    capex_to_revenue = Column(Float)
    capex_to_depreciation = Column(Float)
    stock_based_compensation_to_revenue = Column(Float)
    graham_number = Column(Float)
    roic = Column(Float)
    return_on_tangible_assets = Column(Float)
    graham_net_net = Column(Float)
    working_capital = Column(BigInteger)
    tangible_asset_value = Column(BigInteger)
    net_current_asset_value = Column(BigInteger)
    invested_capital = Column(Float)
    average_receivables = Column(BigInteger)
    average_payables = Column(BigInteger)
    average_inventory = Column(BigInteger)
    days_sales_outstanding = Column(Float)
    days_payables_outstanding = Column(Float)
    days_of_inventory_on_hand = Column(Float)
    receivables_turnover = Column(Float)
    payables_turnover = Column(Float)
    inventory_turnover = Column(Float)
    roe = Column(Float)
    capex_per_share = Column(Float)

    stocksymbol = relationship("StockSymbol", back_populates="keymetrics")

    # Add a unique constraint for stock_id, date and period
    __table_args__ = (UniqueConstraint('stock_id', 'date', 'period',
                      name='_keymetrics_stockid_date_period_uc'),)

class STOXXEurope600(Base):
    """Represents the STOXX Europe 600 index within a database, detailing each stock's involvement.

    The STOXX Europe 600 index, which includes 600 different stocks across 
    Europe, aims to provide a broad yet effective representation of the 
    European stock market. This class links each stock to its performance and
    metadata within the index.

    Attributes:
        __tablename__ (str): The name of the table in the database, set to 'sxxp'.
        id (Column): The primary key, an integer ID uniquely identifying each entry.
        stock_id (Column): An integer foreign key linking to the StockSymbol table, cannot be null.
        date (Column): The date the STOXX Europe 600 index was published.
        index_symbol (Column): A string representing the symbol of the index within the market.
        index_name (Column): The formal name of the index
        index_isin (Column): The International Securities Identification Number 
        (ISIN) for the index.
        isin (Column): The International Securities Identification Number 
        (ISIN) for the stock
        rank (Column): An integer representing the rank of the stock within the 
        STOXX Europe 600 index, based on criteria such as market capitalization 
        or performance.

    Relationships:
        stocksymbol (relationship): SQLAlchemy `relationship` to the 
        corresponding `StockSymbol` instance, providing access to the stock 
        symbol associated with the stock index.

    Constraints:
        __table_args__ : A unique constraint (_sxxp_stockid_date_uc) is 
        applied to the `stock_id` and `date` fields to ensure there are no 
        duplicate entries for the same stock on the same date.

    """
    __tablename__ = 'sxxp'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey(StockSymbol.id), unique=True, nullable=False)
    date = Column(Date, nullable=False)
    index_symbol = Column(String(20))
    index_name = Column(String(50))
    index_isin = Column(String(12))
    isin = Column(String(12))
    rank = Column(Integer)

    stocksymbol = relationship("StockSymbol", back_populates="stoxx600")

    # Add a unique constraint for stock_id and date
    __table_args__ = (UniqueConstraint('stock_id', 'date',
                      name='_sxxp_stockid_date_uc'),)
