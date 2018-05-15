from fooltrader.api import quote


def test_get_china_stock_list():
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
