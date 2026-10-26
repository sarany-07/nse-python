import requests
import json
from list import p1_list
from stocks_list import stocks_list

urllink = 'https://www.nseindia.com/api/corporate-announcements?index=sme'

def callapi():

    today_list = []

    header = {
        "User-Agent": "PythonLearningApp/1.0",
        "Accept": "application/json",
        'Referer': 'https://www.nseindia.com/'
    }

    try:
        responce = requests.get(url=urllink,headers=header,timeout=20)

        data = responce.json()

    except Exception as error:
        print('invalid error')

    finally:
        pass

    def normalize_names(each_ammouncement_data):

        sim_list = []

        remove_list=["attFileSize","bflag","csvName","difference","dt","exchdisstime","hasXbrl","old_new","orgid","seq_id","smIndustry","sm_isin","sort_date"]

        for key,value in each_ammouncement_data.items():

            if key not in remove_list:
                sim_list.append(value)

        # conver_to_tuple = tuple(sim_list)
        today_list.append(sim_list)


    for i in data:

        normalize_names(i)
        stocks_list(i)

    return today_list


callapi()

