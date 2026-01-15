"""
CVM Data Collector Module

Downloads and extracts financial statements (DFP) from the Brazilian
Securities and Exchange Commission (CVM).
"""

import os
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import wget


class CVMDataCollector:
    """Collects financial data from CVM (Comissão de Valores Mobiliários)."""

    BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/"
    COMPANY_INFO_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"

    def __init__(self, download_dir: str = "data/raw", output_dir: str = "data/raw"):
        """
        Initialize the collector.

        Args:
            download_dir: Directory to download ZIP files
            output_dir: Directory to extract CSV files
        """
        self.download_dir = Path(download_dir)
        self.output_dir = Path(output_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create directories if they don't exist."""
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_company_info(self) -> pd.DataFrame:
        """
        Download and filter active companies listed on stock exchange.

        Returns:
            DataFrame with company names (excluding banks and financial institutions)
        """
        dest_file = wget.download(self.COMPANY_INFO_URL, out=str(self.download_dir))
        
        info = pd.read_csv(dest_file, sep=';', encoding='latin1', dtype={'CNPJ_CIA': str})
        
        # Filter active companies on stock exchange, excluding banks
        excluded_sectors = ["Bancos", "Intermediação Financeira", "Seguradoras e Corretoras"]
        
        companies = (
            info[
                (info['SIT'] == 'ATIVO') &
                (info['TP_MERC'] == 'BOLSA') &
                (~info['SETOR_ATIV'].isin(excluded_sectors))
            ]
            .sort_values('DENOM_SOCIAL')
        )
        
        return companies

    def download_dfp(self, start_year: int, end_year: int) -> list[str]:
        """
        Download DFP ZIP files from CVM.

        Args:
            start_year: First year to download
            end_year: Last year to download (inclusive)

        Returns:
            List of downloaded file paths
        """
        downloaded_files = []
        
        for year in range(start_year, end_year + 1):
            filename = f"dfp_cia_aberta_{year}.zip"
            filepath = self.download_dir / filename
            
            # Remove existing file if present
            if filepath.exists():
                filepath.unlink()
            
            url = f"{self.BASE_URL}{filename}"
            try:
                wget.download(url, out=str(self.download_dir))
                downloaded_files.append(str(filepath))
                print(f"\n✓ Downloaded: {filename}")
            except Exception as e:
                print(f"\n✗ Failed to download {filename}: {e}")
        
        return downloaded_files

    def extract_files(self, start_year: int, end_year: int) -> None:
        """
        Extract all downloaded ZIP files.

        Args:
            start_year: First year to extract
            end_year: Last year to extract (inclusive)
        """
        for year in range(start_year, end_year + 1):
            zip_path = self.download_dir / f"dfp_cia_aberta_{year}.zip"
            if zip_path.exists():
                with ZipFile(zip_path, 'r') as zf:
                    zf.extractall(self.output_dir)
                print(f"✓ Extracted: {zip_path.name}")

    def concatenate_statements(
        self,
        start_year: int,
        end_year: int,
        statement_types: list[str]
    ) -> dict[str, pd.DataFrame]:
        """
        Concatenate financial statements across years.

        Args:
            start_year: First year
            end_year: Last year (inclusive)
            statement_types: List of statement types (e.g., ['BPA_con', 'DRE_con'])

        Returns:
            Dictionary mapping statement type to concatenated DataFrame
        """
        result = {}
        
        for stmt_type in statement_types:
            frames = []
            for year in range(start_year, end_year + 1):
                filepath = self.output_dir / f"dfp_cia_aberta_{stmt_type}_{year}.csv"
                if filepath.exists():
                    df = pd.read_csv(
                        filepath,
                        sep=';',
                        decimal=',',
                        encoding='ISO-8859-1'
                    )
                    frames.append(df)
            
            if frames:
                result[stmt_type] = pd.concat(frames, ignore_index=True)
                print(f"✓ Concatenated {stmt_type}: {len(result[stmt_type])} rows")
        
        return result

    def run(
        self,
        start_year: int = 2016,
        end_year: int = 2025,
        statements: list[str] = None
    ) -> dict[str, pd.DataFrame]:
        """
        Execute the complete data collection pipeline.

        Args:
            start_year: First year to collect
            end_year: Last year to collect (inclusive)
            statements: Statement types to concatenate

        Returns:
            Dictionary with concatenated DataFrames
        """
        if statements is None:
            statements = ['BPA_con', 'BPP_con', 'DRE_con', 'DFC_MI_con']

        print("=== CVM Data Collection ===\n")
        
        print("1. Downloading company info...")
        companies = self.download_company_info()
        companies['DENOM_SOCIAL'].to_csv(
            self.output_dir / 'companies.csv',
            index=False,
            sep=';'
        )
        
        print("\n2. Downloading DFP files...")
        self.download_dfp(start_year, end_year)
        
        print("\n3. Extracting files...")
        self.extract_files(start_year, end_year)
        
        print("\n4. Concatenating statements...")
        data = self.concatenate_statements(start_year, end_year, statements)
        
        print("\n=== Collection Complete ===")
        return data


if __name__ == "__main__":
    collector = CVMDataCollector()
    data = collector.run(start_year=2016, end_year=2025)
