  
stock_prices_yesterday = [10, 7, 5, 8, 11, 9]

def get_max_profits(stock_prices_yesterday):
    buy_stock = 0
    sell_stock = stock_prices_yesterday[0]
    for number in stock_prices_yesterday:
        if number > buy_stock:
            buy_stock = number

        elif number < sell_stock:
            sell_stock = number

    print(buy_stock, sell_stock)
            
list_1 = [1, 7, 3, 4]
list_2 = []
lenght_list = list_1[-1]
counter = 0 
while counter >= lenght_list:
    list_3 = list_1.pop(counter)





#get_max_profits(stock_prices_yesterday)
