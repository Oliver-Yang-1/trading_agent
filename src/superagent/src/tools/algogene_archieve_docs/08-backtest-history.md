## Backtest History

  

Under **\[My History\]** section, all your previous backtest results and outstanding running tasks can be found.

For any non-finished oustanding task(s), you can either 'Load' to view its latest simulation image, or 'Cancel' the running task. For historical completed backtests, you can also either 'Load' to view the full result, or 'Delete' unwanted backtests.

  
![](https://algogene.com/static/image/TechDoc/myhistory.JPG)

  
  

### Query New Chain Address

The function ' **self.evt.getChainHistory(...)** ' can be used to query the number of unique addresses that appeared for the first time in a transaction of the native coin in the network. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'address\_new' | address\_new |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC', 'AAVE', 'ABT', 'AMPL', 'ANT', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SNT', 'SNX', 'STAKE', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'WETH', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - number of new address | 75446 |

  
  

Suppose we want to query the new network address for ETH on a daily basis.

12345678910111213141516

  
  

### Query Receiver Address

The function ' **self.evt.getChainHistory(...)** ' can also be used to query the number of unique addresses that were active as a receiver of funds. Only addresses that were active as a receiver in successful non-zero transfers are counted. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'address\_receiver' | address\_receiver |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC', 'AAVE', 'ABT', 'AMPL', 'ANT', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SNT', 'SNX', 'STAKE', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'WETH', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - number of unique receiver address | 226051 |

  
  

Suppose we want to query the unique receiver address for ETH on a daily basis.

12345678910111213141516

  
  

### Query Sender Address

The function ' **self.evt.getChainHistory(...)** ' can be used to query the number of unique addresses that were active as a sender of funds. Only addresses that were active as a sender in successful non-zero transfers are counted. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'address\_sender' | address\_sender |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC', 'AAVE', 'ABT', 'AMPL', 'ANT', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SNT', 'SNX', 'STAKE', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'WETH', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - number of unique sender address | 242478 |

  
  

Suppose we want to query the unique sender address for ETH on a daily basis.

12345678910111213141516

  
  

### Query Total Address

The function ' **self.evt.getChainHistory(...)** ' can be used to query the total number of unique addresses that ever appeared in a transaction of the native coin in the network. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'address\_total' | address\_total |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC', 'AAVE', 'ABT', 'AMPL', 'ANT', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SNT', 'SNX', 'STAKE', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'WETH', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - number of total unique address | 152991428 |

  
  

Suppose we want to query the total unique address for ETH on a daily basis.

12345678910111213141516

  
  

### Query Block Interval

The function ' **self.evt.getChainHistory(...)** ' can be used to query the mean time (in seconds) between mined blocks. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'block\_interval' | block\_interval |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - the average number of second between mined blocks | 13.8924264351182 |

  
  

Suppose we want to query the average block mined time for ETH on a daily basis.

12345678910111213141516

  
  

### Query Mined Block

The function ' **self.evt.getChainHistory(...)** ' can be used to query the number of blocks created and included in the main blockchain every day. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'block\_mined' | block\_mined |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - number of block mined on that day | 6367 |

  
  

Suppose we want to query the number of block mined for ETH on a daily basis.

12345678910111213141516

  
  

### Query Block Size

The function ' **self.evt.getChainHistory(...)** ' can be used to query the total size of all blocks created within the day (in bytes). The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'block\_size' | block\_size |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - the size of block created on that day | 94581.5983277054 |

  
  

Suppose we want to query the block size created for ETH on a daily basis.

12345678910111213141516

  
  

### Query Miner Fee

The function ' **self.evt.getChainHistory(...)** ' can be used to query the total amount of fees paid to miners (unit in asset). Issued (minted) coins are not included. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'fee\_miner' | fee\_miner |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - the total miner fee on that day | 2755.60112570558 |

  
  

Suppose we want to query the miner fee for ETH on a daily basis.

12345678910111213141516

  
  

### Query Gas Used

The function ' **self.evt.getChainHistory(...)** ' can be used to query the total amount of gas used in all transactions. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'gas\_used' | gas\_used |
| asset | Yes | string | - specify the crypto asset - available values include 'ETH' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - the total gas used on that day | 95841970142 |

  
  

Suppose we want to query the gas used for ETH on a daily basis.

12345678910111213141516

  
  

### Query Hash Rate

The function ' **self.evt.getChainHistory(...)** ' can be used to query the average estimated number of hashes per second produced by the miners in the network. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'hash\_rate' | hash\_rate |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', ETH' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - the average hash rate on that day | 1020754820942120.0 |

  
  

Suppose we want to query the hash rate for ETH on a daily basis.

12345678910111213141516

  
  

### Query Spent Output Profit Ratio (SOPR)

The function ' **self.evt.getChainHistory(...)** ' can be used to query the SOPR indicator. Spent Output Profit Ratio (SOPR) is computed by dividing the realized value (in USD) divided by the value at creation (USD) of a spent output. In other word, SOPR = price sold / price paid. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'indicator\_sopr' | indicator\_sopr |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', ETH', 'LTC' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - the average hash rate on that day | 0.942036072684753 |

  
  

Suppose we want to query the SOPR for ETH on a daily basis.

12345678910111213141516

  
  

### Query Market Cap

The function ' **self.evt.getChainHistory(...)** ' can be used to query the market capitalization (or network value). It is defined as the product of the current supply by the current USD price. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'market\_cap' | market\_cap |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC', 'AAVE', 'ABT', 'AMPL', 'ANT', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SNT', 'SNX', 'STAKE', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - the market cap on that day | 236419355911.9569 |

  
  

Suppose we want to query the market cap for ETH on a daily basis.

12345678910111213141516

  
  

### Query Coin Supply

The function ' **self.evt.getChainHistory(...)** ' can be used to query the total amount of all coins ever created/issued, i.e. the circulating supply. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'supply' | supply |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC', 'AAVE', 'ABT', 'AMPL', 'ANT', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SNT', 'SNX', 'STAKE', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-23' |
| v | float | - the coin supply on that day | 118610842.16867436 |

  
  

Suppose we want to query the circulating supply for ETH on a daily basis.

12345678910111213141516

  
  

### Query Transaction Rate

The function ' **self.evt.getChainHistory(...)** ' can be used to query the total amount of transactions per second. Only successful transactions are counted. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC', 'AAVE', 'ABT', 'AMPL', 'ANT', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SNT', 'SNX', 'STAKE', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-30' |
| v | float | - the average transaction rate on that day | 11.734479166666667 |

  
  

Suppose we want to query the transaction rate for ETH on a daily basis.

12345678910111213141516

  
  

### Query Total Transfer Volume

The function ' **self.evt.getChainHistory(...)** ' can also be used to query the total amount of coins transferred on-chain as follows. Only successful transfers are counted. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'transfer\_volume\_total' | transfer\_volume\_total |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'LTC', 'AAVE', 'ABT', 'AMPL', 'ANT', 'APE', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SAND', 'SHIB', 'SNT', 'SNX', 'STAKE', 'stETH', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'WETH', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-05-30' |
| v | float | - the total transferred coin on blockchain on that day | 1866571.87361071 |

  
  

Suppose we want to query the transfer volume for ETH on a daily basis.

12345678910111213141516

  
  

### Query Exchange Inflow

The function ' **self.evt.getChainHistory(...)** ' can also be used to query the total amount of coins transferred to exchange addresses. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'exchange\_inflow\_total' | exchange\_inflow\_total |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'AAVE', 'ABT', 'ANT', 'APE', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RSR', 'SAI', 'SAN', 'SAND', 'SHIB', 'SNT', 'SNX', 'STAKE', 'stETH', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'WETH', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2021-12-07' |
| v | float | - the total coin transferred to exchanges address on that day | 408016.11536319763 |

  
  

Suppose we want to query the exchange's inflow of ETH on a daily basis.

12345678910111213141516

  
  

### Query Exchange Inhouse Transfer

The function ' **self.evt.getChainHistory(...)** ' can also be used to query the total amount of coins transferred within wallets of the same exchange. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'exchange\_inhouse\_transfer\_volume' | exchange\_inhouse\_transfer\_volume |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'AAVE', 'ABT', 'ANT', 'APE', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RSR', 'SAI', 'SAN', 'SAND', 'SHIB', 'SNT', 'SNX', 'STAKE', 'stETH', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'WETH', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2021-12-07' |
| v | float | - the total amount of coins transferred within wallets of the same exchange on that day | 495695.63099544763 |

  
  

Suppose we want to query the total amount of ETH transferred within exchanges' wallets on a daily basis.

12345678910111213141516

  
  

### Query Supply from Smart Contracts

The function ' **self.evt.getChainHistory(...)** ' can also be used to query the percent of total supply of the token that is held in smart contracts. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'supply\_contracts' | supply\_contracts |
| asset | Yes | string | - specify the crypto asset - available values include 'ETH', 'AAVE', 'ABT', 'AMPL', 'ANT', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SNT', 'SNX', 'STAKE', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'TUSD', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2022-01-14' |
| v | float | - the percent of total supply of the token that is held in smart contracts on that day | 0.444602780587112 |

  
  

Suppose we want to query the percent of ETH held in smart contracts on a daily basis.

12345678910111213141516

  
  

### Query Token Gini Coefficient

The function ' **self.evt.getChainHistory(...)** ' can also be used to query the Gini coefficient for the distribution of coins over addresses. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'gini\_coeff' | gini\_coeff |
| asset | Yes | string | - specify the crypto asset - available values include 'ETH', 'AAVE', 'ABT', 'AMPL', 'ANT', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DDX', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DOUGH', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'INDEX', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NDX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RPL', 'RSR', 'SAI', 'SAN', 'SNT', 'SNX', 'STAKE', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'TUSD', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2021-12-18' |
| v | float | - the Gini Coefficient of the token on that day | 0.993328 |

  
  

Suppose we want to query the Gini Coefficient of ETH on a daily basis.

12345678910111213141516

  
  

### Query Issued Coin Supply

The function ' **self.evt.getChainHistory(...)** ' can also be used to query the total amount of new coins added to the current supply, i.e. minted coins or new coins released to the network. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'supply\_issued' | supply\_issued |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2021-12-18' |
| v | float | - the newly issued token on that day | 14997.530791453 |

  
  

Suppose we want to query the number of newly issued ETH on a daily basis.

12345678910111213141516

  
  

### Query Exchange Deposit

The function ' **self.evt.getChainHistory(...)** ' can also be used to query the total number of transfers to exchange addresses, i.e. the number of on-chain deposits to exchanges. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'exchange\_deposit' | exchange\_deposit |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'AAVE', 'ABT', 'ANT', 'APE', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RSR', 'SAI', 'SAN', 'SAND', 'SHIB', 'SNT', 'SNX', 'STAKE', 'stETH', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'TUSD', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'WETH', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2021-12-18' |
| v | float | - the number of transfers to exchange addresses on that day | 38391.0 |

  
  

Suppose we want to the number of ETH transfers to exchange addresses on a daily basis.

12345678910111213141516

  
  

### Query Exchange Withdrawal

The function ' **self.evt.getChainHistory(...)** ' can also be used to query the total count of transfers from exchange addresses, i.e. the number of on-chain withdrawals from exchanges. The parameters can be referred to below.

| 'self.evt.getChainHistory' INPUT PARAMETER | IS NECESSARY | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- | --- |
| evt | Yes | string | set to 'exchange\_withdrawal' | exchange\_withdrawal |
| asset | Yes | string | - specify the crypto asset - available values include 'BTC', 'ETH', 'AAVE', 'ABT', 'ANT', 'APE', 'ARMOR', 'BADGER', 'BAL', 'BAND', 'BAT', 'BIX', 'BNT', 'BOND', 'BRD', 'BUSD', 'BZRX', 'CELR', 'CHSB', 'CND', 'COMP', 'CREAM', 'CRO', 'CRV', 'CVC', 'CVP', 'DAI', 'DENT', 'DGX', 'DHT', 'DMG', 'DODO', 'DRGN', 'ELF', 'ENG', 'ENJ', 'EURS', 'FET', 'FTT', 'FUN', 'GNO', 'GUSD', 'HEGIC', 'HOT', 'HPT', 'HT', 'HUSD', 'KCS', 'LAMB', 'LBA', 'LDO', 'LEO', 'LINK', 'LOOM', 'LRC', 'MANA', 'MATIC', 'MCB', 'MCO', 'MFT', 'MIR', 'MKR', 'MLN', 'MTA', 'MTL', 'MX', 'NEXO', 'NFTX', 'NMR', 'Nsure', 'OCEAN', 'OKB', 'OMG', 'PAY', 'PERP', 'PICKLE', 'PNK', 'PNT', 'POLY', 'POWR', 'PPT', 'QASH', 'QKC', 'QNT', 'RDN', 'REN', 'REP', 'RLC', 'ROOK', 'RSR', 'SAI', 'SAN', 'SAND', 'SHIB', 'SNT', 'SNX', 'STAKE', 'stETH', 'STORJ', 'sUSD', 'SUSHI', 'TEL', 'TOP', 'TUSD', 'UBT', 'UMA', 'UNI', 'USDC', 'USDK', 'USDP', 'USDT', 'UTK', 'VERI', 'WaBi', 'WAX', 'WBTC', 'WETH', 'wNXM', 'WTC', 'YAM', 'YFI', 'ZRX' | ETH |
| starttime | No | datetime | - specify the start date of search result, format in 'YYYY-MM-DD HH:MM:SS' - empty value will assume to query from the earliest data history - future date value will assume to be the current date | '2022-05-23' |
| endtime | No | datetime | - specify the end date of search result, format in 'YYYY-MM-DD HH:MM:SS' - an empty value or future date value will assume to be the current date | '2022-05-30' |

  
  

The returned output *'res'* will be a list of JSON object sorted in ascending time, where its value can be accessed via a dictionary key method.

| 'res' | DATA TYPE | DESCRIPTIONS | SAMPLE |
| --- | --- | --- | --- |
| t | string | - the value date | '2021-12-18' |
| v | float | - the number of transfers from exchange addresses on that day | 42752.0 |

  
  

Suppose we want to the number of ETH transferred from exchange addresses on a daily basis.

12345678910111213141516

  
  

