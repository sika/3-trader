  

start = time.time()
# temp_stockInfo_list = getStockList(pathInputThis + glo_stockInfo_file_raw)
# # temp_stockInfo_list = getStockList(pathInputThis + 'stock-info-raw-4.csv')
# setStockListGlobally(temp_stockInfo_list, glo_stockInfo_list_name)
# print('temp_stockInfo_list:', len(temp_stockInfo_list))

# temp_blacklist = getStockList(pathInputThis + glo_blacklist_file)
# setStockListGlobally(temp_blacklist, glo_blacklist_name)
# print('temp_blacklist:', len(temp_blacklist))

# temp_stockInfo_list = mod_shared.removeListFromList(temp_stockInfo_list, temp_blacklist)
# print('temp_stockInfo_list:', len(temp_stockInfo_list))

# temp_complimentary_list = getStockList(pathInputThis + glo_complimentary_file)
# setStockListGlobally(temp_complimentary_list, glo_nn_complimentary_list_name)
# print('temp_complimentary_list:', len(temp_complimentary_list))

# temp_stockInfo_list = getStocksFromSb(temp_stockInfo_list)
# print('temp_stockInfo_list:', len(temp_stockInfo_list))

# temp_stockInfo_list = mod_shared.mod_shared.updateListFromListByKeys(temp_stockInfo_list, temp_complimentary_list) # list to update, list to update from

# temp_stockInfo_list = getStocksFromNn(temp_stockInfo_list)

# writeStockList(temp_stockInfo_list, pathInputThis + glo_stockInfo_file_updated)
# writeStockList(temp_stockInfo_list, pathOutput+glo_stockInfo_file_updated)

# time.sleep(5)

# stockToBuy_list = filterStocksToWatch()
# writeStockList(stockToBuy_list, pathInputThis+glo_stockToBuy_allData_file)

# writeStockList(stockToBuy_list, pathInput+glo_stockToBuy_file_str)

# clearSbWatchlist()
# stockToBuy_list = getStockList(pathInputThis+glo_stockToBuy_file_str)

list_of_keys_to_remove = [glo_stockInfoColName_price,
glo_stockInfoColName_6_percent,
glo_stockInfoColName_6_value,
glo_stockInfoColName_12_percent,
glo_stockInfoColName_12_value,
glo_stockInfoColName_24_percent,
glo_stockInfoColName_24_value,
glo_stockInfoColName_percentAverage,
glo_stockInfoColName_valueAverage,
glo_stockInfoColName_24_buys_correct_percent,
glo_stockInfoColName_buysTotal,
glo_stockInfoColName_pricePercentChange_average,
glo_stockInfoColName_pricePercentChange_median,
glo_stockInfoColName_buyAverageFailedPerChange,
glo_stockInfoColName_buyAverageSuccessPerChange,
glo_stockInfoColName_buyMedianFailedPerChange,
glo_stockInfoColName_buyMedianSuccessPerChange,
glo_stockInfoColName_buyAndFailMedian_keyValue,
glo_stockInfoColName_buyAndFailAverage_keyValue,
glo_stockInfoColName_percentChange_highestThroughCurrent,
glo_complimentary_colName_compList
]

# stockToBuy_forOutputFolder_list = deleteKeyValuesFromOrderedDict(stockToBuy_list, list_of_keys_to_remove)

list_of_keys_to_add = [glo_traderScript_colName_held,
glo_traderScript_colName_active,
glo_traderScript_colName_activeTemp,
glo_traderScript_colName_amountHeld,
glo_traderScript_colName_price,
glo_traderScript_colName_priceTemp
]
# stockToBuy_forOutputFolder_list = addKeyToOrderedDict(stockToBuy_forOutputFolder_list, list_of_keys_to_add)
# writeStockList(stockToBuy_forOutputFolder_list, pathInput_main+glo_stockToBuy_file_str)

BP()
pass

# setSbWatchlist(stockToBuy_list)

end = time.time()
timeElapsed = datetime.timedelta(seconds=(end - start))
timeElapsed = str(timeElapsed - datetime.timedelta(microseconds=timeElapsed.microseconds))
print('Time elapsed (H:M:S):', timeElapsed)
# Goal:
    # 1. check best stocks to watch
    #   - get the success-fail ratio of signals for 6, 12 and 24 months
    #   - get the success-fail ratio total average between 6, 12 and 24 months
    # 2. get information which can directly be used by 4-robo
    #   - market Id
    #   - Identifier Id
    #   - (sorted by highest?)
    # 3. make it possible for 4-robo to use the output automatically
    # 4. Make 4-robo use the ouput automatically

    # Consider:
    # - If new list of stocks, how to handle of those already held are not in list?