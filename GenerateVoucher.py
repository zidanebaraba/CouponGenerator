import random
import pandas as pd
from sqlalchemy import create_engine
from datetime import date, timedelta


def create_coupon(y):
    exp = date.today() + timedelta(days=3)

    Dict = {'coupon': [],
            'expiration': [],
            'status': []
            }
    num = int(y)
    list_coupon = []
    exp_date = []
    x = 1

    while x <= num:
        Dict['coupon'].append('ISAT' + str(random.randint(10000000, 99999999)))
        Dict['expiration'].append(exp.strftime("%Y-%m-%d"))
        Dict['status'].append(2)
        x += 1

    df = pd.DataFrame(Dict)
    print(df)

    # create sqlalchemy engine
    engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                           .format(user="root",
                                   pw="",
                                   db="db_coupon"))

    df.to_sql('tbl_voucher', con=engine, if_exists='append', index=False)
