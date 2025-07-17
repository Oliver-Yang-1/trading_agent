## Environment Setup

  

Once you have come up with a trading strategy, the first step to backtest it on ALGOGENE is to initialize the backtest environment. To do so, you should go to 'Backtest' -> 'script' section. There will be serveral components essential to be defined. That is,

- Strategy Name
- Backtest Start Month
- Backtest End Month
- Data Interval
- Initial Capital
- Leverage
- Allow Short Sell
- Position Netting
- Enable News Stream
- Enable Economics Stream
- Enable Weather Stream
- Transaction Cost
- Risk free rate
- Instruments
- Benchmark
  

### Strategy Name

A strategy name simply provides a high level description for a strategy backtest. It doesn't have to be unique, or it can even be set to an empty string. Nevertheless, it is strongly encouraged to give a meaningful name so that when your number of backtests increase, you can easily identify the desired script from **\[My History\]** pool.

  
  

### Start Period

You are required to specify the starting month for backtest. In case you have multiple instruments, it is recommended to set it to be the month in which all datasets of subscripted instruments are available.

  
  

### End Period

Similarly, you are also required to specify the end month for backtesting, which must be at least equal to or greater than the start period. Any invalid setting will by default set to the same as start period.

  
  

### Data Interval

Data interval refers to the frequency of data feed used for backtesting. The higher frequency you choose, the more accurate trading results it will generated, but in the compensation of higher computational burden and longer processing time. As a result, it is suggested to use an infrequent dataset for quick testing or debugging purposes. Once your algo and strategy is coded properly, then you might apply to a tick environment for a full simulation.

ALGOGENE currently supports 5 data intervals (i.e. 1 day bar, 1 hour bar, 5 min bar, 1 min bar, full tick). An important point to note here is that News, Economic Statistics, or other non-market data feed will only be available under full tick data environment.

  
  

### Initial Capital

Initial capital is the initial investment amount in dollar value you use to execute a trading strategy. For strategy backtest, to simplify the complexity of capital management, ALGOGENE assumes every trading algorithm is a self financing strategy. That is, during the backtesting period, there will no further capital or deposits be introduced.

Moreover, the backtest will be terminated once your capital balance goes to or below zero. Thus, in the early stage of your algorithm development, you are adviced to set it in a higher amount. In the later development stage, you might try to low this value in order to better utilize the capital.

Here, you can set it as any positive value. Any invalid setting will by default set to 1000000.

  
  

### Base Currency

Base currency refers to the account currency unit for your specified initial capital amount. For each trade order, the profit and loss will be converted from the settle currency to the base currency.

  
  

### Leverage

Different markets/ brokers/ countries have different restrictions on the maximum leverage one can take. Therefore, ALGOGENE provides a flexibility to set the leverage ratio subject to your own risk appetite. In market practice, common leverage ratios include 5:1, 10:1, 20:1, 33:1, 50:1, and 100:1. For example, a 50:1 ratio mean $10,000 capital will have a maximum purchasing power of 50\*10000 = $500,000.

Here you can set it as any positive integer number. Any invalid setting will be by default set to 1. That is, no leverage is taken.

  
  

### Allow Short Sell

In real world, there might be difficulites or restrictions on short sell over certain markets. This variable is introduced to better simulate the real situation.

If it is set to False, any submitted sell orders without positve inventory will be rejected by the system. In contrast, a 'True' setting has no restriction on opening order in either long/short direction, as long as you have sufficient capital to execute that trades.

  
  

### Position Netting

It is for system handling for partial close.

Suppose you open 3 offsetting trades:

- #1: buy 2 share of ABC at $123
- #2: sell 1 share of ABC at $124
- #3: sell 1 share of ABC at $125

If position netting is disabled, all transactions are managed in a round order mannar and you need to close the 3 trades separately in order to realize the PnL. Thus, the PnL is **unrealized** and calculated to be 2\*(bid - 123) + 1\*(124 - ask) + 1\*(125 - ask) = $3 + 2\*(bid - ask).

If position netting is enabled, orders will be offsetted based on FIFO (First In, First Out) approach, and PL will become realized so long as position is net to zero. Thus, your PnL in this case will be **realized** at $3.

  
  

### Transaction Cost

To better simulate the trading performance in real market, you can specify the per order transaction cost based on your knowledge and experience. It will be expressed in an all-in amount to cover any kind of trading costs, eg. broker fee, tax, stamp duty, etc. The cost is calculated in multiple to your transact number of contract and lot. For example, suppose you set this per order trade cost as 10 and you buy 5 contract of SPXUSD at $3000, the charged transaction cost amount will then be 5\*10 = $50

Moreover, the cost will be charged at the begining of successful open order, and no charge will be involved to close an order. Also, any rejected or cancelled trades will not be charged.

At the beginning of your strategy development, it is suggested to set it as zero, so that you can easily identify whether your algorithm has a potential to generate consistent return. Later, you can include a more realistic assumption for the transaction cost.

Here you can set it as any positive number. Any invalid setting will be by default set to 0. That is, no transaction cost is taken into account.

  

### Risk free rate

Risk-free rate is the minimum guranteed interest rate that you could receive if your capital is alternatively invested on a risk-free asset (eg. US treasury bond, bank saving rate, etc). System by defualt set to 0.

  
  

### Instruments

It is neccessary to select at least 1 instrument to include in backtest. The available instrument symbols can be referred to *'Data Source'* section.

For Options/Futures, subscribing an instrument will automatically bind to the whole contract chains for different expiry/strike/right.

  
  

### Benchmark

It compares how your strategy performs relative to a benchmark 'buy-and-hold' strategy of a selected index or underlying.

  
  

### Enable News Stream

It provides news feed from various global publishers in multiple languages.

When news data feed is on, the backtest instance will additionally listen to historical News events in a callback sequence together with the market data stream.

  
  

### Enable Economics Stream

This data stream provides fundamental statistics in country- or city-wide including GDP, Inflation Rate, Unemployment Rate, etc. It supports analysis from economic perspectives.

If this data feed is on, the backtest instance will additionally listen to Economics events in a callback sequence.

  
  

### Enable Weather Stream

Some financial markets such as commodity usually found to have cyclical or seasonal effect. This data stream provides city-wide weather status such as temperature, humudity, wind speed, etc.

If weather feed is on, the backtest instance will additionally listen to weather events in a callback sequence.

  
  

