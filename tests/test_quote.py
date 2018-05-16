from fooltrader import settings
from fooltrader.api import quote


def test_get_china_stock_list():
    print(settings.FOOLTRADER_STORE_PATH)
    df = quote.get_security_list('stock', exchanges=['sh', 'sz'])
    assert '000001' in df.index
    assert '金融行业' == df.loc['000001', 'sinaIndustry']

    df = quote.get_security_list('stock', exchanges=['sh'])
    assert '600000' in df.index
    assert '金融行业' == df.loc['600000', 'sinaIndustry']

    df = quote.get_security_list('stock', exchanges=['sh', 'sz'], start='000338', end='600388')
    assert '000338' in df.index
    assert '600388' in df.index
    assert '600389' not in df.index

    df = quote.get_security_list('stock', exchanges=['sh', 'sz'], codes=['300027', '000002'])
    assert len(df.index) == 2

    df = quote.get_security_list('stock', exchanges=['sh', 'sz'], mode='es')
    assert type(df.loc['600004', 'sinaArea']) == list
    assert '广州' in (df.loc['600004', 'sinaArea'])
    assert '广东' in (df.loc['600004', 'sinaArea'])


def test_get_mix_stock_list():
    df = quote.get_security_list('stock', exchanges=['sh', 'sz', 'nasdaq'])
    assert '000001' in df.index
    assert '600000' in df.index
    assert 'MSFT' in df.index


def test_get_future_list():
    df = quote.get_security_list('future', exchanges=['shfe'])
    assert 'ag1301' in df.index


def test_to_security_item():
    item = quote.to_security_item('stock_sz_000338')
    assert item.id == 'stock_sz_000338'
    assert item.code == '000338'

    item = quote.to_security_item('000338')
    assert item.id == 'stock_sz_000338'
    assert item.code == '000338'

    item = quote.to_security_item('stock_nasdaq_MSFT')
    assert item.id == 'stock_nasdaq_MSFT'
    assert item.code == 'MSFT'

    item = quote.to_security_item('MSFT')
    assert item.id == 'stock_nasdaq_MSFT'
    assert item.code == 'MSFT'

    item = quote.to_security_item('future_shfe_ag1301')
    assert item.id == 'future_shfe_ag1301'
    assert item.code == 'ag1301'

    item = quote.to_security_item('ag1301')
    assert item.id == 'future_shfe_ag1301'
    assert item.code == 'ag1301'

    item = quote.to_security_item('future_shfe_ag1301')
    assert item.id == 'future_shfe_ag1301'
    assert item.code == 'ag1301'

    item = quote.to_security_item('ag1301')
    assert item.id == 'future_shfe_ag1301'
    assert item.code == 'ag1301'


def test_get_stock_kdata():
    df = quote.get_kdata('600977')
    assert len(df.index) > 0

    df = quote.get_kdata('600977', the_date='2018-03-29')
    assert '2018-03-29' in df.index

    df = quote.get_kdata('600977', start_date='2016-08-09', end_date='20180329')
    assert '2016-08-09' in df.index
    assert '20180329' in df.index
    assert df.loc['2016-08-09', 'factor'] == 1
    assert df.loc['20180329', 'factor'] > 1


def test_get_stock_fuquan_kdata():
    # 根据factor计算的后复权价格
    df = quote.get_kdata('600977', the_date='2018-03-29', fuquan='hfq')

    # 从新浪获取的后复权价格
    df1 = quote.get_kdata('600977', the_date='2018-03-29', fuquan='hfq', source='sina')

    # 四舍五入取两位小数
    assert round(df.loc['2018-03-29', 'close'], 2) == round(df1.loc['2018-03-29', 'close'], 2)
