#### Setup 
-------
Use EDGAR search companies 10-K filings and return histoical financial statements in json format


Install  packages:
-------
```console
pip install requests bs4
```

Add USER_AGENT in config.py 

Usage:
-------
Run main.py
```console
stock = EDGAR('AAPL')
stock.get_financial_statement()
print(stock.income_statement)
print(stock.balance_sheet)
print(stock.cash_flow)
```

