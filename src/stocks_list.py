from database_call import get_existed_stock_names, insert_stock_list_data



def stocks_list(single_data):

    stocks_list_tabel = get_existed_stock_names()

    stocks_symbol_list = [symbol for id,symbol in stocks_list_tabel]

    print(stocks_symbol_list)

    new_stocks_list = []

    

    if single_data['symbol'] not in stocks_symbol_list:

        new_stocks_list.append([single_data['symbol'],single_data['sm_name']])

    print(new_stocks_list)

    if len(new_stocks_list) >= 1:

        insert_stock_list_data(new_stocks_list)

    else:

        print('list is empty')

