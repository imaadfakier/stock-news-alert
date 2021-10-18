import requests
import os
# import datetime
# import math
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
BASE_URL = 'https://www.alphavantage.co/query'
NEWS_BASE_URL = 'https://newsapi.org/v2/everything'
ACCOUNT_SID = 'enter accound sid'
AUTH_TOKEN = 'enter auth token'
PERCENTAGE_THRESHOLD = 1

#   - set(ting) environment variables
os.environ['ALPHA_STOCK_PRICES_API_KEY'] = 'enter api key'
os.environ['NEWS_API_KEY'] = 'enter api key'
os.environ['TWILIO_ACCOUNT_SID'] = 'enter accound sid'
os.environ['TWILIO_AUTH_TOKEN'] = 'enter auth token'

parameters = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK,
    #   - get(ting) environment variable(s)
    'apikey': os.environ.get(key='ALPHA_STOCK_PRICES_API_KEY'),
    'outputsize': 'compact'
}
news_endpoint_parameters = {
    'qInTitle': COMPANY_NAME,
    'from': '2021-07-01',
    'sortBy': 'publishedAt',
    #   - get(ting) environment variable(s)
    'apiKey': os.environ.get(key='NEWS_API_KEY'),
    'language': 'en',
}

# STEP 1: Use https://www.alphavantage.co
# # When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

#   - get stock prices (from api)
response = requests.get(BASE_URL, params=parameters)
response.raise_for_status()
data = response.json()

#   - print subset of response data
# print(data['Time Series (Daily)'])

#   - get yesterday's close price data
price_data_list = [price_data for date, price_data in data['Time Series (Daily)'].items()]
yesterday_price_data = price_data_list[0]
close_price_yesterday = float(yesterday_price_data['4. close'])
price_data_two_days_ago = price_data_list[1]
close_price_two_days_ago = float(price_data_two_days_ago['4. close'])


#   - find percentage difference
price_difference = abs(close_price_yesterday - close_price_two_days_ago)  # <--- learned something new; regardless of
                                                                          # the (price) difference being positive or
                                                                          # negative - the abs function will return the
                                                                          # positive equivalent/version if the price
                                                                          # difference is negative or positive
price_percentage_difference = round((price_difference / close_price_two_days_ago) * 100, 2)

# STEP 2: Use https://newsapi.org
# # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

#   - get news data (from api)
news_api_response = requests.get(NEWS_BASE_URL, params=news_endpoint_parameters)
news_api_response.raise_for_status()
news_data = news_api_response.json()

#   - get first three news pieces
first_three_news_pieces = news_data['articles'][:3:]

# STEP 3: Use https://www.twilio.com
# # Send a separate message with the percentage change and each article's title and description to your phone number.
# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file 
by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the 
coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file 
by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the 
coronavirus market crash.
"""
#   - send separate message with percentage change and each article's title and description to your phone number
emoji_to_use = ''

if ((close_price_yesterday - close_price_two_days_ago) / close_price_two_days_ago) >= PERCENTAGE_THRESHOLD:
    emoji_to_use = '🔺'
elif ((close_price_yesterday - close_price_two_days_ago) / close_price_two_days_ago) <= PERCENTAGE_THRESHOLD:
    emoji_to_use = '🔻'

if price_percentage_difference >= PERCENTAGE_THRESHOLD:
    client = Client(os.environ.get(key='TWILIO_ACCOUNT_SID'), os.environ.get(key='TWILIO_AUTH_TOKEN'))

    for article_index in range(len(first_three_news_pieces)):
        message = client.messages.create(
            body='TSLA: {emoji}{percentage}%\n'  # <--- learned something new; emojis are treated as strings in code
                 'Headline: {headline} Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?.\n'
                 'Brief: {brief}'.format(emoji=emoji_to_use,
                                         percentage=price_percentage_difference,
                                         headline=first_three_news_pieces[article_index]['title'],
                                         brief=first_three_news_pieces[article_index]['description']),
            from_='enter phone number',
            to='enter phone number'
        )

        print(message.status)
else:
    print('Don\'t check news.')
