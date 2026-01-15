"""
Financial Data Processor Module

Processes financial statements from CVM and calculates financial indicators.
"""

from pathlib import Path

import pandas as pd


class FinancialProcessor:
    """Processes financial statements and calculates indicators."""

    def __init__(self, data_dir: str = "data/raw", output_dir: str = "data/processed"):
        """
        Initialize the processor.

        Args:
            data_dir: Directory containing raw DFP data
            output_dir: Directory to save processed data
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.companies: list[str] = []

    def load_companies(self, filepath: str = None) -> list[str]:
        """Load list of company names to filter."""
        if filepath is None:
            filepath = self.data_dir / "companies.csv"
        
        df = pd.read_csv(filepath, sep=';')
        self.companies = df.iloc[:, 0].tolist()
        return self.companies

    def _load_statement(self, filename: str) -> pd.DataFrame:
        """Load a financial statement CSV file."""
        filepath = self.data_dir / filename
        return pd.read_csv(filepath, sep=';', decimal=',', encoding='ISO-8859-1')

    def process_balance_sheet(self, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Process Balance Sheet (Balanço Patrimonial).

        Returns:
            Filtered and pivoted balance sheet data
        """
        # Load assets (BPA) and liabilities (BPP)
        bpa = self._load_statement(f"dfp_cia_aberta_BPA_con_{start_year}-{end_year}.csv")
        bpp = self._load_statement(f"dfp_cia_aberta_BPP_con_{start_year}-{end_year}.csv")
        
        bp = pd.concat([bpa, bpp], axis=0)
        
        accounts = [
            "Ativo Total",
            "Passivo Total",
            "Patrimônio Líquido Consolidado",
            "Ativo Circulante",
            "Ativo Não Circulante",
            "Passivo Circulante",
            "Passivo Não Circulante"
        ]
        
        filtered = (
            bp[
                bp.DS_CONTA.isin(accounts) &
                bp.DENOM_CIA.isin(self.companies) &
                (bp.ORDEM_EXERC == 'ÚLTIMO')
            ][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
            .pivot(index=['DT_REFER', 'DENOM_CIA'], columns='DS_CONTA', values='VL_CONTA')
            .assign(passivo=lambda x: x['Passivo Total'] - x['Patrimônio Líquido Consolidado'])
            .reset_index()
        )
        
        return filtered

    def process_income_statement(self, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Process Income Statement (DRE - Demonstração do Resultado).

        Returns:
            Filtered and pivoted income statement data
        """
        dre = self._load_statement(f"dfp_cia_aberta_DRE_con_{start_year}-{end_year}.csv")
        
        accounts = [
            "Receita de Venda de Bens e/ou Serviços",
            "Custo dos Bens e/ou Serviços Vendidos",
            "Lucro/Prejuízo Consolidado do Período"
        ]
        
        filtered = (
            dre[
                dre.DS_CONTA.isin(accounts) &
                dre.DENOM_CIA.isin(self.companies) &
                dre.CD_CONTA.isin(['3.11', '3.01', '3.02']) &
                (dre.ORDEM_EXERC == 'ÚLTIMO')
            ][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
            .pivot(index=['DT_REFER', 'DENOM_CIA'], columns='DS_CONTA', values='VL_CONTA')
            .reset_index()
        )
        
        return filtered

    def process_cash_flow(self, start_year: int, end_year: int) -> pd.DataFrame:
        """
        Process Cash Flow Statement (DFC).

        Returns:
            Filtered and pivoted cash flow data
        """
        dfc = self._load_statement(f"dfp_cia_aberta_DFC_MI_con_{start_year}-{end_year}.csv")
        
        accounts = [
            "Caixa Líquido Atividades Operacionais",
            "Caixa Líquido Atividades de Investimento",
            "Caixa Líquido Atividades de Financiamento",
            "Aumento (Redução) de Caixa e Equivalentes",
            "Saldo Inicial de Caixa e Equivalentes",
            "Saldo Final de Caixa e Equivalentes"
        ]
        
        filtered = (
            dfc[
                dfc.DS_CONTA.isin(accounts) &
                dfc.DENOM_CIA.isin(self.companies) &
                (dfc.ORDEM_EXERC == 'ÚLTIMO')
            ][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
            .pivot(index=['DT_REFER', 'DENOM_CIA'], columns='DS_CONTA', values='VL_CONTA')
            .reset_index()
        )
        
        return filtered

    def save_data(self, df: pd.DataFrame, filename: str) -> None:
        """Save DataFrame to CSV in output directory."""
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False, sep=';', encoding='latin1')
        print(f"✓ Saved: {filename}")


class FinancialIndicators:
    """Calculates financial indicators from processed data."""

    def __init__(self, data_dir: str = "data/raw", output_dir: str = "data/processed"):
        """
        Initialize indicators calculator.

        Args:
            data_dir: Directory containing raw DFP data
            output_dir: Directory to save calculated indicators
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.companies: list[str] = []
        self._df_dfp: pd.DataFrame = None

    def load_data(self, bp: pd.DataFrame, dre: pd.DataFrame, companies: list[str]) -> None:
        """Load base data for indicator calculations."""
        self.companies = companies
        self._df_dfp = pd.concat([bp, dre], axis=0)
        self._df_dfp = self._df_dfp[self._df_dfp.DENOM_CIA.isin(companies)]

    def _load_statement(self, filename: str) -> pd.DataFrame:
        """Load a financial statement CSV file."""
        filepath = self.data_dir / filename
        return pd.read_csv(filepath, sep=';', decimal=',', encoding='ISO-8859-1')

    def calculate_liquidity(self) -> pd.DataFrame:
        """
        Calculate liquidity indicators.

        Returns:
            DataFrame with liquidity ratios
        """
        accounts = ["1.01.01", "2.01", "1.01", "1.01.04", "1.01.07", "1.02", "2.02"]
        
        df = self._df_dfp[
            self._df_dfp.CD_CONTA.isin(accounts) &
            (self._df_dfp.ORDEM_EXERC == 'ÚLTIMO')
        ][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
        
        result = (
            df.pivot(index=['DT_REFER', 'DENOM_CIA'], columns='DS_CONTA', values='VL_CONTA')
            .reset_index()
            .assign(
                liquidez_imediata=lambda x: x['Caixa e Equivalentes de Caixa'] / x['Passivo Circulante'],
                liquidez_seca=lambda x: (x['Ativo Circulante'] - x['Estoques'] - x['Despesas Antecipadas']) / x['Passivo Circulante'],
                liquidez_corrente=lambda x: x['Ativo Circulante'] / x['Passivo Circulante'],
                liquidez_geral=lambda x: (x['Ativo Circulante'] + x['Ativo Não Circulante']) / (x['Passivo Circulante'] + x['Passivo Não Circulante'])
            )
            [['DT_REFER', 'DENOM_CIA', 'liquidez_imediata', 'liquidez_seca', 'liquidez_corrente', 'liquidez_geral']]
        )
        
        return result

    def calculate_debt(self) -> pd.DataFrame:
        """
        Calculate debt/leverage indicators.

        Returns:
            DataFrame with debt ratios
        """
        accounts = ["1", "2.01", "2.02", "2.01.04", "2.02.01", "2.03", "3.05"]
        
        df = self._df_dfp[
            self._df_dfp.CD_CONTA.isin(accounts) &
            (self._df_dfp.ORDEM_EXERC == 'ÚLTIMO')
        ][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
        
        result = (
            df.pivot(index=['DT_REFER', 'DENOM_CIA'], columns='CD_CONTA', values='VL_CONTA')
            .reset_index()
            .assign(
                divida_pl=lambda x: (x["2.01.04"] + x["2.02.01"]) / x["2.03"],
                divida_ativos=lambda x: (x["2.01.04"] + x["2.02.01"]) / x["1"],
                divida_ebit=lambda x: (x["2.01.04"] + x["2.02.01"]) / x["3.05"],
                pl_ativos=lambda x: x["2.03"] / x["1"],
                passivos_ativos=lambda x: (x["2.01"] + x["2.02"]) / x["1"]
            )
            [['DT_REFER', 'DENOM_CIA', 'divida_pl', 'divida_ativos', 'divida_ebit', 'pl_ativos', 'passivos_ativos']]
        )
        
        return result

    def calculate_efficiency(self) -> pd.DataFrame:
        """
        Calculate efficiency/margin indicators.

        Returns:
            DataFrame with margin ratios
        """
        accounts = ["3.01", "3.03", "3.05", "3.11"]
        
        df = self._df_dfp[
            self._df_dfp.CD_CONTA.isin(accounts) &
            (self._df_dfp.ORDEM_EXERC == 'ÚLTIMO')
        ][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
        
        result = (
            df.pivot(index=['DT_REFER', 'DENOM_CIA'], columns='CD_CONTA', values='VL_CONTA')
            .reset_index()
            .assign(
                margem_bruta=lambda x: x["3.03"] / x["3.01"] * 100,
                margem_liquida=lambda x: x["3.11"] / x["3.01"] * 100,
                margem_ebit=lambda x: x["3.05"] / x["3.01"] * 100
            )
            [['DT_REFER', 'DENOM_CIA', 'margem_bruta', 'margem_liquida', 'margem_ebit']]
        )
        
        return result

    def calculate_profitability(self) -> pd.DataFrame:
        """
        Calculate profitability indicators (ROE, ROA, ROIC).

        Returns:
            DataFrame with profitability ratios
        """
        accounts = ["1", "2", "2.03", "3.05", "3.08", "3.11"]
        
        df = self._df_dfp[
            self._df_dfp.CD_CONTA.isin(accounts) &
            (self._df_dfp.ORDEM_EXERC == 'ÚLTIMO')
        ][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
        
        result = (
            df.pivot(index=['DT_REFER', 'DENOM_CIA'], columns='CD_CONTA', values='VL_CONTA')
            .reset_index()
            .assign(
                roic=lambda x: (x["3.05"] - x["3.08"]) / x["2"] * 100,
                roe=lambda x: x["3.11"] / x["2.03"] * 100,
                roa=lambda x: x["3.11"] / x["1"] * 100
            )
            [['DT_REFER', 'DENOM_CIA', 'roic', 'roe', 'roa']]
        )
        
        return result

    def save_indicator(self, df: pd.DataFrame, filename: str) -> None:
        """Save indicator DataFrame to CSV."""
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False, sep=';', encoding='latin1')
        print(f"✓ Saved: {filename}")


if __name__ == "__main__":
    # Example usage
    processor = FinancialProcessor()
    companies = processor.load_companies()
    
    print("Processing financial statements...")
    bp = processor.process_balance_sheet(2016, 2025)
    dre = processor.process_income_statement(2016, 2025)
    dfc = processor.process_cash_flow(2016, 2025)
    
    processor.save_data(bp, "balance_sheet.csv")
    processor.save_data(dre, "income_statement.csv")
    processor.save_data(dfc, "cash_flow.csv")
    
    print("\nCalculating indicators...")
    indicators = FinancialIndicators()
    indicators.load_data(bp, dre, companies)
    
    liquidity = indicators.calculate_liquidity()
    debt = indicators.calculate_debt()
    efficiency = indicators.calculate_efficiency()
    profitability = indicators.calculate_profitability()
    
    indicators.save_indicator(liquidity, "liquidity.csv")
    indicators.save_indicator(debt, "debt.csv")
    indicators.save_indicator(efficiency, "efficiency.csv")
    indicators.save_indicator(profitability, "profitability.csv")
