## Architecture

  

ALGOGENE's Python IDE is where you develop your trading idea. The platform is architected in an event streaming model to process data and to simulate historical environment. It defines a simple but powerful object-oriented API callbacks as building blocks. Their functional usage will be discussed in more details in the coming sections.

- init\_MarketData
- on\_marketdatafeed
- on\_bulkdatafeed
- on\_newsdatafeed
- on\_econsdatafeed
- on\_weatherdatafeed
- on\_orderfeed
- on\_openPositionfeed
- on\_dailyPLfeed

The logical process and computing flow is structured as below.

  
![](https://algogene.com/static/image/TechDoc/process3.JPG)  
  

In the design, ALGOGENE strived to make everything as simple as possible while preseving all essential components. The reason of doing this is to lower the barrier for people from different background to get into the field of algorithmic trading.

Now, we are pround that the skeleton of ALGOGENE framework is structured in less than 50 lines of code.

123456789101112131415161718192021222324252627282930313233 from AlgoAPI import AlgoAPIUtil,AlgoAPI\_Backtest class AlgoEvent:def \_\_init\_\_ ( self ):pass def start ( self,mEvt ):self.evt \= AlgoAPI\_Backtest.AlgoEvtHandler ( self,mEvt ) self.evt.start ( ) def on\_bulkdatafeed ( self,isSync,bd,ab ):pass def on\_marketdatafeed ( self,md,ab ):pass def on\_newsdatafeed ( self,nd ):pass def on\_econsdatafeed ( self,ed ):pass def on\_weatherdatafeed ( self,wd ):pass def on\_corpAnnouncement ( self,ca ):pass def on\_orderfeed ( self,of ):pass def on\_dailyPLfeed ( self,pl ):pass  

  
  

