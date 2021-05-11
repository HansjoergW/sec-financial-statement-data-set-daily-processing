import requests

ticker = "320193"

url = 'https://www.sec.gov/cgi-bin/browse-edgar'
query_args = {'CIK': ticker, 'action': 'getcompany', 'output': 'xml'}
response = requests.get(url, params=query_args)
print(response.text)