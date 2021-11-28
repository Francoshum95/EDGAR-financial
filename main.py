from bs4 import BeautifulSoup
import requests
from constants import BALANCE_SHEET, INCOME_STATEMENT, STATEMENT_OF_CASH_FLOW
from config import USER_AGENT


class EDGAR:
  def __init__(self,ticker):
    self.ticker = ticker
    self.heads = {'User-Agent': USER_AGENT}
    self.doc_url = "https://www.sec.gov/Archives/edgar/data/"

    self.get_cik_num()
    self.init()
   
  
  def get_cik_num(self):
    response = requests.get("https://www.sec.gov/files/company_tickers.json").json()

    for i in range(len(response)):
      if response[str(i)]['ticker'] == self.ticker.upper():
        self.cik_num = str(response[str(i)]['cik_str'])

  def init(self):
    base_url = "https://data.sec.gov/submissions/"
    adj_cik_num = "0" * (10 - len(self.cik_num)) + self.cik_num
    url= base_url + "CIK" + adj_cik_num + ".json"

    self.master_data  = requests.get(url, headers=self.heads).json()
  
  def get_company_info(self):
    return {
      'ticker': self.ticker,
      'cik_number': self.cik_num,
      'name': self.master_data['name'],
      'exchanges': self.master_data['exchanges'][0]
    }

  def get_financial_statement(self):

  
    filling_master = self.master_data['filings']['recent']
    self.income_statement = []
    self.balance_sheet = []
    self.cash_flow = []

    def get_income_statement(temp_df):
      income_statement_url = self.doc_url + self.cik_num + "/" + doc_number + "/" + report.htmlfilename.text
      statement_response = requests.get(income_statement_url, headers=self.heads).content
      statement_soup = BeautifulSoup(statement_response, 'html.parser')

      statement_headers = []

      for index, row in enumerate(statement_soup.table.find_all('tr')):
        cols = row.find_all('td')
        if (len(row.find_all('th')) != 0):
          hed_row = [ele.text.strip() for ele in row.find_all('th')]
         
          statement_headers.append(hed_row)
        elif (len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0): 
          reg_row = [ele.text.strip() for ele in cols]
          
          temp_df.update({reg_row[0]: reg_row[1]})
      
      if  len(statement_headers) == 2:
        temp_df.update({'title': statement_headers[0][0]})
        temp_df.update({'date': statement_headers[1][0]})
      elif len(statement_headers) == 1:
        temp_df.update({'title': statement_headers[0][0]})
        temp_df.update({'date': statement_headers[0][1]})
        
    
    def get_balance_sheet(temp_df):
      balance_sheet_url = self.doc_url + self.cik_num +  "/" + doc_number + "/" + report.htmlfilename.text
      statement_response = requests.get(balance_sheet_url, headers=self.heads).content
      
      statement_soup = BeautifulSoup(statement_response, 'html.parser')

      for index, row in enumerate(statement_soup.table.find_all('tr')):
        cols = row.find_all('td')

        if (len(row.find_all('th')) != 0):
          hed_row = [ele.text.strip() for ele in row.find_all('th')]
          temp_df.update({'title': hed_row[0]})
          temp_df.update({'date': hed_row[1]})
        elif (len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0): 
          reg_row = [ele.text.strip() for ele in cols]
          if len(reg_row) > 1: 
            temp_df.update({reg_row[0]: reg_row[1]})
      
    def get_cash_flow(temp_df):
      cash_flow_url = self.doc_url + self.cik_num +  "/" + doc_number + "/" + report.htmlfilename.text
      statement_response = requests.get(cash_flow_url, headers=self.heads).content
      
      statement_soup = BeautifulSoup(statement_response, 'html.parser')
      statement_headers = []

      for index, row in enumerate(statement_soup.table.find_all('tr')):
        cols = row.find_all('td')

        if (len(row.find_all('th')) != 0):
          hed_row = [ele.text.strip() for ele in row.find_all('th')]
          statement_headers.append(hed_row)

        elif (len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0): 
          reg_row = [ele.text.strip() for ele in cols]
          temp_df.update({reg_row[0]: reg_row[1]})

      if len(statement_headers) == 2:
        temp_df.update({'title': statement_headers[0][0]})
        temp_df.update({'date': statement_headers[1][0]})
      elif len(statement_headers) == 1:
        temp_df.update({'title': statement_headers[0][0]})
        temp_df.update({'date': statement_headers[0][1]})

    for index in range(len(filling_master['form'])):
      if filling_master['form'][index] == "10-K":

        temp_income_df = {}
        temp_balance_df = {}
        temp_cashflow_df = {}

        doc_number =  filling_master['accessionNumber'][index].replace("-", "")
        xml_url = self.doc_url + self.cik_num + "/" + doc_number + "/" + "FilingSummary.xml"
        
        xml_response = requests.get(xml_url, headers=self.heads).content
        xml_summary = BeautifulSoup(xml_response, 'html.parser')
        reports = xml_summary.find('myreports')
        
        try: 
          for report in reports.find_all('report')[:-1]:
            if report.shortname.text.lower() in INCOME_STATEMENT:
              get_income_statement(temp_income_df)
            elif report.shortname.text.lower() in BALANCE_SHEET:
              get_balance_sheet(temp_balance_df)
            elif report.shortname.text.lower() in STATEMENT_OF_CASH_FLOW:
              get_cash_flow(temp_cashflow_df)
        except AttributeError:
          pass

        self.income_statement.append(temp_income_df)   
        self.balance_sheet.append(temp_balance_df)
        self.cash_flow.append(temp_cashflow_df)