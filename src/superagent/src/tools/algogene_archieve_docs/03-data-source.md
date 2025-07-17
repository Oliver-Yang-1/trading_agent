## Data Source

  

ALGOGENE provides strategy backtest and development over various Commodities, Cryptos, Equities, Equity Index, FX pairs, and Interest Rate Future CFDs, from 2000 up to the most recently completed trading month. All the datasets are standardized into the same GMT+0 time zone. The full list of available financial securities are as follows.

With continuous establishment of trading connection with different exchanges and brokers, there will be more financial instruments pending to launch in the near future. The list below will be updated from time to time.

  
  
  

Here is to explain how the 'CONTRACT SIZE' and 'SETTLE CURRENCY' is related to the calculation of margin amount and profit-and-loss under backtest environment as well as in real trading.

Suppose we have HKD as the base currency (also called home or local currency). We also open a long position of 1 contract for SPXUSD at US$2700 with leverage 50:1, where the exchange rate for USDHKD at that time is 7.781. Then, for opening such an order, the margin amount will be

*

margin\_amt = 100\*2700/50\*7.781 = HK$42,017.4

*

  

It means that our currenct account balance should have at least HK$42,017.4 in order to open such an order. Otherwise, the order will be rejected.

On the other hand, suppose we close the position when SPXUSD rises to US$2750 in the meantime USDHKD becomes 7.782. The profit-and-loss will then be calculated as

*

PnL = 100\*(2750\*7.782-2700\*7.781) = HK$39,180

*

  
  

