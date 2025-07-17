## Data Stream

  

After initializing the set up for backtest environment, you are now prepared to get into the core part to code up your strategy. ALGOGENE event handlers are basically server-client callback functions, where your client script will receive messages whenever there is new event update.

  
  

### Stream Market Data Feed

The API function *'on\_marketdatafeed'* allows you to get price, volume, sensitivity, and order book data for the subscripted instruments. This API is a First-In-First-Out (FIFO) data stream that pop out market data in the sequence of time. It is particularly useful for tick data simulation. You can access the market data from *'md'* object as below.

Besides, whenever there is market data update, the latest account balance can be retrieved from object *'ab'*.

  
12345def on\_marketdatafeed(self, md, ab): instrument = md.instrument timestamp = md.timestamp lastPrice = md.lastPrice NAV = ab\['NAV'\]  
  

Here is the full set of attributes that can be accessed from *'md'*.

  

| 'md' ATTRIBUTE | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| instrument | string | - the instrument name of a subscripted data stream | HKXHKD |
| expiry | string | - the expiry date of the future/option contract, in format of 'yyyymmdd' - value will be empty for non option/future contract |  |
| right | string | - the call/put side of option contract, value either in \['C', 'P'\] - value will be empty for non option contract |  |
| strike | float | - the strike price of option contract - value will be zero for non option contract | 0 |
| minTick | float | - the minimum level of price changes | 0.01 |
| symbol | string | - the symbol name of the instrument - for future contract, value will be concat with 'instrument'+'expiry' - for option contract, value will be concat with 'instrument'+'expiry'+'right'+'strike' - for non option/future contract, symbol name will has the same value to instrument name | HKXHKD |
| timestamp | datetime | - represents the historical timestamp for that particular stream - for non-tick dataset, it represents the closing time for that particular OHLC bar | 2018-01-05 14:01:10.932000 |
| bidPrice | float | - the best price you can sell to market at that particular time point | 27800.5 |
| askPrice | float | - the best price you can buy from market at that particular time point | 27810.3 |
| midPrice | float | - calculated as (bidPrice+askPrice)/2 | 27805.4 |
| openPrice | float | - represents the opening price within a specified data bar - in case of full tick, it will equal to midPrice | 27801 |
| highPrice | float | - represents the highest price within a specified data bar - in case of full tick, it will equal to midPrice | 27850.5 |
| lowPrice | float | - represents the lowest price within a specified data bar - in case of full tick, it will equal to midPrice | 27780.9 |
| lastPrice | float | - represents the last closing price for a specified data bar - in case of full tick, it will equal to midPrice | 27805.4 |
| volume | int | - represents the number of market trades for a specified data bar - in case of full tick, it will equal to 1 | 123 |
| bidSize | float | - the availale trading volume at current bid price | 10000 |
| askSize | float | - the availale trading volume at current ask price | 10000 |
| bidOrderBook | list of list | - represent the current bid order book - the sub-list refers to a pair of \['price', 'volume'\] - sorted in ascending of best bid - only available under full tick environment | ```js [     [27800, 500],     [27790, 500],      [27780, 1000],      [27750, 1600] ] ``` |
| askOrderBook | list of list | - represent the current ask order book - the sub-list refers to a pair of \['price', 'volume'\] - sorted in ascending of best ask - only available under full tick environment | ```js [     [27815, 200],     [27820, 1000],      [27835, 800],      [27840, 700],      [27860, 1700] ] ``` |
| session | int | - the type of market session - 0: continous trading session - 1: pre-opening session - 2: after-close session | 0 |

  
  

On the other hand, the details of Account balance can be accessed via *'ab'* object using dictionary key method.

  

| 'ab' KEYS | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| realizedPL | float | - the total realized Profit and Loss of all closed trades - represented in dollar amount in base currency | 2300 |
| unrealizedPL | float | - the total unrealized Profit and Loss of all outstanding opened trades - represented in dollar amount in base currency | \-777 |
| cumDeposit | float | - the net amount of capital invested in a portfolio - represented in dollar amount in base currency | 10000 |
| NAV | float | - the latest Net Asset Value of a portfolio - represented in dollar amount in base currency - calculated as *'NAV = cumDeposit + realizedPL + unrealizedPL'* | 11523.0 |
| marginUsed | float | - the used amount of capital (in base currency) at that particular time point - represented in dollar amount in base currency | 150 |
| availableBalance | float | - the remaining account balance (in base currency) that is available to trade - represented in dollar amount in base currency - calculated as *'availableBalance = NAV - marginUsed'* | 11373 |

  
  

### Bulk Data Feed

There is another way to assess market data via *'on\_bulkdatafeed'*. From this function, all your subscripted instrument(s) will be presented in a JSON/ Python dictionary object *'bd'*, and you can extract all of their latest images at the same time. It is particularly useful for non-tick data simulation or cross assets strategy development.

Similarly, you can obtain the latest account balance of your portfolio from object *'ab'*, which have exactly the same data structure defined above.

In the following example, suppose you have subscripted 2 instruments (eg. USDJPY, EURUSD), and you want to extract their latest data image in the mean time. You can do something like.

  
1234567891011def on\_bulkdatafeed(self, isSync, bd, ab): p1 = 'USDJPY' instrument\_p1 = bd\[p1\]\['instrument'\] timestamp\_p1 = bd\[p1\]\['timestamp'\] lastPrice\_p1 = bd\[p1\]\['lastPrice'\] p2 = 'EURUSD' instrument\_p2 = bd\[p2\]\['instrument'\] timestamp\_p2 = bd\[p2\]\['timestamp'\] lastPrice\_p2 = bd\[p2\]\['lastPrice'\] isAllDataBarSync = isSync NAV = ab\['NAV'\]  
  

*'on\_bulkdatafeed'* has very similar attributes as *'on\_marketdatafeed'*, except that it has to be assessed with a directory key method. The first key for *'bd'* is your subscripted symbol, while the second key for *'bd\[your\_symbol\]'* has the following attributes.

  

| 'bd\[your\_symbol\]' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| instrument | string | - the symbol of your subscripted instrument(s) | HKXHKD |
| expiry | string | - the expiry date of the future/option contract, in format of 'yyyymmdd' - value will be empty for non option/future contract |  |
| right | string | - the call/put side of option contract, value either in \['C', 'P'\] - value will be empty for non option contract |  |
| strike | float | - the strike price of option contract - value will be zero for non option contract | 0 |
| minTick | float | - the minimum level of price changes | 0.01 |
| symbol | string | - the symbol name of the instrument - for future contract, value will be concat with 'instrument'+'expiry' - for option contract, value will be concat with 'instrument'+'expiry'+'right'+'strike' - for non option/future contract, symbol name will has the same value to instrument name | HKXHKD |
| timestamp | datetime | - represents the last trade timestamp for *your\_symbol* - for non-tick dataset, it represents the closing time for that particular OHLC bar | 2018-01-05 14:01:10.932000 |
| bidPrice | float | - the best price you can sell to market at that particular time point for *your\_symbol* | 27800.5 |
| askPrice | float | - the best price you can buy from market at that particular time point for *your\_symbol* | 27810.3 |
| midPrice | float | - calculated as (bidPrice+askPrice)/2 | 27805.4 |
| openPrice | float | - represents the opening mid price within a specified data bar for *your\_symbol* - in case of full tick, it will equal to midPrice | 27800 |
| highPrice | float | - represents the highest mid price within a specified data bar for *your\_symbol* - in case of full tick, it will equal to midPrice | 27850.5 |
| lowPrice | float | - represents the lowest mid price within a specified data bar for *your\_symbol* - in case of full tick, it will equal to midPrice | 27780.9 |
| lastPrice | float | - represents the last closing mid price for a specified data bar for *your\_symbol* - in case of full tick, it will equal to midPrice | 27805.4 |
| volume | int | - represents the number of market trades for a specified data bar - in case of full tick, it will equal to 1 | 123 |
| bidSize | float | - the availale trading volume at current bid price | 10000 |
| askSize | float | - the availale trading volume at current ask price | 10000 |
| bidOrderBook | list of list | - represent the current bid order book - the sub-list refers to a pair of \['price', 'volume'\] - sorted in ascending of best bid - only available under full tick environment | ```js [     [27800, 500],     [27790, 500],      [27780, 1000],      [27750, 1600] ] ``` |
| askOrderBook | list of list | - represent the current ask order book - the sub-list refers to a pair of \['price', 'volume'\] - sorted in ascending of best ask - only available under full tick environment | ```js [     [27815, 200],     [27820, 1000],      [27835, 800],      [27840, 700],      [27860, 1700] ] ``` |
| session | int | - the type of market session - 0: continous trading session - 1: pre-opening session - 2: after-close session | 0 |

  

More importantly, for muliple instrument subscription under non tick data environment (say 1 hour bar), it is common that different instruments may have different trading hours. To check whether the market datasets for all instruments are aligned or updated to the same OHLC bar, it can be refered to 'isSync' where TRUE means all the subscripted instruments have been updated to the same time horizon.

  
  

### News Data Feed

ALGOGENE News database is sourced from 200+ different channels globally, including BBC, CNN, Reuters, etc. The news context also covers various languages in English, Chinese, Japenese, Korean, French, German, etc. These provide a strong fundation for trading strategy development in Natural Langauge Processing (NPL).

News event data can be accessed via callback function *'on\_newsdatafeed'*. Below example shows you how to get each received news headline and print the result to console.

  
123def on\_newsdatafeed(self, nd): title = nd.title self.evt.consoleLog(title)  

All other available attibutes can be referred to below.

  

| 'nd' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| published | datetime | - the timestamp of the published news - timezone is standardised into UTC+0 | 2020-04-30 23:56:26.000000 |
| source | string | - the publisher of the News - source values include 'APPLE\_DAILY', 'AsahiNews', 'BBC', 'CHINADAILYHK', 'CHOSUM', 'CNN', 'CUP', 'DW\_NEWS', 'ENGADGET', 'ETNET', 'FACEBOOK', 'GOOGLE', 'GOV.HK', 'GRASSMEDIACTION', 'HKET', 'HKEX', 'HKFP', 'HORBOURTIMES', 'InsiderInsight', 'JTBC', 'JapanIndustryNews', 'KBS', 'KINLIU', 'KyodoNews', 'LOCALPRESSHK', 'LivedoorNews', 'MADDOG', 'MARKETWATCH', 'MASTER-INSIGHT', 'MINGPAO', 'MSN', 'NDTV', 'NHK', 'NYTIMES', 'NipponNews', 'OILPRICE', 'ORIENTAL\_DAILY', 'PMNEWS', 'PeopleDaily', 'REUTERS', 'RFA', 'RTHK', 'SUPERMEDIA', 'SYMEDIALAB', 'SoraNews', 'TRT', 'TheNewsLensHK', 'UDN', 'VOACANTONESE', 'WallStreetJournal', 'YAHOO', 'Yonhap', 'aamacau', 'bastillepost', 'benzinga', 'feedburner', 'feedx', 'heraldcorp', 'hkcnews', 'hkjam', 'inmediahk', 'japaninsides', 'japantimes', 'japantoday', 'koreaherald', 'koreatimes', 'litenews', 'localpresshk', 'mcnews', 'memehk', 'newsonjapan', 'nytimes', 'pentoy', 'philstar', 'polymerhk', 'post852', 'scmp', 'thebridge', 'theinitium', 'thejapannews', 'thestandnews', 'tmhk', 'tokyoreporter', 'voachinese', 'yahoo', 'zakzak', 'zhihu' | BBC |
| category | string | - the category of the News - category values include 'AFRICA', 'AGRICULTURE', 'AMERICAS', 'ART', 'ASIA', 'ASSET\_SALES', 'AUSTRALIA', 'AUTO', 'BIOTECH', 'BOND', 'BOOK', 'BOTsWANA', 'BUSINESS', 'BUYBACK', 'CANADA', 'CENTRAL\_ASIA', 'CHINA', 'COMMENTARY', 'COMMODITY', 'COMMUNITY', 'COMPANY', 'COMPANY NEWS', 'CONTRACT', 'CULTURE', 'DIPLOMACY', 'DIVIDENDS', 'EARNINGS', 'EAST\_ASIA', 'ECONOMY', 'EDUCATION', 'EMERGING\_MARKET', 'ENERGY', 'ENTERTAINMENT', 'ENVIRONMENT', 'ETF', 'ETHIOPIA', 'EUROPE', 'EVENT', 'FASHION', 'FDA', 'FEDERAL\_RESERVE', 'FINANCE', 'FINANCING', 'FINTECH', 'FOREX', 'FORUM', 'FRANCE', 'FUND', 'FUTURE', 'GENERAL', 'GEOPOLITICS', 'GERMANY', 'GHANA', 'HEALTH', 'HEIDI', 'HISTORY', 'HONG KONG', 'HOT', 'HOUSE', 'INDIA', 'INDONESIA', 'INSIDER\_TRADE', 'INTERNET', 'INTERVIEW', 'IPO', 'IRELAND', 'ISRAEL', 'ITALIA', 'JAPAN', 'KENYA', 'KOREA', 'LATIN\_AMERICA', 'LATVIA', 'LAW', 'LEGAL', 'LIFESTYLE', 'LOGISTICS', 'M&A', 'MALAYSIA', 'MANAGEMENT', 'MEDIA', 'MIDDLE\_EAST', 'MILITARY', 'MONEY', 'MOVIES', 'NAMIBIA', 'NATION', 'NEW\_ZEALAND', 'NIGERIA', 'NORTH\_KOREA', 'OFFERING', 'OPINION', 'OPTION', 'PAKISTAN', 'PEOPLE', 'PETS', 'PHILIPPINES', 'PICTURES', 'POLITICS', 'POLLS', 'POSTAL', 'PRESS', 'RATING', 'REAL\_ESTATE', 'REAL\_TIME', 'REGION', 'RESEARCH', 'RETAIL\_SALES', 'REVIEW', 'RUMORS', 'RUSSIA', 'SCIENCE', 'SINGAPORE', 'SMALL\_CAP', 'SOCIALS', 'SOUTHEAST\_ASIA', 'SOUTH\_AFRICA', 'SOUTH\_ASIA', 'SPEECH', 'SPORT', 'SPORT\_BOXING', 'SPORT\_GOLF', 'SPORT\_RACING', 'SPORT\_RUGBY', 'SPORT\_SOCCER', 'SPORT\_TENNIS', 'STATISITCS', 'STOCK', 'STOCK\_SPLIT', 'STORY', 'TAIWAN', 'TANZANIA', 'TECHNOLOGY', 'TELECOMS', 'TOP', 'TOURISM', 'TRAFFIC', 'TRAVEL', 'TURKEY', 'UGANDA', 'UK', 'US', 'USA', 'WEATHER', 'WORLD', 'ZIMBABWE' | TOP |
| title | string | - News headlines | Coronavirus: 'We go hungry so we can feed our children' |
| authors | list | - the author(s) who wrote the News | \['Brian Wheeler', 'Political Reporter'\] |
| text | string | - the context of the News article | Image copyright Aimee Smith Image caption "I don't think I have ever set foot in a Waitrose" - Amie Smith, with her family      Many families are struggling to put food on the table as the coronavirus lockdown robs them of their income. A report by food bank charities points to an alarming rise in the number of people in need of essential supplies. How are they coping and what more can be done to help?   We have gone without meals so the children can eat. It isn't nice when you are feeling hungry and you open the cupboard and there is nothing in there for you.   Amie Smith and her partner Marcus were just about getting by before the coronavirus lockdown. Now they have had to give up their zero hours contract jobs and are relying on universal credit payments, food vouchers from the government and the occasional food parcel from local schools.   Their biggest daily struggle is finding enough food in the shops for their four children, aged two to 13.   The family is getting by on a weekly budget of about £30. The children are entitled to free school meals, which translate into food vouchers during lockdown, but they can't find anywhere to spend them. Amie says she has about £200 worth of vouchers, but they are mostly for upmarket shops like Marks & Spencer and Waitrose, which are absent from their neck of South London.   I don't think I have ever set foot in a Waitrose in my life," she said.      'Becoming expensive'   Their car has broken down, so they find themselves using local convenience stores - which charge higher prices.   It's becoming very expensive. I just paid £5 for 30 eggs. That was the cheapest we could find.   Image copyright Amie Smith Image caption Reid-Angel, two, and Bree, 11, are learning to cope with life in lockdown   Labour are calling on the government to "expand which shops are able to accept free school meal vouchers to include those supermarkets most present in our poorest communities".   Under the current scheme, run by private contractor Endenred, every eligible child is entitled to £15 a week in vouchers. The school or parent must choose a supermarket at which to redeem them, from the following list: Aldi, McColl's, Morrisons, Tesco, Sainsbury's, Asda, Waitrose and M&S.      'Tidal wave'   The government says it recognises it may not be convenient for some families to visit one of these shops. It is "working to see if additional supermarkets can be added to this list". In the meantime, it is advising schools to prepare food parcels for pupils on free meals.   Image copyright PA Media Image caption People are seeking help from food banks in record numbers   Many families - who may not have children on free school meals - are turning to food banks for essential supplies. This is putting an enormous strain on charities that provide them.   A new report by the UK's biggest food bank network, the Trussell Trust, said it handed out 81% more emergency food parcels in the last two weeks of March, than at the same time last year. People struggling with the amount of income they were receiving from working or benefits was the main reason for the increase, the trust said.   Like a tidal wave gathering pace, an economic crisis is sweeping towards us, but we don't all have lifeboats," said chief executive Emma Revie.      'Fresh faces'   Sonya Johnson, who runs Ediblelinks, an independent food bank in North Warwickshire, has noticed a big increase in families with previously comfortable incomes seeking help.   "There are fresh faces coming through the door," she said. "People who really don't want to be here, who have never used a food bank but suddenly find themselves at a point of crisis."   These new clients tend to be small business owners, or sole traders, such a hairdressers or cafe proprietors. They are waiting for universal credit payments or money from the government's business loan scheme. The food bank has seen a 20% increase in demand week-on-week since coronavirus took hold.      What can be done?   Extreme financial hardship exists even outside a global pandemic. Debt charity Christians Against Poverty says one in 10 of its clients live without a bed or mattress, or skip meals on a daily basis. It, and others in the sector, fear coronavirus will mean more people living like this - perhaps for the first time.   Payment "holidays" put off, rather than cancel, regular bills such as rent or council tax. There is concern people are simply piling up unmanageable debt for the future.   But there is support. Credit unions can offer low-cost loans for small amounts. People are also donating generously in this crisis and some of that money is given in grants so those in crippling hardship.   Charity Turn2us has a search tool to check eligibility for these non-repayable grants. The Child Poverty Action Group has also launched a tool to help people find support during the pandemic.   No government has had to cope with a crisis on this scale in peacetime and poverty campaigners have welcomed actions to help those in most need, through the benefits system. But a group of charities, including the Trussell Trust, is calling now for a coronavirus emergency income support scheme.   They say many families need money urgently, to prevent them being from being "swept into destitution".      'Grateful'   A government spokesman said it was "committed to supporting all those affected... through these unprecedented times".   "We've implemented an enormous package of measures to do so, including income protection schemes and mortgage holidays For those in most need, we've injected more than £6.5bn into the welfare system, including an increase to universal credit of up to £1,040 a year. No-one has to wait five weeks for money as urgent payments are available."   Amie and Marcus are just about managing to feed their children each day. But they are worried what the future holds, if they can't get back to work soon.   "There have been times when we have had nothing but maybe beans on toast to give them," says Amie. "We have to remind ourselves that there are people out there with absolutely nothing. We should be grateful for what we have." |
| top\_image | string | - the URL of images included in the News | https://ichef.bbci.co.uk/news/1024/branded\_news/15A87/production/\_111911788\_family.jpg |
| movies | list | - the URL(s) of video clips included in the News | \[\] |
| link | string | - the official URL of the News articles | https://www.bbc.co.uk/news/uk-politics-52455776 |
| lang | string | - the language used in the News - language codes follows \[ISO 639-1 codes\] ( [https://en.wikipedia.org/wiki/List\_of\_ISO\_639-1\_codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) ) - values can be either of "af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he, hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl, pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw" | en |

  
  

### Weather Data Feed

ALGOGENE weather database collected real-time weather details from over 200+ cities and regions globally.

Weather event data can be accessed via callback function *'on\_weatherdatafeed'*. The details can be accessed via a JSON/ dictionary-key methods. Below example shows you how to get each received city and temperature and print the result to console.

  
12345def on\_weatherdatafeed(self, wd): city = wd.city temp = wd.temperature msg = vars(wd) self.evt.consoleLog(msg)  

All other available attibutes can be referred to below.

  

| 'wd' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| timestamp | datetime | - the recorded timestamp of the weather event - timezone is standardised into UTC+0 | 2020-01-26 12:22:41.000000 |
| city | string | - the city/region of the weather event - values include 'Baghdad', 'Bangkok', 'Beijing', 'Berlin', 'Bloemfontein', 'Boston', 'Brasilia', 'Cairo', 'Cape Town', 'Chengdu', 'Chicago', 'Chongqing', 'Columbia', 'Hanoi', 'Havana', 'Hong Kong', 'Jakarta', 'Kinshasa', 'London', 'Los Angeles', 'Madrid', 'Malaysia', 'Manila', 'Moscow', 'New Delhi', 'New York City', 'Osaka', 'Ottawa', 'Paris', 'Perth', 'Phnom Penh', 'Pretoria', 'Pyongyang', 'Rabat', 'Reykjavik', 'Rome', 'San Diego', 'Seoul', 'Shanghai', 'Singapore', 'Sudan', 'Taipei', 'Tokyo', 'Toronto', 'Ulaanbaatar', 'Washington', 'Xinjiang', etc | Taipei |
| country | string | - the country/region code of the weather event - values include 'AU', 'BR', 'CA', 'CD', 'CN', 'CU', 'DE', 'EG', 'ES', 'FR', 'GB', 'HK', 'ID', 'IN', 'IQ', 'IS', 'IT', 'JP', 'KH', 'KP', 'KR', 'MA', 'MN', 'MY', 'PH', 'RU', 'TH', 'TW', 'US', 'VN', 'YE', 'ZA', etc | TW |
| coord\_lat | float | - the geographical coordinate in latitude for the recorded location | 25.05 |
| coord\_lon | list | - the geographical coordinate in longitude for the recorded location | 121.53 |
| sunrise | datetime | - the sunrise time of the recorded date | 2020-01-25 22:39:02.000000 |
| sunset | datetime | - the forecast sunset time of the recorded date | 2020-01-26 09:33:06.000000 |
| visibility | int | - the visibility, unit in miles - None for missing value | 805 |
| pressure | float | - the atmosheric pressure of the city at the recorded time - unit in Dynes per squre centimetre | 1014 |
| temperature\_min | float | - the minimum temperature of the city on the recorded date - unit in Fahrenheit (F) | 287.04 |
| temperature\_max | float | - the maximum temperature of the city on the recorded date - unit in Fahrenheit (F) | 292.04 |
| temperature | float | - the temperature of the city at the recorded time - unit in Fahrenheit (F) | 288.77 |
| humidity | float | - the humidity of the city at the recorded time - unit in percentage (%) | 96 |
| wind\_speed | float | - the wind speed of the city at the recorded time - unit in mile per hour (mph) | 0.89 |
| wind\_degree | float | - the wind degree of the city at the recorded time - value range from 0 to 360 degree | 199 |
| weather | string | - high level classification of the city's weather - value include 'Clear', 'Clouds', 'Haze', 'Mist', 'Rain', etc | Rain |
| weather\_desc | string | - detailed description of the city's weather - value include 'broken clouds', 'clear sky', 'few clouds', 'haze', 'light rain', 'mist', 'moderate rain', 'overcast clouds', 'scattered clouds', etc | light rain |
| clouds | float | - the density of cloud of the city - value ranging from 0 to 100 | 100 |

  
  

### Economics Statistics Data Feed

ALGOGENE Economics database collected over 10,000 economic time series across different countries and regions globally.

Economics event data can be accessed via callback function *'on\_econsdatafeed'*. The details can be accessed via a JSON/ dictionary-key methods. Here is a quick example to print the received data stream to console.

  
12345def on\_econsdatafeed(self, ed): title = ed.title value = ed.value msg = vars(ed) self.evt.consoleLog(msg)  

All other available attibutes can be referred to below.

  

| 'ed' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| timestamp | datetime | - the timestamp of the Economic data release - time unit standardize into GMT+0 | 2020-02-03 07:01:02.060000 |
| series\_id | string | - the unique id to identify an Economic time series | RECPROUSM156N |
| title | string | - the description of an Economic time series | Smoothed U.S. Recession Probabilities |
| tag | list | - high level classification of the time series | \['recession indicators', 'academic data'\] |
| seasonal\_adj | string | - an identifier to specify whether the time series is adjusted or not - "SA" - seasonally adjusted - "NSA" or blank - non-seasonally adjusted | NSA |
| popularity | int | - to specify whether this time series is widely used among industrial professionals - value ranging from 0 to 100 (the higher the value, the more popular in use) | 83 |
| obs\_start | date | - the earliest avalability of the time series | 1967-06-01 |
| src | string | - the source provider or publisher of the Economic time series | chauvet, marcelle |
| geo | sting | - the country or region that the Economic time series measure or apply to | usa |
| freq | string | - the reporting frequency of the Economic time series | monthly |
| date | date | - the end date of the period in which the time series is measured | 2019-12-01 |
| units | string | - the unit of the reported observation | Percent |
| value | float | - the reported figure | 2.06 |

  
  

There are 100,000+ economics time series in the database. Here to explore the available time series and the details of the meta attributes. For runtime efficiency, the search result will list out a maximum of 10,000 matched records. It is advised to further fine-tune the search in order to get your desired time series.

  
  

### Corporate Accouncement

For stock market, a corporate action is an event carried out by a company that materially impacts its stakeholders. These actions include the payment of dividends, stock split, mergers and acquisitions.

Corporate Action data can be accessed via callback function 'on\_corpAnnouncement'. The details can be accessed via an object attribute methods. Here is a quick example to print the received data stream to console.

  
12345678910def on\_corpAnnouncement(self, ca): event = ca.event ex\_date = ca.ex\_date dividend\_amt = ca.dividend\_amt msg = vars(ca) self.evt.consoleLog(msg)  

Other available attibutes can be referred to below.

  

| 'ca' ATTRIBUTE | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| symbol | string | - the finacial symbol | 00005HK |
| event | string | - specify the event type of corporate action - value can either be 'dividend', 'splits' | dividend |
| announce\_date | datetime | - the announcement date of the corporate action | 2019-05-04 |
| ex\_date | datetime | - the ex-dividend date where you will be eligible to receive dividends as long as you hold shares on that date | 2019-05-17 |
| payable\_date | datetime | - the date for dividend payment - this attribute is only available for event='dividend', empty otherwise | 2018-07-05 |
| dividend\_amt | float | - the dividend amount - this attribute is only available for event='dividend', empty otherwise | 0.1 |
| is\_special | string | - specify whether it is a normal or special dividend - value can either be 'T' or 'F' - this attribute is only available for event='dividend', empty otherwise | F |
| splits | float | - the share split ratio - for example 	- if value=3, it means that for each 1 original share, it will split into 3 shares 	- if value=0.2, it means that original 1 share will become 0.2 shares. In other word, for each 5 original shares, it will merge into 1 share - this attribute is only available for event='splits', empty otherwise |  |

  

  
  

### Order Feed

Immediately after submitting an order event *'self.evt.sendOrder(orderObj)'*, you will receive a system's message from *'def on\_orderfeed(self, of)'* telling you whether your order has been executed successfully, together with other transaction details.

Below is an example of extracting the transaction detail.

  
12345678def on\_orderfeed(self, of): trade\_status = of.status execution\_time = of.insertTime tradeID = of.tradeID instrument = of.instrument buysell = of.buysell execution\_price = of.fill\_price execution\_volume = of.fill\_volume  

The full list of attributes for 'on\_orderfeed' are as follows.

  

| 'of' ATTRIBUTE | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| status | string | - specify whether your order is accepted by the system - return 'success' if an order is opened/ closed successfully, or when a limit/stop order is filled - return 'cancel' if your submitted cancel order is successfully removed from the system - return 'pending' if a limit/stop order is submitted and pending to get filled - return 'kill' if the waiting time of an unfilled limit/stop order exceed your specified expiry time - return 'reject' if you specify 'allowShortSell' as False and you place a market sell order without sufficient positive position, or you don't have sufficient capital to open a new order | success |
| insertTime | datetime | - specify the timestamp for this order event - in format of 'YYYY-MM-DD HH:MM:SS.ffffff' | 2018-01-05 14:01:10.932000 |
| tradeID | int | - a system generated trade ID for your executed order - you need to use this tradeID to close/cancel your order later | 1 |
| openclose | string | - your order action | open |
| orderRef | string | - it is the order reference your specified previously at order submit | 1 |
| market | string | - the financial market of the excuted trade | FX |
| broker | string | - the broker/counterparty of the excuted trade | DMA |
| producttype | string | - the product type of the excuted trade | SPOT |
| instrument | string | - the instrument of the excuted trade | EURUSD |
| expiry | string | - the expiry date for the executed future/option contract, with format in 'yyyymmdd' - value is empty for instrument other than options and futures |  |
| right | string | - the call/put side for the executed option contract - value wiil be 'C' for call option - value wiil be 'P' for put option - value is empty for non option product |  |
| strike | float | - the strike price for the executed option contract - value is zero for non option product | 0 |
| buysell | int | - specify whether the trade is a buy or a short sell order - value will be 1 for buy order - value will be -1 for sell order | 1 |
| fill\_price | float | - specify the executed price of the trade | 1.25000 |
| fill\_volume | float | - specify the executed volume of the trade | 0.01 |

  
  

### Daily PL Feed

Under ALGOGENE's backtest environment, there is a tab *'PnL'* showing the daily profit and loss of your trading algorithm.

  
![](https://algogene.com/static/image/TechDoc/tab_PL.JPG)  

On the other hand, whenever market data stream comes to a new date, you can also access the PnL figures via API function *'def on\_dailyPLfeed(self, pl):'*, which already take into account of leverage, transaction cost, lot size unit, and margin usage. The PnL figures will be presented in a cummulative gain/ loss in dollar amount for each of the subscripted instrument(s), as well as an overall cummulative total.

The calculation formula is as follows.

  
![](https://algogene.com/static/image/TechDoc/PL_formula.JPG)  

PnL details in *'on\_dailyPLfeed'* can be extracted from a dictionary key method. Below are the full list of *'pl\[keys\]'*.

  

| 'pl' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| Acdate | datetime | - the accounting date of the cumulative PnL calculation - cut off time for all instruments is the same in GMT+0 | 2018-01-02 00:00:00 |
| TotalPL | float | - represent the total cummulative PnL in dollar value including both closed and outstanding orders for all your subscripted instruments up to Acdate | 1200.00 |

  

Moreover, you can access the PnL breakdown and the day range PnL by symbol from *'on\_dailyPLfeed'*. It can be extracted using a dictionary key based on *'your\_symbol'*. Below are the full list of *'pl\[your\_symbol\]'* key.

  

| 'pl\[your\_symbol\]' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| FixedPL | float | - represent the cummulative PnL in dollar value for closed orders up to 'Acdate' for 'your\_symbol' | 5700 |
| FloatPL | float | - represent the cummulative PnL in dollar value for outstanding orders up to 'Acdate' for 'your\_symbol' | \-400 |
| TotalPL | float | - represent the cummulative PnL in dollar value up to 'Acdate' for 'your\_symbol' - it equals the direct sum of FixedPL and FloatPL for the same 'your\_symbol' | 5300 |
| dayHigh | float | - represent the highest cummulative PnL value on 'Acdate' for 'your\_symbol' | 6300 |
| dayLow | float | - represent the lowest cummulative PnL value on 'Acdate' for 'your\_symbol' | 3800 |
| marginUsed | float | - represent the margin usage in base currency amount on 'Acdate' for 'your\_symbol' | 150 |

  

Suppose you have subscripted 2 instruments (eg. USDJPY, EURUSD). Then, you can extract the daily PnL data as follows.

  
12345def on\_dailyPLfeed(self, pl): acdate = pl\['Acdate'\] PL\_instru1 = pl\['USDJPY'\]\['TotalPL'\] PL\_instru2 = pl\['EURUSD'\]\['TotalPL'\] TotalPL = pl\['TotalPL'\]

  
  

### Position Feed

The trade position details can be found in tab 'Position', which is presented in a daily basis.

![](https://algogene.com/static/image/TechDoc/tab_Pos.JPG)  

On the other hand, whenever there is position updated due to successful orders opening/ closing/ cancel, you can get below information from *'def on\_openPositionfeed(self, op, oo, uo):'*

- 'op' - the latest net position in terms of number of oustanding contracts by symbol(s)
- 'oo' - the full list of filled open orders that are not closed yet
- 'uo' - the full list of limit/stop orders pending to fill

'op' object can be accessed through a dictionary key method. The first key for *'op'* will be your subscripted symbol, while the second key for *'op\[your\_symbol\]'* has the following attributes.

| 'op\[your\_symbol\]' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| LastTradeTime | datetime | - specify the last trading time for 'your\_symbol' | 2018-01-02 08:57:43 |
| netVolume | float | - specify the outstanding net position for 'your\_symbol' - positive value means net buy; negative value means net sell | \-2 |

  

Suppose you have subscripted 2 instruments (eg. USDJPY, EURUSD), below is an example showing you how to get its latest net position.

  
1234567def on\_openPositionfeed(self, op, oo, uo): p1 = 'USDJPY' p1\_LastTradeTime = op\[p1\]\['LastTradeTime'\] p1\_netVolume = op\[p1\]\['netVolume'\] p2 = 'EURUSD' p2\_LastTradeTime = op\[p2\]\['LastTradeTime'\] p2\_netVolume = op\[p2\]\['netVolume'\]  
  

Secondly, the full outstanding 'oo' object can be accessed through a dictionary key method. The first key for *'oo'* must come from one of the system generated tradeID, while the second key for *'oo\[tradeID\]'* include the following.

| 'oo\[tradeID\]' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
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
| trailingstop | float | - the trailing stop (in percentage) you specified when opening this trade - Default as 0 if not set | 0 |
| timeinforce | float | - the effective time of a limit/stop order, after which the unfilled limit/stop order will be canceled by system - Display as 0 if not set | 0 |
| holdtime | float | - the maximum holding time you specified when opening this trade - Display as 0 if not set | 0 |

  

Here is an example showing you how to compute the average purchase price for your subscripted instrument (eg. XAUUSD).

  
1234567891011121314  
  

Lastly and similarly, the full list of unfilled limit/stop order 'uo' object can be accessed through a dictionary key method. The first key for *'uo'* is a system generated tradeID, while the second key for *'uo\[tradeID\]'* has the following attributes.

| 'uo\[tradeID\]' KEY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| orderRef | string | - the order reference you specified previously at limit/stop order opening | 1 |
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

  

Here is an example showing you how to get the earliest submitted limit/stop order that is not filled yet.

  
123456789101112

  
  

### Performance Report

Under the *'Report'* tab, you can find a high level summary on how your trading strategy perform over the backtesting period. Below is the explanation of the summary statistics included in the report.

| STATISTICS | DESCRIPTIONS | FORMULA |
| --- | --- | --- |
| Tradable Days | - the total number of tradable days during the backtest horizon |  |
| Number of Trades | - the total number of trades placed during the backtest horizon - a round order will be counted as 2 |  |
| Average per trade PL | - overall PnL over 'Number of Trades' | ![](https://algogene.com/static/image/TechDoc/avgPerTradePL.JPG) |
| Average per day PL | - overall PnL over 'Tradable Days' | ![](https://algogene.com/static/image/TechDoc/avgPerDayPL.JPG) |
| Daily Return Series | - a simple return between 2 accounting dates | ![](https://algogene.com/static/image/TechDoc/DailyReturnSeries_formula.JPG) |
| Downside Daily Return Series | - cap the daily return series by 0 | ![](https://algogene.com/static/image/TechDoc/downside_dailyReturnSeries.JPG) |
| Mean Daily Return | - mean of the 'Daily Return' series | ![](https://algogene.com/static/image/TechDoc/MeanDailyReturn_formula.JPG) |
| Mean Annualized Return | - 252 times 'Mean Daily Return' |  |
| Median Daily Return | - 50th percentile of the 'Daily Return' series |  |
| Q1 Daily Return | - 25th percentile of the 'Daily Return' series |  |
| Q3 Daily Return | - 75th percentile of the 'Daily Return' series |  |
| 95% 1D VAR | - 5th percentile of the 'Daily Return' series |  |
| 99% 1D VAR | - 1st percentile of the 'Daily Return' series |  |
| Daily StdDev | - standard derviation of 'Daily Return' series | ![](https://algogene.com/static/image/TechDoc/StdDevDaily_formula.JPG) |
| Downside Daily StdDev | - standard derviation of 'Downside Daily Return' series | ![](https://algogene.com/static/image/TechDoc/downside_dailyStdDev.JPG) |
| Annualized StdDev | - 'Daily StdDev' times sqrt(252) |  |
| Downside Annualized StdDev | - 'Downside Daily StdDev' times sqrt(252) |  |
| Win Rate | - the portion of winning days during the backtest period | ![](https://algogene.com/static/image/TechDoc/winRate_formula.JPG) |
| Odd Ratio | - the ratio between win rate and non-win rate | ![](https://algogene.com/static/image/TechDoc/oddRatio_formula.JPG) |
| Daily Sharpe Ratio | - assume zero risk free rate - the ratio between daily mean return and daily std. dev. | ![](https://algogene.com/static/image/TechDoc/dailySharp_formula.JPG) |
| Annualized Sharpe Ratio | - 'Daily Sharpe Ratio' times sqrt(252) |  |
| Daily Sortino Ratio | - assume zero risk free rate - the ratio between daily mean return and downside daily std. dev. | ![](https://algogene.com/static/image/TechDoc/dailySortino.JPG) |
| Annualized Sortino Ratio | - 'Downside Daily Sharpe Ratio' times sqrt(252) |  |
| Drawdown Ratio | - The drop ratio from a peak value to a lower value | ![](https://algogene.com/static/image/TechDoc/DD.JPG) |
| Maximal Drawdown Ratio | - The maximum of the drawdown ratio along the whole period | ![](https://algogene.com/static/image/TechDoc/MDD.JPG) |
| Drawdown Amount | - The drop amount from a peak value to a lower value | ![](https://algogene.com/static/image/TechDoc/DD_amt.JPG) |
| Maximal Drawdown Amount | - The maximum of the drawdown amount along the whole period |  |
| Maximal Drawdown Duration | - The longest number of day before establishing a new high |  |
| Average Drawdown Duration | - The average number of days for drawdowns |  |
| Gross Profit | - Sum of PnL from closed profitable trades | ![](https://algogene.com/static/image/TechDoc/gross_profit.png) |
| Gross Loss | - Sum of PnL from closed lossing trades | ![](https://algogene.com/static/image/TechDoc/gross_loss.png) |
| Profit Factor | - Absolute of Gross Profit over Gross Loss | ![](https://algogene.com/static/image/TechDoc/profit_factor.png) |
| CAPM Beta | - Covariance of portfolio return and benchmark return, over variance of benchmark return | ![](https://algogene.com/static/image/TechDoc/beta.png) |
| Jensen's Alpha | - Difference between actual return and expected return from CAPM | ![](https://algogene.com/static/image/TechDoc/alpha.png) |
| Information Ratio | - Excess return over tracking error | ![](https://algogene.com/static/image/TechDoc/information_ratio.png) |
| Omega Ratio | - Sum of positive excess return, over sum of negative excess return | ![](https://algogene.com/static/image/TechDoc/omega.png) |
| Treynor Ratio | - Excess return over beta | ![](https://algogene.com/static/image/TechDoc/treynor_ratio.png) |
| Tail Ratio | - 95-percentile / 5-percentile of the return distribution | ![](https://algogene.com/static/image/TechDoc/tail_ratio.png) |
| Calmar Ratio | - Annualized return over maximum drawdown | ![](https://algogene.com/static/image/TechDoc/calmar_ratio.png) |
| Annual Turnover Rate | - The turnover amount over the average NAV | ![](https://algogene.com/static/image/TechDoc/TurnoverRate.JPG) |

  
  

In addition to above, the relative strength of a strategy in terms of activeness, prediction, robustness, consistency, profitability, and recovery will be presented in a radar chart.

- **Activeness** measures the trading frequency of a strategy over different time horizon for determining the applicability of a strategy for practical use.
- **Predictiveness** measures the accuracy of each trade action in making profits.
- **Robustness** based on the capital utilization rate and margin safety level over the trading horizon to determine the sustainability of a strategy.
- **Consistency** measures the similarity and stability of how a strategy perform over different time horizon.
- **Profitability** is a risk-adjusted measurement to evaluate how much profit is earned compared to the amount of risk taken.
- **Recovery** measures how fast a strategy can recover from losses.

Each completed backtest is assigned with an overall score ranging from 0-100. It is an equally weighted average for above 6 components, so as to ease for comparison among all different strategies.

  
  

