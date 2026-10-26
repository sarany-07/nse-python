from list import p1_list
from apiCall import callapi
from database_call import TABLE_NAMES, database_cursor

from datetime import datetime


tabel_name = 'rawtabel'


full_data = callapi()

# print(full_data[0])


def normalize_date(data):

    # a = data.split(' ')

    date_val = datetime.strptime(data, "%d-%b-%Y %H:%M:%S").date()


    return date_val


for i in full_data:

    i[0]=normalize_date(i[0])

print(full_data[0])


query = f"""

    INSERT INTO {TABLE_NAMES['raw']}
        (annoucement_date, file_url, file_text, subject, file_size, stock_name, symbol)
    VALUES (%s,%s,%s,%s,%s,%s,%s)

"""

with database_cursor(commit=True) as cursor:
    cursor.executemany(query, full_data)

print('connected')















# sme_announcement_api_1day = 'https://www.nseindia.com/api/corporate-announcements?index=sme&from_date=15-10-2026&to_date=16-10-2026&reqXbrl=false'
# Equite_api_1day = 'https://www.nseindia.com/api/corporate-announcements?index=equities&from_date=15-10-2026&to_date=16-10-2026&reqXbrl=false'

# sql = 'https://chatgpt.com/share/6ad22134-0b3c-83ec-b076-81ea715cb44f'
# python = 'https://chatgpt.com/share/6ad22161-5644-83ee-a469-6f59600941b4'


