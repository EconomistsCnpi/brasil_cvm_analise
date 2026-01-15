# Financial Analysis Platform

Plataforma de análise fundamentalista de ações brasileiras.

## Estrutura do Projeto

```
├── src/                    # Código fonte
│   ├── cvm/               # Módulo de dados CVM
│   │   ├── collector.py   # Coleta de dados DFP
│   │   └── processor.py   # Processamento e indicadores
│   ├── metatrader/        # Módulo MetaTrader 5
│   │   └── quotes.py      # Coleta de cotações
│   └── dashboard/         # Dashboard Shiny
│       └── app.py         # Aplicação web
├── data/                   # Dados
│   ├── raw/               # Dados brutos da CVM
│   └── processed/         # Indicadores calculados
├── notebooks/             # Análises exploratórias
├── main.py                # Ponto de entrada
└── requirements.txt       # Dependências
```

## Instalação

```bash
# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Uso

### Coletar dados da CVM
```bash
python main.py collect --start-year 2016 --end-year 2025
```

### Processar demonstrativos financeiros
```bash
python main.py process
```

### Coletar cotações via MetaTrader 5 (Windows)
```bash
python main.py quotes PETR4 VALE3 ABEV3 --timeframe D1
```

### Executar dashboard
```bash
python main.py dashboard --port 8000
```

## Indicadores Calculados

| Categoria | Indicadores |
|-----------|-------------|
| Liquidez | Imediata, Seca, Corrente, Geral |
| Endividamento | Dívida/PL, Dívida/Ativos, Dívida/EBIT |
| Eficiência | Margem Bruta, Líquida, EBIT |
| Rentabilidade | ROE, ROA, ROIC |

## Fonte de Dados

- **CVM**: Demonstrativos Financeiros Padronizados (DFP) - dados.cvm.gov.br
- **MetaTrader 5**: Cotações históricas de ações (Windows only)
