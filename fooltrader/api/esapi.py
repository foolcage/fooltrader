# -*- coding: utf-8 -*-
from fooltrader.contract.data_contract import KDATA_COLUMN_STOCK


def get_kdata(security_item, the_date=None, start_date=None, end_date=None, fuquan='bfq', level='day',
              fields=KDATA_COLUMN_STOCK):
    """
    get kdata.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code
    the_date : TimeStamp str or TimeStamp
        get the kdata for the exact date
    start_date : TimeStamp str or TimeStamp
        start date
    end_date : TimeStamp str or TimeStamp
        end date
    fuquan : str
        {"qfq","hfq","bfq"},default:"bfq"
    level : str or int
        the kdata level,{1,5,15,30,60,'day','week','month'},default : 'day'

    Returns
    -------
    DataFrame

    """
    pass
