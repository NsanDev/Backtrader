from io import StringIO
from json import loads
from requests import get
from pandas import read_csv
from enum import Enum
LIM_API = "http://chgva-tux01.mercuria.met:3333/api/Lim/"
FORMAT_HEADER = {'Accept':'text/csv'}
DEFAULT_PRECISION = 6
COLUMN_NAMES = ['open','high','low','close','volume']

class RolloverDate(Enum):
    EXPIRATION_DAY = "expiration day"

class RolloverPolicy(Enum):
    ACTUAL_PRICES = "actual prices"


def _build_query_contract_ts(ticker, columns, from_date, to_date, precision):

    return f"{LIM_API}data/{ticker}/{columns}?fromDate={from_date}&toDate={to_date}&precision={precision}"


def _build_query_continuous_contract_ts(symbol, columns, from_date, to_date, precision,
                                        rolloverDate, rolloverPolicy):
    #To change in the API
    return f"{LIM_API}metadata/continuous/{symbol}/{columns}?fromDate={from_date}&toDate={to_date}" \
           f"&precision={precision}&rolloverPolicy={rolloverPolicy}&rolloverDate={rolloverDate}"


def fetch_contract(ticker, columns, from_date, to_date, precision=DEFAULT_PRECISION):

    url = _build_query_contract_ts(ticker, "|".join(columns), from_date, to_date,precision)
    url_data = get(url, headers=FORMAT_HEADER).content
    df = read_csv(StringIO(url_data.decode('utf-8')),
                        names=columns,
                        index_col=0,
                        parse_dates=True)
    return df


def fetch_continuous_contract(symbol, columns, from_date, to_date, rolloverDate=RolloverDate.EXPIRATION_DAY.value,
                   rolloverPolicy=RolloverPolicy.ACTUAL_PRICES.value, precision=DEFAULT_PRECISION):
    url = _build_query_continuous_contract_ts(symbol, "|".join(columns), from_date, to_date, precision,
                                        rolloverDate, rolloverPolicy)
    url_data = get(url, headers=FORMAT_HEADER).content
    df = read_csv(StringIO(url_data.decode('utf-8')),
                        names=columns,
                        index_col=0,
                        parse_dates=True)
    return df


# TODO: finish that
def _fetch_metadata_root_symbol(root_symbol):
    query_range = f'{LIM_API}metadata/datarange/{root_symbol}'
    url_range = get(query_range, headers=FORMAT_HEADER).content
    df = read_csv(StringIO(url_range.decode('utf-8')),
                        names=['symbol','first_traded','expiration_date'])
    query_meta = b'{LIM_API}metadata/{root_symbol}'
    url_data = get(query_meta).content


