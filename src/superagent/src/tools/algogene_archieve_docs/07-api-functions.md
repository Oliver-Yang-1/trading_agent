## API Functions

During a backtest or live trading process, you can base on the APIs below to perform on-demand request and to interact with the server resources.

  
  
  

### Place Order

Opening or closing trade orders in ALGOGENE starts from creating an object *'AlgoAPIUtil.OrderObject()'*. Then, the order will be submitted through function *'self.evt.sendOrder(orderObj)'*. The implementation can be referred to examples below. ALGOGENE support 3 types of orders.

1. market order
2. limit order
3. stop order

For market order, the following features are further supported:

- take profit
- stop loss
- holding time
- trailing stop

For limit/stop order, the following features are further supported:

- take profit
- stop loss
- holding time
- trailing stop
- time-in-force

In order to define a valid order oject, there are several elements required to be set. Below summarize all available attributes for *'AlgoAPIUtil.OrderObject()'*.

  

| 'AlgoAPIUtil.OrderObject()' ATTRIBUTE | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| instrument | Yes for open order; No for close/cancel order | string | - specify the instrument to trade - must be one of your selected symbol code - for close/cancel order, it can be omitted, and will be automatically be determined by system based on tradeID | HKXHKD |
| tradeID | No for open order; Yes for close/cancel order | int | - it can be omitted for open order, and it will be a system generated trade number for a successful executed open order - it will be a unique number for each trade - when you want to close/cancel order later, you need to submit this trade number to tell system which trade to close | 1 |
| orderRef | No | string | - set your customized order reference for a trade so that you can distinguish it from your outstanding trade pool - can be leave as empty | 1 |
| openclose | Yes | string | - specify whether the action is to open, close, or cancel an order - set value to 'open' for open order - set value to 'close' for close order - set value to 'cancel' for cancel a limit/stop order - for close order, tradeID must be existing in outstanding order pool - for cancel order, tradeID must be submitted before and its trade volume not filled yet | open |
| buysell | Yes for open order; No for close/cancel order | int | - specify whether it is to open a buy or a short sell order - set value to 1 for buy order - set value to -1 for sell order - for close/cancel order, it can be omitted and will automatically be determined by system based on tradeID | 1 |
| ordertype | Yes for open order; No for close/cancel order | int | - specify whether it is opened as a market, limit or stop order - set value to 0 for market order - set value to 1 for limit order - set value to 2 for stop order - for close order, it can be omitted and will be by default closed in market order | 1 |
| volume | Yes | float | - specify your trade volume in the number of contract - has to be positive value - fiction lot will be round to 4 decimals | 0.01 |
| price | Yes for limit/stop order; No for market order | float | - specify your desired trade price - for market order, it can be omitted and will be automatically determined by system | 25000 |
| expiry | Yes for Futures/ Options contract; No for other product type | string | - specify the expiry date for future/option contract - format in 'yyyymmdd' - leave as blank and has no effect for instrument other than options and futures |  |
| right | Yes for Options contract; No for other product type | string | - specify the call/put side for option contract - value either in \['C','P'\] - leave as blank and has no effect for non option product |  |
| strike | Yes for Options contract; No for other product type | float | - specify the strike price for option contract - leave as blank and has no effect for non option product |  |
| takeProfitLevel | No | float | - specify the level to exit a trade with profit - for limit/stop buy order, it is restricted to be at least the specifed limit/stop Price - for limit/stop sell order, it is restricted to be at most the specifed limit/stop askPrice - this feature will be disabled if not set | 25500 |
| stopLossLevel | No | float | - specify the level to exit a trade with stop loss - for limit/stop buy order, it is restricted to be at most the specified limit/stop price - for limit/stop sell order, it is restricted to be at least the specified limit/stop price - this feature will be disabled if not set | 24500 |
| trailingstop | No | float | - specify the trailing stop (in percentage) to exit a trade - this feature will be disabled if not set | 0.05 |
| holdtime | No | int | - specify how long to hold an opened order - set value in seconds - start to be effective once an order get filled - this feature will be disabled if not set | 3600 |
| timeinforce | No | int | - specify the effective time of a limit/stop order, after which the unfilled limit/stop order will be canceled by system - set value in seconds - only has impact on opening a limit/stop order - this feature will be disabled if not set | 3600 |

  
  

Here you can find some examples for taking different trade actions and submitting different orders.

1234567891011  
12345678910# ==== open a pure market buy order (modify object property) ==== def sample2(self): order = AlgoAPIUtil.OrderObject() order.instrument = 'EURUSD' order.orderRef = 123 order.openclose = 'open' order.buysell = 1 #1=buy, -1=sell order.ordertype = 0 #0=market, 1=limit, 2=stop order.volume = 0.01 self.evt.sendOrder(order)  
123456789101112  
1234567891011# ==== open a market buy order with maximum holding period feature ==== def sample4(self): order = AlgoAPIUtil.OrderObject() order.instrument = 'EURUSD' order.orderRef = 123 order.openclose = 'open' order.buysell = 1 #1=buy, -1=sell order.ordertype = 0 order.volume = 0.01 order.holdtime = 3600 #max holding time is 1 hour self.evt.sendOrder(order)  
12345678910111213# ==== open a market buy order with both take profit, stop loss, maximum holding period feature ==== def sample5(self): order = AlgoAPIUtil.OrderObject() order.instrument = 'EURUSD' order.orderRef = 123 order.openclose = 'open' order.buysell = 1 #1=buy, -1=sell order.ordertype = 0 #0=market, 1=limit, 2=stop order.volume = 0.01 order.takeProfitLevel = 1.30000 order.stopLossLevel = 1.10000 order.holdtime = 3600 self.evt.sendOrder(order)  
123456# ==== close a pure market order based on a known outstanding tradeID ==== def sample6(self): order = AlgoAPIUtil.OrderObject() order.tradeID = 1 order.openclose = 'close' self.evt.sendOrder(order)  
1234567891011# ==== open a pure limit sell order ==== def sample7(self): order = AlgoAPIUtil.OrderObject() order.instrument = 'EURUSD' order.orderRef = 123 order.openclose = 'open' order.buysell = -1 #1=buy, -1=sell order.ordertype = 1 #0=market, 1=limit, 2=stop order.volume = 0.01 order.price = 1.20000 self.evt.sendOrder(order)  
123456789101112# ==== open a limit sell order with stop loss feature ==== def sample8(self): order = AlgoAPIUtil.OrderObject() order.instrument = 'EURUSD' order.orderRef = 123 order.openclose = 'open' order.buysell = -1 #1=buy, -1=sell order.ordertype = 1 #0=market, 1=limit, 2=stop order.volume = 0.01 order.price = 1.20000 order.stopLossLevel = 1.30000 self.evt.sendOrder(order)  
123456789101112# ==== open a limit sell order with maximum holding period feature ==== def sample9(self): order = AlgoAPIUtil.OrderObject() order.instrument = 'EURUSD' order.orderRef = 123 order.openclose = 'open' order.buysell = -1 #1=buy, -1=sell order.ordertype = 1 #0=market, 1=limit, 2=stop order.volume = 0.01 order.price = 1.20000 order.holdtime = 3600 self.evt.sendOrder(order)  
1234567891011121314# ==== open a limit sell order with both take profit, stop loss, and expiry feature ==== def sample10(self): order = AlgoAPIUtil.OrderObject() order.instrument = 'EURUSD' order.orderRef = 123 order.openclose = 'open' order.buysell = -1 #1=buy, -1=sell order.ordertype = 1 #0=market, 1=limit, 2=stop order.volume = 0.01 order.price = 1.20000 order.stopLossLevel = 1.30000 order.takeProfitLevel = 1.10000 order.timeinforce = 3600 #this limit order will be expired in 1 hour self.evt.sendOrder(order)  
123456# ==== cancel an unfilled limit order based on a known outstanding tradeID ==== def sample11(self): order = AlgoAPIUtil.OrderObject() order.tradeID = 1 order.openclose = 'cancel' self.evt.sendOrder(order)  
1234567

  
  

### Debugging

During your algo development, you might probably encounter any kind of coding errors. In case of this, you will be popped with a warning or error message after submitting the script, and you can go to the 'Console' tab to look at any system generated messages.

  
![](https://algogene.com/static/image/TechDoc/tab_debug.JPG)  

On the other hand, ALGOGENE supports a Python equivalent 'print' function *'self.evt.consoleLog(msg)'* for you to debug or trouble shoot your code. The printed messages will then be printed under 'Console' tab.

  

| 'self.evt.consoleLog' arg | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| msg | \*arg | - specify any number of message object you want to view in console - output will be encoded as UTF8 string separated with comma | "Hello World!" |

  

Below is an example to demonstrate how to print the PnL result to console.

  
12def on\_dailyPLfeed(self, pl): self.evt.consoleLog("Today's PL is... ", pl)

  
  

### Query Historical Market Data

ALGOGENE provides a utility function 'self.evt.getHistoricalBar(contract, numOfBar, interval, timestamp)' to query historical market data in OHLC bar. The parameters can be referred to below.

  

| 'self.evt.getHistoricalBar' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| contract | Yes | json | - specify the financial instrument/contract - for non Future/Option contract, only "instrument" is required. - for Future contract, "instrument", "expiry" are required. - for Option contract, "instrument", "expiry", "right", "strike" are all required. - instrument have to be in your subscribed list at initial setting | {   "instrument":"HSIOPT",   "expiry":"20190830",   "right":"C",   "strike":27000   } |
| numOfBar | Yes | int | - specify the number of historical bar to be returned | 100 |
| interval | Yes | string | - specify the data interval of the historical bar - supported values include 'M','M2','M5','M10',M15','M30', 'H','H2','H3','H4','H6','H12', 'D' - 'M': 1 minute bar - 'M2': 2 minute bar - 'M5': 5 minute bar - 'M10': 10 minute bar - 'M15': 15 minute bar - 'M30': 30 minute bar - 'H': 1 hour bar - 'H2': 2 hour bar - 'H3': 3 hour bar - 'H4': 4 hour bar - 'H6': 6 hour bar - 'H12': 12 hour bar - 'D': 1 day bar | 'D' |
| timestamp | No | datetime | - specify the datetime - if this variable is not specified, default as the latest run time for backtest; or the current time stamp for real trading | datetime(2019,10,15,22,30,0) |
| chain\_dated | No | int | - this variable is for future related instruments to get the combined future chain history - value can be either of 	- 1: The closest-to-expiry (spot month) contract 	- 2: The second closest-to-expiry contract 	- 3: The third closest-to-expiry contract 	- 4: The fourth closest-to-expiry contract - Example refer to [here](https://algogene.com/community/post/46#div_comment_1) | 1 |

  
  

It should be noticed that the return might contain insufficient historical bar if the parameter 'numOfBar' is set to be too high, or it is queried during early backtest year. The returned output *'res'* is presented in JSON/ Python dictionary object. The first key will be timestamp sorted ascendingly, while the second key has below values.

| 'res\[timestamp\]' key | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the closing time of that particular bar - string format of datetime in yyyy-mm-dd hh:mm:ss | 2019-12-25 00:00:00 |
| b | float | - the closing bid price of that particular bar | 25000 |
| a | float | - the closing ask price of that particular bar | 25000 |
| m | float | - the closing mid price of that particular bar | 25005 |
| o | float | - the mid opening price of that particular bar | 24985 |
| h | float | - the highest mid price of that particular bar | 25063 |
| l | float | - the lowest mid price of that particular bar | 24906 |
| c | float | - the mid closing price of that particular bar | 25005 |
| v | float | - the trading volume of that particular bar | 100560 |

  
  

Here is an example for demonstration. Suppose we are backtesting for HKXHKD, and want to conduct a sliding window analysis by continuously querying the last 100 daily closing price.

12345678

  
  

### Query Historical News

ALGOGENE provides a utility function 'self.evt.getHistoricalNews(lang, count, starttime, endtime, category, source)' to query historical news. The parameters can be referred to below.

  

| 'self.evt.getHistoricalBar' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| lang | Yes | string | - specify the language of news - language codes follows \[ISO 639-1 codes\] ( [https://en.wikipedia.org/wiki/List\_of\_ISO\_639-1\_codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) ) - values can be either of "af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he, hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl, pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw" | en |
| count | Yes | int | - specify the number of news to be returned after 'starttime' - maximum return 100 records | 5 |
| starttime | Yes | string | - specify the start period of news - format in "YYYY-MM-DD HH:mm:SS". | 2019-03-31 03:00:00 |
| endtime | No | string | - specify the end period of news - get up-to the latest system time if left blank "". - format in "YYYY-MM-DD HH:mm:SS". | 2019-03-31 04:00:00 |
| category | No | list | - a list of filtering criteria of news category - available categories can refer to [here](https://algogene.com/#NewsDataFeed) - no category filter apply if left blank | \["ECONOMY","FINANCE"\] |
| source | No | list | - a list of filtering criteria of news source - available sources can refer to [here](https://algogene.com/#NewsDataFeed) - no source filter apply if left blank | \["BBC","CNN"\] |

  
  

The returned output *'res'* is presented in a list of news objects in JSON format with ascending timestamp. i.e. \[{'published':'t1','title':'v1',...}, {'published':'t2','title':'v2',...},...\].

| 'res\[i\]' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| published | datetime | - the timestamp of the published news - timezone is standardised into UTC+0 | 2020-04-30 23:56:26.000000 |
| source | string | - the publisher of the News - available sources can refer to [here](https://algogene.com/#NewsDataFeed) | BBC |
| category | string | - the category of the News - available category can refer to [here](https://algogene.com/#NewsDataFeed) | TOP |
| title | string | - News headlines | Coronavirus: 'We go hungry so we can feed our children' |
| authors | list | - the author(s) who wrote the News | \['Brian Wheeler', 'Political Reporter'\] |
| text | string | - the context of the News article | Image copyright Aimee Smith Image caption "I don't think I have ever set foot in a Waitrose" - Amie Smith, with her family      Many families are struggling to put food on the table as the coronavirus lockdown robs them of their income. A report by food bank charities points to an alarming rise in the number of people in need of essential supplies. How are they coping and what more can be done to help?   We have gone without meals so the children can eat. It isn't nice when you are feeling hungry and you open the cupboard and there is nothing in there for you.   Amie Smith and her partner Marcus were just about getting by before the coronavirus lockdown. Now they have had to give up their zero hours contract jobs and are relying on universal credit payments, food vouchers from the government and the occasional food parcel from local schools.   Their biggest daily struggle is finding enough food in the shops for their four children, aged two to 13.   The family is getting by on a weekly budget of about £30. The children are entitled to free school meals, which translate into food vouchers during lockdown, but they can't find anywhere to spend them. Amie says she has about £200 worth of vouchers, but they are mostly for upmarket shops like Marks & Spencer and Waitrose, which are absent from their neck of South London.   I don't think I have ever set foot in a Waitrose in my life," she said.      'Becoming expensive'   Their car has broken down, so they find themselves using local convenience stores - which charge higher prices.   It's becoming very expensive. I just paid £5 for 30 eggs. That was the cheapest we could find.   Image copyright Amie Smith Image caption Reid-Angel, two, and Bree, 11, are learning to cope with life in lockdown   Labour are calling on the government to "expand which shops are able to accept free school meal vouchers to include those supermarkets most present in our poorest communities".   Under the current scheme, run by private contractor Endenred, every eligible child is entitled to £15 a week in vouchers. The school or parent must choose a supermarket at which to redeem them, from the following list: Aldi, McColl's, Morrisons, Tesco, Sainsbury's, Asda, Waitrose and M&S.      'Tidal wave'   The government says it recognises it may not be convenient for some families to visit one of these shops. It is "working to see if additional supermarkets can be added to this list". In the meantime, it is advising schools to prepare food parcels for pupils on free meals.   Image copyright PA Media Image caption People are seeking help from food banks in record numbers   Many families - who may not have children on free school meals - are turning to food banks for essential supplies. This is putting an enormous strain on charities that provide them.   A new report by the UK's biggest food bank network, the Trussell Trust, said it handed out 81% more emergency food parcels in the last two weeks of March, than at the same time last year. People struggling with the amount of income they were receiving from working or benefits was the main reason for the increase, the trust said.   Like a tidal wave gathering pace, an economic crisis is sweeping towards us, but we don't all have lifeboats," said chief executive Emma Revie.      'Fresh faces'   Sonya Johnson, who runs Ediblelinks, an independent food bank in North Warwickshire, has noticed a big increase in families with previously comfortable incomes seeking help.   "There are fresh faces coming through the door," she said. "People who really don't want to be here, who have never used a food bank but suddenly find themselves at a point of crisis."   These new clients tend to be small business owners, or sole traders, such a hairdressers or cafe proprietors. They are waiting for universal credit payments or money from the government's business loan scheme. The food bank has seen a 20% increase in demand week-on-week since coronavirus took hold.      What can be done?   Extreme financial hardship exists even outside a global pandemic. Debt charity Christians Against Poverty says one in 10 of its clients live without a bed or mattress, or skip meals on a daily basis. It, and others in the sector, fear coronavirus will mean more people living like this - perhaps for the first time.   Payment "holidays" put off, rather than cancel, regular bills such as rent or council tax. There is concern people are simply piling up unmanageable debt for the future.   But there is support. Credit unions can offer low-cost loans for small amounts. People are also donating generously in this crisis and some of that money is given in grants so those in crippling hardship.   Charity Turn2us has a search tool to check eligibility for these non-repayable grants. The Child Poverty Action Group has also launched a tool to help people find support during the pandemic.   No government has had to cope with a crisis on this scale in peacetime and poverty campaigners have welcomed actions to help those in most need, through the benefits system. But a group of charities, including the Trussell Trust, is calling now for a coronavirus emergency income support scheme.   They say many families need money urgently, to prevent them being from being "swept into destitution".      'Grateful'   A government spokesman said it was "committed to supporting all those affected... through these unprecedented times".   "We've implemented an enormous package of measures to do so, including income protection schemes and mortgage holidays For those in most need, we've injected more than £6.5bn into the welfare system, including an increase to universal credit of up to £1,040 a year. No-one has to wait five weeks for money as urgent payments are available."   Amie and Marcus are just about managing to feed their children each day. But they are worried what the future holds, if they can't get back to work soon.   "There have been times when we have had nothing but maybe beans on toast to give them," says Amie. "We have to remind ourselves that there are people out there with absolutely nothing. We should be grateful for what we have." |
| top\_image | string | - the URL of images included in the News | https://ichef.bbci.co.uk/news/1024/branded\_news/15A87/production/\_111911788\_family.jpg |
| movies | list | - the URL(s) of video clips included in the News | \[\] |
| link | string | - the official URL of the News articles | https://www.bbc.co.uk/news/uk-politics-52455776 |
| lang | string | - the language used in the News - language codes follows \[ISO 639-1 codes\] ( [https://en.wikipedia.org/wiki/List\_of\_ISO\_639-1\_codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) ) - values can be either of "af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he, hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl, pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw" | en |

  
  

Here is an example for demonstration. Suppose we want to continuously query the latest series record every quarter.

1234567891011121314151617

  
  

### Query Economic Statistics series

ALGOGENE provides a utility function 'self.evt.getHistoricalEconstat(series\_id, starttime, endtime)' to query historical time series of Economic Statistics. The parameters can be referred to below.

  

| 'self.evt.getHistoricalBar' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| series\_id | Yes | string | - specify the ID of an Economics series - available series\_id can be found from [here](https://algogene.com/#EconsStatFeed). | CASHBLHKA188A |
| starttime | No | string | - specify the start period of an Economics series - get all the history if left blank "". | 2010-01-01 |
| endtime | No | string | - specify the end period of an Economics series - get up-to the latest system time if left blank "". | 2019-12-31 |

  
  

The returned output *'res'* is presented in a list of JSON objects where timestamp is sorted ascendingly. i.e. \[{'date':'t1','value':'v1','release\_date':'d1'}, {'date':'t2','value':'v2','release\_date':'d2'},...\].

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| date | string | - reporting date, in format of 'yyyy-mm-dd' | 2002-01-01 |
| release\_date | string | - the data's release date, in format of 'yyyy-mm-dd' | 2002-02-11 |
| value | float | - reporting value of the economic series - '.' for missing value | \-243.827856708086 |

  
  

Here is an example for demonstration. Suppose we want to continuously query the latest series record every quarter.

1234567891011121314

  
  

### Query Exchange Rate

The function 'self.evt.getExchangeRate(cur1, cur2)' is used to get the exchange rate between currencies 'cur1' and 'cur2'. The returned result represents the number of unit in 'cur2' in exchange for 1 unit of 'cur1'.

The parameters can be referred to below.

  

| 'self.evt.getExchangeRate' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| cur1 | Yes | string | - specify the currency exchange from - available currencies: 'AED', 'AMD', 'ARS', 'AUD', 'AZN', 'BDT', 'BGN', 'BHD', 'BND', 'BRL', 'CAD', 'CHF', 'CLP', 'CNH', 'CNY', 'COP', 'CZK', 'DKK', 'DZD', 'EGP', 'EUR', 'GBP', 'GEL', 'GHS', 'HKD', 'HUF', 'IDR', 'INR', 'ISK', 'JOD', 'JPY', 'KES', 'KGS', 'KRW', 'KZT', 'LBP', 'LKR', 'MAD', 'MXN', 'MYR', 'NGN', 'NOK', 'NPR', 'NZD', 'OMR', 'PHP', 'PKR', 'PLN', 'QAR', 'RON', 'RUB', 'SAR', 'SEK', 'SGD', 'SYP', 'THB', 'TJS', 'TMT', 'TND', 'TRY', 'TWD', 'UAH', 'UGX', 'UZS', 'VND', 'VUV', 'XAG', 'XOF', 'ZAR' | EUR |
| cur2 | Yes | string | - specify the currency exchange to - available currencies: 'AED', 'AMD', 'ARS', 'AUD', 'AZN', 'BDT', 'BGN', 'BHD', 'BND', 'BRL', 'CAD', 'CHF', 'CLP', 'CNH', 'CNY', 'COP', 'CZK', 'DKK', 'DZD', 'EGP', 'EUR', 'GBP', 'GEL', 'GHS', 'HKD', 'HUF', 'IDR', 'INR', 'ISK', 'JOD', 'JPY', 'KES', 'KGS', 'KRW', 'KZT', 'LBP', 'LKR', 'MAD', 'MXN', 'MYR', 'NGN', 'NOK', 'NPR', 'NZD', 'OMR', 'PHP', 'PKR', 'PLN', 'QAR', 'RON', 'RUB', 'SAR', 'SEK', 'SGD', 'SYP', 'THB', 'TJS', 'TMT', 'TND', 'TRY', 'TWD', 'UAH', 'UGX', 'UZS', 'VND', 'VUV', 'XAG', 'XOF', 'ZAR' | GBP |

  
  

For live-testing or real-trading, the result will be the latest real-time exchange rate. For backtesting, it will be the previous dayend (time zone in UTC+0) exchange rate of the query time point.

The returned output is a float type number, and it will be 0 for invalid currency pairs.

  

Here is an example for demonstration. Suppose we want to get the exchange rate for 'AUD/HKD'.

123456789101112

  
  

### Query Account Balance

Apart from the *'ab'* object in ' [on\_marketdatafeed](https://algogene.com/#StreamDataFeed) ' and ' [on\_bulkdatafeed](https://algogene.com/#bulkDataFeed) ', the function 'self.evt.getAccountBalance()' can also be used to query the current account balance.

  
  
  

The result can be accessed via *'ab'* object using a dictionary key method.

  

| 'ab' KEYS | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| realizedPL | float | - the total realized Profit and Loss of all closed trades - represented in dollar amount in base currency | 2300 |
| unrealizedPL | float | - the total unrealized Profit and Loss of all outstanding opened trades - represented in dollar amount in base currency | \-777 |
| cumDeposit | float | - the net amount of capital invested in a portfolio - represented in dollar amount in base currency | 10000 |
| NAV | float | - the latest Net Asset Value of a portfolio - represented in dollar amount in base currency - calculated as *'NAV = cumDeposit + realizedPL + unrealizedPL'* | 11523.0 |
| marginUsed | float | - the used amount of capital (in base currency) at that particular time point - represented in dollar amount in base currency | 150 |
| availableBalance | float | - the remaining account balance (in base currency) that is available to trade - represented in dollar amount in base currency - calculated as *'availableBalance = NAV - marginUsed'* | 11373 |

  
  

For example, we want to query the latest available balance right after an order status change.

123456789101112

  
  

### Query Contract Specification

The function 'self.evt.getContractSpec(instrument)' is used to get the product feature or contract specification of a financial instrument. It is particularly useful if we want to get the current tradable Options/Futures. The parameters can be referred to below.

  

| 'self.evt.getExchangeRate' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| instrument | Yes | string | - available symbol refers to [Data Source](https://algogene.com/#DataSource) section | HKXHKD |

  
  

The returned output *'res'* is presented in a JSON object, where the value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| contractSize | float | - the number of unit purchase for opening 1 lot of the contract | 100 |
| description | string | - contract description | Hong Kong HSI Stock Index |
| market | string | - the financial market of the instrument - available values: 	- COM 	- CRYPTO 	- EQ 	- ENERGY 	- FX 	- IDX 	- METAL | IDX |
| producttype | string | - the product or security type of the instrument - available values: 	- CFD 	- FUT 	- OPT 	- SPOT | CFD |
| settleCurrency | string | - the settlement currency of the contract | HKD |
| minTick | float | - the minimum level of price changes | 0.01 |
| chain | array | - it will be an empty list for non future/option contract - for 'FUT' or 'OPT', it will be a list of JSON, eg. \[{"expiry":expiry,"right":right,"strike":strike},...\] 	- 'expiry': the expiry date in string format of 'yyyymmdd' 	- 'right': 		- for non 'OPT' contract, value is "" 		- for 'OPT' contract, value is either 'C' for call or 'P' for put option 	- 'strike': 		- for non 'OPT' contract, value is 0 		- for 'OPT' contract, it is the option strike price in float data type - for 'FUT' or 'OPT', it only returns the tradable contracts as at the query time point | \[\] |

  
  

Here is an example for demonstration. Suppose we want to check the contract size for all our selected instruments.

1234567891011121314

  
  

### Query Orders and Positions

The function 'self.evt.getSystemOrders()' is used to get:

- current positions (pos),
- outstanding opened orders (osOrder),
- limit/stop orders that are pending to fill (pendOrder)
  
  

There will be 3 returned results which are similar to that in this [section](https://algogene.com/#Position). They are all in JSON objects which can be accessed via a dictionary key method.

For 'pos', the first key will be the financial symbol while the second key has below values.

| 'pos\[symbol\]' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| LastTradeTime | datetime | - the last traded time of this symbol - time zone in UTC+0 | 2021-02-20 00:04:30.230000 |
| netVolume | float | - the net amount of outstanding number of contract - positive for net long position, while negative for net short position | 0.01 |

  
  

Suppose we want to get our outstanding position every hour.

1234567891011121314  
  

Secondly, for 'osOrder', the first key will be a system generated 'tradeID' while the second key has below values.

| 'osOrder\[tradeID\]' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| orderRef | string | - the order reference you specified previously at trade opening | 1 |
| market | string | - the market of this trade | EQ |
| broker | string | - the counterparty of this trade | DMA |
| producttype | string | - the product type of this trade | SPOT |
| instrument | string | - the instrument name of this trade | HKXHKD |
| symbol | string | - the symbol name of the instrument - for future contract, value will be concat with 'instrument'+'expiry' - for option contract, value will be concat with 'instrument'+'expiry'+'right'+'strike' - for non option/future contract, symbol name will has the same value to instrument name | HKXHKD |
| expiry | string | - the expiry date for the executed future/option contract, with format in 'yyyymmdd' - value is empty for instrument other than options and futures |  |
| right | string | - the call/put side for the executed option contract - value wiil be 'C' for call option - value wiil be 'P' for put option - value is empty for non option product |  |
| strike | float | - the strike price for the executed option contract - value is zero for non option product | 0 |
| buysell | int | - value = 1 for buy order - value = -1 for sell order | 1 |
| opentime | datetime | - the timestamp to open this trade | 2018-01-05 14:01:10.932000 |
| openprice | float | - the execution price to open this trade | 30100.6 |
| Volume | float | - the execution volume to open this trade | 5 |
| takeProfitLevel | float | - the take profit level you specified when opening this trade - Display as 0 if not set | 0 |
| stopLossLevel | float | - the stop loss level you specified when opening this trade - Default as 0 if not set | 0 |
| trailingstop | float | - the trailing stop (in percentage) you specified when opening this trade - Default as 0 if not set | 0.05 |
| timeinforce | float | - the effective time of a limit/stop order, after which the unfilled limit/stop order will be canceled by system - Display as 0 if not set | 0 |
| holdtime | float | - the maximum holding time you specified when opening this trade - Display as 0 if not set | 0 |

  
  

Suppose we want to get our outstanding orders every hour.

1234567891011121314  
  

Lastly and similarly, the full list of unfilled limit/stop order 'pendOrder' object can be accessed through a dictionary key method. The first key for *'pendOrder'* is a system generated tradeID, while the second key for *'pendOrder\[tradeID\]'* has the following attributes.

| 'pendOrder\[tradeID\]' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| orderRef | string | - the order reference you specified previously at limit/stop trade opening | 1 |
| market | string | - the market of this limit/stop order | EQ |
| broker | string | - the counterparty of this limit/stop order | DMA |
| producttype | string | - the product type of this limit/stop order | SPOT |
| instrument | string | - the instrument name of this limit/stop order | HKXHKD |
| symbol | string | - the symbol name of the instrument - for future contract, value will be concat with 'instrument'+'expiry' - for option contract, value will be concat with 'instrument'+'expiry'+'right'+'strike' - for non option/future contract, symbol name will has the same value to instrument name | HKXHKD |
| expiry | string | - the expiry date for the pending future/option order, with format in 'yyyymmdd' - value is empty for instrument other than options and futures |  |
| right | string | - the call/put side for the pending option order - value wiil be 'C' for call option - value wiil be 'P' for put option - value is empty for non option product |  |
| strike | float | - the strike price for the pending option order - value is zero for non option product | 0 |
| buysell | int | - value = 1 for this pending buy order - value = -1 for this pending sell order | 1 |
| opentime | datetime | - the timestamp to submit this limit/stop order | 2018-01-05 14:01:10.932000 |
| openprice | float | - the desired price to open this limit/stop order | 30100.6 |
| Volume | float | - the desired volume to open this limit/stop order | 5 |
| takeProfitLevel | float | - the take profit level you specified when opening this limit/stop order - Default as 0 if not set | 0 |
| stopLossLevel | float | - the stop loss level you specified when opening this limit/stop order - Default as 0 if not set | 0 |
| trailingstop | float | - the trailing stop (in percentage) you specified when opening this limit/stop order - Default as 0 if not set | 0.05 |
| timeinforce | float | - the effective time of a limit/stop order, after which the unfilled limit/stop order will be canceled by system - Default as 0 if not set | 0 |
| holdtime | float | - the maximum holding time you specified when opening this limit/stop order - Default as 0 if not set | 0 |

  
  

Suppose we want to get our unfilled limit/stop orders every hour.

1234567891011121314

  
  

### Query Corporate Action

For stock market, a corporate action is an event carried out by a company that materially impacts its stakeholders. These actions include the payment of dividends, stock split, mergers and acquisitions. The function 'self.evt.getHistoricalCorpAction(...)' can be used to query corporate actions filtered by its announcement date. The parameters can be referred to below.

| 'self.evt.getHistoricalCorpAction' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| symbol | Yes | string | - the financial symbol | 00005HK |
| starttime | No | datetime | - the earliest annoucement date, format in 'YYYY-MM-DD' - will return all the corporate action history if omitted this parameter | '2019-01-01' |
| endtime | No | datetime | - the latest annoucement date, format in 'YYYY-MM-DD' - will return all the corporate action history up to the current time if omitted this parameter | '' |
| event | No | string | - filter the type of corporate event, available input: - - ' **dividend** ': cash dividend, bonus 	- ' **splits** ': stock split, reverse split, stock dividend | dividend |

  
  

The returned output *'res'* will be a list of JSON object, where the value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| event | string | - specify the event type of corporate action - value can either be 'dividend', 'splits' | dividend |
| announce\_date | datetime | - the announcement date of the corporate action | 2019-05-04 |
| ex\_date | datetime | - the ex-dividend date where you will be eligible to receive dividends as long as you hold shares on that date | 2019-05-17 |
| payable\_date | datetime | - the date for dividend payment - this attribute is only available for event='dividend' | 2018-07-05 |
| dividend\_amt | float | - the dividend amount - this attribute is only available for event='dividend' | 0.1 |
| is\_special | string | - available for evt='' - specify whether it is a normal or special dividend - value can either be 'T' or 'F' - this attribute is only available for event='dividend' | F |
| splits | float | - the share split ratio - for example 	- if value=3, it means that for each 1 original share, it will split into 3 shares 	- if value=0.2, it means that original 1 share will become 0.2 shares. In other word, for each 5 original shares, it will merge into 1 share - this attribute is only available for event='splits' | 3.0 |

  
  

Suppose we want to query the corporate action data every day.

1234567891011121314

  
  

### Update Opened Order

The function 'self.evt.update\_opened\_order(...)' is used to update the attached parameters of an opened order. The parameters can be referred to below.

| 'self.evt.update\_opened\_order' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| tradeID | Yes | string | - the unique system tradeID to identify the order to be updated - 'tradeID' can be obtained from [on\_orderfeed](https://algogene.com/#OrderFeed), or [getSystemOrders](https://algogene.com/#QueryServerOrder) | 5 |
| tp | No | float | - update the take profit level of an order | 150 |
| sl | No | float | - update the stop loss level of an order | 100 |
| holdtime | No | int | - update the holding time of an order - unit in second, and counted from order opening time | 3600 |
| orderRef | No | string | - update the user-specified order reference | abc |

  
  

The returned output *'res'* is presented in a JSON object, where the value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| status | bool | - specify whether the update is successful or not - True for successfully update - False for error in update | True |
| msg | string | - description of error message, or detail of updates | New settings applied to opened order tradeID=5... tp=150, sl=100, |

  
  

Suppose we want to update the take profit level when a previously submitted limit order get filled.

1234567891011121314

  
  

### Update Pending Order

Similarly, the function 'self.evt.update\_pending\_order(...)' is used to update the attached parameters of a limit/stop order that is pending to fill. The parameters can be referred to below.

| 'self.evt.update\_pending\_order' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| tradeID | Yes | string | - the unique system tradeID to identify the order to be updated - 'tradeID' can be obtained from [on\_orderfeed](https://algogene.com/#OrderFeed), or [getSystemOrders](https://algogene.com/#QueryServerOrder) | 123 |
| price | No | float | - update the limit/stop price or pending entry level | 105 |
| tp | No | float | - update the take profit level of a limit/stop order when such limit/stop order get filled | 150 |
| sl | No | float | - update the stop loss level of a limit/stop order when such limit/stop order get filled | 100 |
| timeinforce | No | int | - update the the effective time of a limit/stop order, after which the unfilled limit/stop order will be canceled by system - unit in second, and counted from the original time at limit/stop order submission | 600 |
| holdtime | No | int | - update the holding time of a limit/stop order - unit in second, and counted from the opening time at limit/stop order filled | 3600 |
| orderRef | No | string | - update the user-specified order reference | abc |

  
  

The returned output *'res'* is presented in a JSON object, where the value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| status | bool | - specify whether the update is successful or not - True for successfully update - False for error in update | False |
| msg | string | - description of error message, or detail of updates | Unable to update pending order as tradeID=123 not found! |

  
  

Suppose we want to adjust the entry level (limit/stop price) of all unfilled limit/stop orders every day.

1234567891011121314151617181920

  
  

### Update Portfolio Stoploss

The function 'self.evt.update\_portfolio\_sl(...)' is used to set the portfolio level stop loss (in percentage). When the account NAV drops for such percentage from its previous high water level, the system will auto close all the outstanding orders and cancel all unfilled limit/stop orders. The parameters can be referred to below.

| 'self.evt.update\_portfolio\_sl' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| sl | Yes | float | - the stoploss (in percentage) from a portfolio NAV's high water mark - value between 0 to 1. eg. 0.1 refers to cutting all positions when a portfolio NAV drops 10% from its previous highest level. - set the value to 0 to disable this feature - once this stoploss condition trigger, the high water level will be reset to the latest NAV | 0.1 |
| resume\_after | No | float | - when the portfolio stoploss event trigger, this parameter refers to the "cooling period" before resuming the algo - unit in second, and default is 0 | 60\*60\*24 |

  
  

Suppose we want to set a global stoploss level for the whole portfolio to 10%, and also pause the algo submitting new trades for 1 week if such stop loss event happen. We can then apply this setup at initialization step at 'def start'.

Additionally, the function 'update\_portfolio\_sl' can be called in other datafeed events, if we target for a dynamic portfolio stoploss at different time points.

12345678910

  
  

### Update Risk Limit - Stoploss

The function 'self.evt.update\_risk\_limit\_sl(...)' is used to set the risk limit for stop loss (in percentage).

- Daily stop loss
- Weekly stop loss
- Monthly stop loss
- Quarterly stop loss
- Yearly stop loss

When the account NAV drops for such percentage from its period start level, the system will auto close all the outstanding orders and cancel all unfilled limit/stop orders. For example, if the risk limit for a monthly stop loss is triggered, all your orders will be closed/canceled, and you will not be able to place new orders until the next month starts.

The input parameters can be referred to below.

| 'self.evt.update\_risk\_limit\_sl' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| sl | Yes | float | - the stoploss (in percentage) from the portfolio NAV at a period start - value between 0 to 1. eg. 0.1 refers to cutting all positions when a portfolio NAV drops 10% from its previous highest level. - set the value to 0 to disable this feature - once this stoploss condition trigger, the high water level will be reset to the latest NAV | 0.1 |
| risk\_type | Yes | string | - set the risk limit type - 'd' for daily stop loss limit - 'w' for weekly stop loss limit - 'm' for monthly stop loss limit - 'q' for quarterly stop loss limit - 'y' for yearly stop loss limit | 'm' |

  
  

Suppose we want to set a monthly stop loss and yearly stop loss to 5% and 10% respectively. We can then apply this setup at initialization step at 'def start'.

Additionally, the function 'update\_risk\_limit\_sl' can be called in other datafeed events, if we target for a dynamic stoploss risk limit at different time points.

1234567891011

  
  

### Query HKEx CCASS History

The function 'self.evt.getCCASSHistory(...)' is used to query HKEx CCASS's shareholding information.

The table below is the participating company/person registered on CCASS.

  
  

The parameters to call this API can be referred to below.

| 'self.evt.getCCASSHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| symbol | No | string | - specify the stock symbol to search - either 'symbol' or 'participant\_id' is required | 00001HK |
| participant\_id | No | string | - specify the CCASS's participant ID to search - either 'symbol' or 'participant\_id' is required |  |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | 2023-01-16 |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - an empty value or future date value will assume to be the current date | 2023-01-17 |

  
  

The returned output *'res'* is presented in a JSON object, where the value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the reported shareholding date | 2023-01-17 |
| symbol | string | - the corresponding stock symbol | 00001HK |
| id | string | - CCASS's participant ID | C00033 |
| type | string | - shareholder type - value can either be 'institution' or 'individual' - 'institution' refers to any registered participating companies on CCASS, otherwise it will be classified as invidiual | institution |
| share | float | - the number of shares held by the reported participant | 75197956 |
| pct | float | - the shareholding in percentage with rounding in 2 decimals. eg. value 1 means 1% of total issued shares | 1.96 |

  
  

Suppose we want to query the percentage of shares held by institutional investors for HSBC (i.e. 00005HK) on a daily basis.

123456789101112131415161718192021

  
  

### Query Index Constituents

The function 'self.evt.getIndexComposite(...)' is used to query the stock constituents of an index on a particular day.

The parameters to call this API can be referred to below.

| 'self.evt.getIndexComposite' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| index | No | string | - specify the index name under the specified exchange - supported values 'DOWJONES', 'HSI', 'NASDAQ100', 'SP500' | HSI |
| date | Yes | datetime | - specify the date of search result, format in 'YYYY-MM-DD' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | 2023-12-08 |

  
  

The returned output *'res'* is presented in a list of.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| symbol | string | - stock symbol | 00005HK |
| weight | float | - the weighting of market capitalization toward the index | 0.0856 |
| sensitivity | float | - the number of index point changes due to 1 dollar change in the stock price | 1.1652 |

  
  

Suppose we want to query the stock weights of HSBC (i.e. 00005HK) towards HSI on a daily basis.

1234567891011121314151617181920

  
  

