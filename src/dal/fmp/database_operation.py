#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Created on 2024-03-10

@author: Roland VANDE MAELE

@abstract: the class act as an interface between the application and the 
database, taking structured data (e.g. JSON) and inserting it into the database 
via SQLAlchemy. These functions are part of the data access logic (DAL).

"""

from datetime import datetime
from sqlalchemy import update, exc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from src.models.base import Session
from src.models.fmp.stock import (StockSymbol, CompanyProfile, DailyChartEOD,
    HistoricalDividend, HistoricalKeyMetrics, STOXXEurope600)
from src.services.date import parse_date
from src.services.various import (safe_convert_to_int,
    generate_dividend_signature)


class StockManager:
    """Manages operations related to stock data in the database."""

    def __init__(self, db_session: Session):
        """Initializes the StockManager with a database session."""
        self.db_session = db_session

    def insert_stock_symbols(self, data):
        """
        Inserts a list of stock symbols into the database.
        
        Args:
            data (list of dict): A list of dictionaries, where each dictionary
            represents a stock symbol.

        Raises:
            RuntimeError: Raises an exception if an error occurs during database operations.
        """
        try:
            for item in data:
                # Create and insert a new StockSymbol instance for each JSON element
                stmt = insert(StockSymbol).values(
                    symbol=item.get("symbol"),
                    name=item.get("name"),
                    price=item.get("price"),
                    exchange=item.get("exchange"),
                    exchangeshortname=item.get("exchangeShortName"),
                    type_=item.get("type")
                )
                # Use insertion with ON CONFLICT DO NOTHING
                stmt = stmt.on_conflict_do_nothing(index_elements=['symbol'])
                self.db_session.execute(stmt)
            # Commit all new instances to the database
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Important to undo changes in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        finally:
            # Close session
            self.db_session.close()

    def insert_company_profile(self, data):
        """
        Inserts company profiles into the database based on provided data.

        This function iterates over a list of dictionaries, each representing a 
        company profile, and inserts them into the 'companyprofile' table. 
        Before inserting, it retrieves the corresponding 'stock_id' from the 
        'stocksymbol' table using the 'symbol' provided in each dictionary. If 
        the symbol does not exist in 'stocksymbol', the function skips 
        inserting that company profile. It handles duplicates by ignoring 
        attempts to insert records that would violate the unique constraint on 
        'stock_id'.

        Args:
            data (list of dict): A list of dictionaries, where each dictionary 
            contains data about a company profile. The 'symbol' is used to link 
            the company profile with its corresponding stock symbol.

        Raises:
            RuntimeError: An error occurred during database operations. The 
            error is logged, and a RuntimeError is raised with a message 
            indicating a database error occurred.

        Note:
            The function commits the transaction if all insertions are 
            successful. In case of an error, it performs a rollback to undo any 
            changes made during the transaction. This ensures the database 
            integrity is maintained. After attempting the operations, the 
            database session is closed.

        Example:
            >>> data = [
                    {
                        "symbol": "TTE.PA",
                        "currency": "EUR",
                        "cik": "0000320193",
                        "isin": "FR0000120271",
                        ...
                    }
                ]
            >>> insert_company_profiles(data)
        """
        try:
            for item in data:
                # Date parsing
                ipo_date_parsed = parse_date(item.get("ipoDate"))
                # Find the stock id from the 'stocksymbol' table based on the symbol
                stock_id_query = self.db_session.query(StockSymbol.id).filter(
                    StockSymbol.symbol == item.get("symbol")).scalar()

                # If stock symbol exists, insert the company profile
                if stock_id_query:
                    stmt = insert(CompanyProfile).values(
                        stock_id=stock_id_query,
                        beta=item.get("beta"),
		                vol_avg=item.get("volAvg"),
		                mkt_cap=item.get("mktCap"),
                        currency=item.get("currency"),
                        cik=str(item.get("cik")),  # convert to string
                        isin=item.get("isin"),
                        cusip=str(item.get("cusip")),  # Same as cik
                        industry=item.get("industry"),
                        website=item.get("website"),
                        description=item.get("description"),
                        sector=item.get("sector"),
                        country=item.get("country"),
                        image=item.get("image"),
                        ipo_date=ipo_date_parsed,
                        is_etf=item.get("isEtf"),
                        is_actively_trading=item.get("isActivelyTrading"),
                        is_adr=item.get("isAdr"),
                        is_fund=item.get("isFund")
                    )
                    # Use insertion with ON CONFLICT DO NOTHING to avoid stock_id duplicates
                    stmt = stmt.on_conflict_do_nothing(index_elements=['stock_id'])
                    self.db_session.execute(stmt)
                else:
                    # Handle case where stock symbol is not found
                    print(f"Stock symbol {item.get('symbol')} not found.")

            self.db_session.commit()
        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        finally:
            self.db_session.close()

    def insert_daily_chart_data(self, data):
        """Inserts daily historical stock data into the 'dailychart' table.

        This function processes a data structure that includes a stock symbol 
        and its associated historical daily data. It first resolves the stock 
        ID corresponding to the provided symbol from the 'stocksymbol' table. 
        For each entry in the historical data, the function attempts to insert 
        it into the 'dailychart' table.
        In case of a conflict (i.e., an attempt to insert a duplicate entry for 
        the same stock ID and date), the operation is designed to do nothing, 
        thus avoiding duplication errors.

        The function commits the transaction if all insertions are successful, 
        or it rolls back the transaction and closes the database session in 
        case of an error.

        Args:
            data (dict): A dictionary containing the stock symbol ('symbol') 
            and its historical data ('historical'). The 'historical' key should
            map to a list of dictionaries, each containing the fields:
            'date', 'open', 'high', 'low', 'close', 'adjClose', 'volume', 
            'unadjustedVolume', 'change', 'changePercent', and 'vwap'.

            Example:
            {
                "symbol": "AAPL",
                "historical": [
                    {
                        "date": "2023-10-06",
                        "open": 173.8,
                        "high": 176.61,
                        ...
                    },
                    ...
                ]
            }

        Raises:
            RuntimeError: An error occurred while inserting the data into the 
            database. The error is caught, the transaction is rolled back, and 
            the session is closed before re-raising the error with a message.

        """
        try:
            # Parse the symbol outside the loop since it's common to all entries
            symbol = data["symbol"]

            # Find the stock id from the 'stocksymbol' table based on the symbol
            stock_id_query = self.db_session.query(StockSymbol.id).filter(
                StockSymbol.symbol == symbol).scalar()

            # Proceed only if the stock symbol exists
            if stock_id_query:
                for item in data["historical"]:
                    # Parse the date field to ensure it matches the Date format in the database
                    date_parsed = parse_date(item.get("date"))

                    # Prepare the insertion statement with the found stock ID
                    stmt = insert(DailyChartEOD).values(
                        stock_id=stock_id_query,
                        date=date_parsed,
                        open=item.get("open"),
                        high=item.get("high"),
                        low=item.get("low"),
                        close=item.get("close"),
                        adj_close=item.get("adjClose"),
                        volume=item.get("volume"),
                        unadjusted_volume=item.get("unadjustedVolume"),
                        change=item.get("change"),
                        change_percent=item.get("changePercent"),
                        vwap=item.get("vwap"),
                    )

                    # Use insertion with ON CONFLICT DO NOTHING to avoid duplicate entries
                    stmt = stmt.on_conflict_do_nothing(index_elements=['stock_id', 'date'])
                    self.db_session.execute(stmt)

                self.db_session.commit()
            else:
                # Handle case where stock symbol is not found
                print(f"Stock symbol {symbol} not found.")

        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        finally:
            self.db_session.close()

    def update_daily_chart_data(self, data):
        """
        Updates daily chart data for a given stock symbol with the provided historical data.

        This method updates rows in the 'dailychart' table with the new data
        provided in the 'data' dictionary. Each entry in the 'data["historical"]
        ' list corresponds to a set of chart data for a specific date. The 
        method first finds the stock ID corresponding to the given symbol from 
        the 'stocksymbol' table. Then, it updates each row identified by the 
        stock ID and date with the new data. If the stock symbol does not exist 
        in the 'stocksymbol' table, the function prints a message and exits.
        The function uses a transactional approach, committing all updates at 
        once. If an error occurs during the process, all changes are rolled 
        back to maintain data integrity.

        Args:
            data (dict): A dictionary containing the stock symbol and 
            historical data to update. The dictionary should have a structure 
            similar to:
                        {
                            "symbol": "AAPL",
                            "historical": [
                                {
                                    "date": "2023-03-15",
                                    "open": 150.00,
                                    "high": 155.00,
                                    ...
                                },
                                ...
                            ]
                        }

        Raises:
            RuntimeError: An error occurred during the database operation, 
            including any issues with finding the stock ID or updating the 
            data. The error details are provided in the exception message, and 
            all changes are rolled back.

        Returns:
            None: This method does not return any value.
        
        """
        try:
            # Parse the symbol outside the loop since it's common to all entries
            symbol = data["symbol"]

            # Find the stock id from the 'stocksymbol' table based on the symbol
            stock_id_query = self.db_session.query(StockSymbol.id).filter(
                StockSymbol.symbol == symbol).scalar()

            # Proceed only if the stock symbol exists
            if stock_id_query:
                for item in data["historical"]:
                    # Parse the date field to ensure it matches the Date format in the database
                    date_parsed = parse_date(item.get("date"))

                    # Prepare the update statement
                    # It's essential to first define a way to identify which rows should be updated
                    stmt = update(DailyChartEOD).where(
                        DailyChartEOD.stock_id == stock_id_query,
                        DailyChartEOD.date == date_parsed
                    ).values(
                        open=item.get("open"),
                        high=item.get("high"),
                        low=item.get("low"),
                        close=item.get("close"),
                        adj_close=item.get("adjClose"),
                        volume=item.get("volume"),
                        unadjusted_volume=item.get("unadjustedVolume"),
                        change=item.get("change"),
                        change_percent=item.get("changePercent"),
                        vwap=item.get("vwap"),
                    )

                    # SQLAlchemy's `execute` method is used to execute the update statement
                    self.db_session.execute(stmt)

                self.db_session.commit()
            else:
                # Handle case where stock symbol is not found
                print(f"Stock symbol {symbol} not found.")

        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        finally:
            self.db_session.close()

    def update_daily_chart_adj_close_for_dividend(self, stock_id: int,
        dividend_date: str, dividend_amount: float):
        """
        Updates the adjusted close prices in the daily chart for a given stock,
        adjusting for dividends.

        This function updates the `adj_close` value for all entries of a 
        specific stock in the `dailychart` table, for dates before the dividend 
        detachment date. It first checks if the adjustment for the specified 
        dividend has already been made to avoid duplicate adjustments. The 
        adjustment is made to reflect the impact of the dividend detachment on 
        the adjusted close price.

        Args:
            stock_id (int): The ID of the stock to adjust.
            dividend_date (str): The date of the dividend detachment in 'YYYY-MM-DD' format.
            dividend_amount (float): The amount of the dividend paid.

        Returns:
            None. The function updates the `adj_close` values in-place and 
            commits the changes to the database.

        Raises:
        RuntimeError: If there's a failure in database operations, or if the 
        close price for the given stock on the specified dividend date is not 
        available in the database, or for any unforeseen errors that occur 
        during the execution of the method.

        Note:
            This function assumes that the `close` value on the dividend 
            detachment day already reflects the dividend detachment,
            i.e., that `close` is adjusted for that day. If that's not the 
            case, the `close` value for the dividend detachment day
            should be adjusted before applying this function.

        """
        # Generate unique signature for dividend event
        signature = generate_dividend_signature(stock_id, dividend_date,
        dividend_amount)

        # Check if the adjustment has already been made to avoid duplicates
        exists = self.db_session.query(
            self.db_session.query(DailyChartEOD).filter_by(dividend_signature=signature).exists()
        ).scalar()

        if exists:
            print("Adjustment already made for this dividend.")
            return

        try:
            # Convert the dividend date string to a datetime object
            dividend_date = datetime.strptime(dividend_date, '%Y-%m-%d').date()

            # Retrieve the 'close' price on the dividend date
            detachment_close = self.db_session.query(DailyChartEOD.close).filter(
                DailyChartEOD.stock_id == stock_id,
                DailyChartEOD.date == dividend_date
            ).scalar()

            if detachment_close is None:
                raise ValueError(
                    f"No closing price available for stock_id {stock_id} on {dividend_date}")

            corrective_ratio = dividend_amount / detachment_close

            # Use SQLAlchemy Core to perform a bulk update directly
            self.db_session.execute(
                update(DailyChartEOD).
                where(DailyChartEOD.stock_id == stock_id, DailyChartEOD.date == dividend_date).
                values({DailyChartEOD.dividend_signature: signature})
            )

            self.db_session.execute(
                update(DailyChartEOD).
                where(DailyChartEOD.stock_id == stock_id, DailyChartEOD.date < dividend_date).
                values({DailyChartEOD.adj_close: DailyChartEOD.close * (1 - corrective_ratio)})
            )

            # Commit the transaction
            self.db_session.commit()

        except exc.SQLAlchemyError as e:
            # Handle general SQLAlchemy errors
            self.db_session.rollback()
            raise RuntimeError(f"Database operation failed: {e}") from e

        except ValueError as e:
            # Handle specific value errors, e.g., missing close price
            raise RuntimeError(e) from e

        except Exception as e:
            # Catch-all for any other unforeseen errors
            self.db_session.rollback()
            raise RuntimeError(f"An unexpected error occurred: {e}") from e


    def insert_historical_dividend(self, data):
        """Inserts historical dividend data for a specified stock symbol into the database.

        This function processes a given dataset containing the stock symbol and 
        its historical dividend data. For each item in the dataset, it checks 
        if the stock symbol exists in the database. If so, it inserts the 
        dividend data while avoiding duplicates through the use of an 'on 
        conflict do nothing' strategy. The function ensures transaction 
        integrity by committing all successful operations or rolling back in 
        case of an error. It also handles the lifecycle of the database session.

        Args:
            data (dict): A dictionary containing the stock symbol and its historical dividend data.
            The expected format is:
            {
                "symbol": "StockSymbol",
                "historical": [
                    {
                        "date": "YYYY-MM-DD",
                        "adjDividend": float,
                        "dividend": float,
                        "paymentDate": "YYYY-MM-DD"
                    },
                    ...
                ]
            }

        Raises:
            RuntimeError: An error occurred during database operations. The 
            specific error is logged, and the database transaction is rolled back.

        """
        try:
            # Parse the symbol outside the loop since it's common to all entries
            symbol = data["symbol"]

            # Find the stock id from the 'stocksymbol' table based on the symbol
            stock_id_query = self.db_session.query(StockSymbol.id).filter(
                StockSymbol.symbol == symbol).scalar()

            # Proceed only if the stock symbol exists
            if stock_id_query:
                for item in data["historical"]:
                    # Parse the date field to ensure it matches the Date format in the database
                    date_parsed = parse_date(item.get("date"))
                    payment_date_parsed = parse_date(item.get("paymentDate"))

                    # Prepare the insertion statement with the found stock ID
                    stmt = insert(HistoricalDividend).values(
                        stock_id=stock_id_query,
                        date=date_parsed,
                        adj_dividend=item.get("adjDividend"),
                        dividend=item.get("dividend"),
                        payment_date=payment_date_parsed,
                    )

                    # Use insertion with ON CONFLICT DO NOTHING to avoid duplicate entries
                    stmt = stmt.on_conflict_do_nothing(index_elements=['stock_id', 'date'])
                    self.db_session.execute(stmt)

                self.db_session.commit()
            else:
                # Handle case where stock symbol is not found
                print(f"Stock symbol {symbol} not found.")

        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        finally:
            self.db_session.close()

    def insert_historical_key_metrics(self, data):
        """
        Inserts historical key financial metrics for stocks into the database.
        
        This function iterates over a list of dictionaries, each representing 
        financial metrics for a stock on a specific date. It checks if the 
        stock symbol exists in the 'StockSymbol' table and inserts the metrics 
        into the 'HistoricalKeyMetrics' table if so. The function avoids 
        inserting duplicate data using an 'ON CONFLICT DO NOTHING' strategy. If 
        the stock symbol is not found in the 'StockSymbol' table, it reports 
        this. The function manages database transactions, committing on success 
        or rolling back in case of an error.

        Args:
            data (list of dict): A list where each dictionary contains the 
            stock symbol, date, calendar year, period, and various financial 
            metrics such as revenuePerShare, netIncomePerShare, etc.

        Raises:
            RuntimeError: If a database error occurs during the operation. The 
            error message includes the original error for debugging purposes.

        Example usage:
            insert_historical_key_metrics([
                {
                    "symbol": "AAPL",
                    "date": "2023-12-30",
                    "calendarYear": "2024",
                    "period": "Q1",
                    "revenuePerShare": 7.6765587651407,
                    "netIncomePerShare": 2.177362885875074,
                    "operatingCashFlowPerShare": 2.561206873805463,
                    "freeCashFlowPerShare": 2.407643599155941,
                    "cashPerShare": 4.6929244886622214,
                    ...
                },
                ...
            ])
        """
        try:
            for item in data:  # Iterate over each item in the input data list
                symbol = item["symbol"]
                date_parsed = parse_date(item["date"])

                # Find the stock id from the 'stocksymbol' table based on the symbol
                stock_id_query = self.db_session.query(StockSymbol.id).filter(
                    StockSymbol.symbol == symbol).scalar()

                # Proceed only if the stock symbol exists
                if stock_id_query:
                    # Prepare the insertion statement with the found stock ID and parsed data
                    stmt = insert(HistoricalKeyMetrics).values(
                        stock_id=stock_id_query,
                        date=date_parsed,
                        calendar_year=item.get("calendarYear"),
                        period=item.get("period"),
                        revenue_per_share=item.get("revenuePerShare"),
                        net_income_per_share=item.get("netIncomePerShare"),
                        operating_cash_flow_per_share=item.get(
                            "operatingCashFlowPerShare"),
                        free_cash_flow_per_share=item.get(
                            "freeCashFlowPerShare"),
                        cash_per_share=item.get("cashPerShare"),
                        book_value_per_share=item.get("bookValuePerShare"),
                        tangible_book_value_per_share=item.get(
                            "tangibleBookValuePerShare"),
                        shareholders_equity_per_share=item.get(
                            "shareholdersEquityPerShare"),
                        interest_debt_per_share=item.get(
                            "interestDebtPerShare"),
                        market_cap=item.get("marketCap"),
                        enterprise_value=item.get("enterpriseValue"),
                        pe_ratio=item.get("peRatio"),
                        price_to_sales_ratio=item.get("priceToSalesRatio"),
                        pocf_ratio=item.get("pocfRatio"),
                        pfcf_ratio=item.get("pfcfRatio"),
                        pb_ratio=item.get("pbRatio"),
                        ptb_ratio=item.get("ptbRatio"),
                        ev_to_sales=item.get("evToSales"),
                        enterprise_value_over_ebitda=item.get(
                            "enterpriseValueOverEBITDA"),
                        ev_to_operating_cash_flow=item.get(
                            "evToOperatingCashFlow"),
                        ev_to_free_cash_flow=item.get("evToFreeCashFlow"),
                        earnings_yield=item.get("earningsYield"),
                        free_cash_flow_yield=item.get("freeCashFlowYield"),
                        debt_to_equity=item.get("debtToEquity"),
                        debt_to_assets=item.get("debtToAssets"),
                        net_debt_to_ebitda=item.get("netDebtToEBITDA"),
                        current_ratio=item.get("currentRatio"),
                        interest_coverage=item.get("interestCoverage"),
                        income_quality=item.get("incomeQuality"),
                        dividend_yield=item.get("dividendYield"),
                        payout_ratio=item.get("payoutRatio"),
                        sales_general_and_administrative_to_revenue=item.get(
                            "salesGeneralAndAdministrativeToRevenue"),
                        research_and_development_to_revenue=item.get(
                            "researchAndDevelopmentToRevenue"),
                        intangibles_to_total_assets=item.get(
                            "intangiblesToTotalAssets"),
                        capex_to_operating_cash_flow=item.get(
                            "capexToOperatingCashFlow"),
                        capex_to_revenue=item.get("capexToRevenue"),
                        capex_to_depreciation=item.get("capexToDepreciation"),
                        stock_based_compensation_to_revenue=item.get(
                            "stockBasedCompensationToRevenue"),
                        graham_number=item.get("grahamNumber"),
                        roic=item.get("roic"),
                        return_on_tangible_assets=item.get(
                            "returnOnTangibleAssets"),
                        graham_net_net=item.get("grahamNetNet"),
                        working_capital=item.get("workingCapital"),
                        tangible_asset_value=item.get("tangibleAssetValue"),
                        net_current_asset_value=item.get(
                            "netCurrentAssetValue"),
                        invested_capital=item.get("investedCapital"),
                        average_receivables=item.get("averageReceivables"),
                        average_payables=item.get("averagePayables"),
                        average_inventory=item.get("averageInventory"),
                        days_sales_outstanding=item.get("daysSalesOutstanding"),
                        days_payables_outstanding=item.get(
                            "daysPayablesOutstanding"),
                        days_of_inventory_on_hand=item.get(
                            "daysOfInventoryOnHand"),
                        receivables_turnover=item.get("receivablesTurnover"),
                        payables_turnover=item.get("payablesTurnover"),
                        inventory_turnover=item.get("inventoryTurnover"),
                        roe=item.get("roe"),
                        capex_per_share=item.get("capexPerShare")
                    )

                    # Use insertion with ON CONFLICT DO NOTHING to avoid duplicate entries
                    stmt = stmt.on_conflict_do_nothing(index_elements=['stock_id', 'date'])
                    self.db_session.execute(stmt)

                else:
                    # Handle case where stock symbol is not found
                    print(f"Stock symbol {symbol} not found.")

            self.db_session.commit()

        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        finally:
            self.db_session.close()

    def insert_sxxp_historical_components(self, data):
        """Inserts historical component data into the 'STOXXEurope600' table.

        This function takes a list of dictionaries containing stock information 
        and inserts each entry into the 'STOXXEurope600' table. If the entry 
        already exists (determined by a unique constraint on 'stock_id' and 
        'creation_date'), the insertion is skipped. The function handles cases 
        where the company profile corresponding to an ISIN does not exist in 
        the database.

        Args:
            data (list of dict): A list of dictionaries where each dictionary 
            contains the data for one stock. Each dictionary should have the 
            keys 'ISIN', 'Creation_Date', 'Index_Symbol', 'Index_Name', 'Index 
            ISIN', and 'Rank (FINAL)' with appropriate values.

        Raises:
            RuntimeError: An error occurred when attempting to insert the data 
            into the database. The original SQLAlchemyError is wrapped in a 
            RuntimeError and raised.

        Example:
            data_to_insert = [
                {'ISIN': 'US1234567890', 'Creation_Date': '20240301', 
                'Index_Symbol': 'SXXP', 'Index_Name': 'STOXX Europe 600',
                'Index ISIN': 'EU0009658202', 'Rank (FINAL)': 1},
                ...
            ]
            insert_sxxp_historical_components(data_to_insert)
        """
        try:
            for row in data:

                date_parsed = parse_date(row['Creation_Date'])
                isin = row['ISIN']
                rank = safe_convert_to_int(row['Rank (FINAL)'])

                # Get the stock_id of the CompanyProfile with the highest vol_avg for the given ISIN
                stock_id_query = self.db_session.query(
                    CompanyProfile.stock_id
                ).filter(
                    (CompanyProfile.isin == isin) and (CompanyProfile.is_actively_trading is True)
                ).order_by(
                    CompanyProfile.vol_avg.desc()  # Order by vol_avg in descending order
                ).limit(1).scalar()  # Get the first record (the one with the highest vol_avg)


                if stock_id_query and rank > 0:
                    # Create a new STOXXEurope600 record
                    stmt = insert(STOXXEurope600).values(
                        stock_id=stock_id_query,
                        date=date_parsed,
                        index_symbol=row['Index_Symbol'],
                        index_name=row['Index_Name'],
                        index_isin=row['Index ISIN'],
                        isin=isin,
                        rank=rank
                    )

                    # Use the ON CONFLICT clause to ignore the insert if it would cause a conflict
                    stmt = stmt.on_conflict_do_nothing(
                        index_elements=['stock_id', 'date'])
                    # Execute the statement
                    self.db_session.execute(stmt)

                else:
                    # Handle case where stock symbol is not found
                    print(f"Stock ISIN {isin} not found.")

            # Commit the session to the database
            self.db_session.commit()

        except SQLAlchemyError as e:
            self.db_session.rollback()  # Rollback in case of error
            raise RuntimeError(f"Database error occurred: {e}") from e
        except Exception as e:
            self.db_session.rollback()  # Rollback in case of any other error
            raise RuntimeError(f"An unexpected error occurred: {e}") from e
        finally:
            self.db_session.close()
