"""
Financial Analysis Platform

Main entry point for the financial analysis application.
Provides commands for data collection, processing, and dashboard.
"""

import argparse
import sys


def cmd_collect(args) -> None:
    """Run CVM data collection."""
    from src.cvm.collector import CVMDataCollector
    
    collector = CVMDataCollector(
        download_dir="data/raw",
        output_dir="data/raw"
    )
    collector.run(
        start_year=args.start_year,
        end_year=args.end_year
    )


def cmd_process(args) -> None:
    """Run financial data processing."""
    from src.cvm.processor import FinancialProcessor, FinancialIndicators
    
    processor = FinancialProcessor(
        data_dir="data/raw",
        output_dir="data/processed"
    )
    
    print("Loading company list...")
    companies = processor.load_companies()
    
    print(f"\nProcessing statements for {len(companies)} companies...")
    bp = processor.process_balance_sheet(args.start_year, args.end_year)
    dre = processor.process_income_statement(args.start_year, args.end_year)
    dfc = processor.process_cash_flow(args.start_year, args.end_year)
    
    processor.save_data(bp, "balance_sheet.csv")
    processor.save_data(dre, "income_statement.csv")
    processor.save_data(dfc, "cash_flow.csv")
    
    print("\nCalculating indicators...")
    indicators = FinancialIndicators(
        data_dir="data/raw",
        output_dir="data/processed"
    )
    indicators.load_data(bp, dre, companies)
    
    indicators.save_indicator(indicators.calculate_liquidity(), "liquidity.csv")
    indicators.save_indicator(indicators.calculate_debt(), "debt.csv")
    indicators.save_indicator(indicators.calculate_efficiency(), "efficiency.csv")
    indicators.save_indicator(indicators.calculate_profitability(), "profitability.csv")
    
    print("\n✓ Processing complete!")


def cmd_quotes(args) -> None:
    """Fetch quotes from MetaTrader 5."""
    from datetime import datetime
    from src.metatrader.quotes import MT5QuotesFetcher
    
    fetcher = MT5QuotesFetcher(output_dir="data/quotes")
    
    if not fetcher.connect():
        print("Failed to connect to MetaTrader 5")
        sys.exit(1)
    
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None
        
        for symbol in args.symbols:
            df = fetcher.fetch_quotes(symbol, start_date, end_date, args.timeframe)
            if df is not None:
                fetcher.save_to_parquet(df, symbol)
    finally:
        fetcher.disconnect()


def cmd_dashboard(args) -> None:
    """Run the Shiny dashboard."""
    import subprocess
    subprocess.run(["shiny", "run", "src/dashboard/app.py", "--port", str(args.port)])


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Financial Analysis Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py collect                  # Collect CVM data
  python main.py process                  # Process financial statements
  python main.py quotes PETR4 VALE3       # Fetch quotes from MT5
  python main.py dashboard                # Run Shiny dashboard
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect data from CVM")
    collect_parser.add_argument("--start-year", type=int, default=2016, help="Start year")
    collect_parser.add_argument("--end-year", type=int, default=2025, help="End year")
    collect_parser.set_defaults(func=cmd_collect)
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process financial data")
    process_parser.add_argument("--start-year", type=int, default=2016, help="Start year")
    process_parser.add_argument("--end-year", type=int, default=2025, help="End year")
    process_parser.set_defaults(func=cmd_process)
    
    # Quotes command
    quotes_parser = subparsers.add_parser("quotes", help="Fetch quotes from MetaTrader 5")
    quotes_parser.add_argument("symbols", nargs="+", help="Symbols to fetch (e.g., PETR4 VALE3)")
    quotes_parser.add_argument("--start-date", default="2020-01-01", help="Start date (YYYY-MM-DD)")
    quotes_parser.add_argument("--end-date", default=None, help="End date (YYYY-MM-DD)")
    quotes_parser.add_argument("--timeframe", default="D1", help="Timeframe (M1, M5, H1, D1, etc.)")
    quotes_parser.set_defaults(func=cmd_quotes)
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Run Shiny dashboard")
    dashboard_parser.add_argument("--port", type=int, default=8000, help="Port number")
    dashboard_parser.set_defaults(func=cmd_dashboard)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
