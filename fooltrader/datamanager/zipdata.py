# -*- coding: utf-8 -*-

import datetime
import os
import zipfile

from fooltrader.contract.files_contract import get_code_from_path
from fooltrader.settings import FOOLTRADER_STORE_PATH, STOCK_END_CODE, STOCK_START_CODE


def zip_dir(src_dir=FOOLTRADER_STORE_PATH, start_code=STOCK_START_CODE, end_code=STOCK_END_CODE, dst_dir=None,
            zip_file_name=None, include_tick=False, just_tick=False):
    if not zip_file_name:
        zip_file_name = "data-{}.zip".format(datetime.datetime.today())

    if dst_dir:
        dst_path = os.path.join(dst_dir, zip_file_name)
    else:
        dst_path = os.path.abspath(os.path.join(src_dir, os.pardir, zip_file_name))

    the_zip_file = zipfile.ZipFile(dst_path, 'w')

    for folder, subfolders, files in os.walk(src_dir):
        for file in files:
            the_path = os.path.join(folder, file)
            # 过滤code
            current_code = get_code_from_path(the_path=the_path)
            if current_code:
                if current_code > end_code or current_code < start_code:
                    continue

            # 只打包tick
            if just_tick:
                if not 'tick' in the_path:
                    continue
            # 不打包tick
            elif not include_tick and 'tick' in the_path:
                continue

            print("zip {}".format(the_path))
            the_zip_file.write(the_path,
                               os.path.relpath(the_path, src_dir),
                               compress_type=zipfile.ZIP_DEFLATED)

    the_zip_file.close()


def zip_data(src_dir=FOOLTRADER_STORE_PATH, dst_dir=None, zip_file_name=None):
    if not zip_file_name:
        zip_file_name = "data-{}.zip".format(datetime.datetime.today())

    if dst_dir:
        dst_path = os.path.join(dst_dir, zip_file_name)
    else:
        dst_path = os.path.abspath(os.path.join(src_dir, os.pardir, zip_file_name))

    the_zip_file = zipfile.ZipFile(dst_path, 'w')

    for folder, subfolders, files in os.walk(src_dir):
        for file in files:
            the_path = os.path.join(folder, file)

            # 不打包tick
            if 'tick' in the_path:
                continue

            print("zip {}".format(the_path))
            the_zip_file.write(the_path,
                               os.path.relpath(the_path, src_dir),
                               compress_type=zipfile.ZIP_DEFLATED)

    the_zip_file.close()


def unzip(zip_file, dst_dir):
    the_zip_file = zipfile.ZipFile(zip_file)
    print("start unzip {} to {}".format(zip_file, dst_dir))
    the_zip_file.extractall(dst_dir)
    print("finish unzip {} to {}".format(zip_file, dst_dir))
    the_zip_file.close()


if __name__ == '__main__':
    zip_data()
    # zip_dir(zip_file_name="data.zip", just_tick=True, start_code='000002', end_code='000002')
    # unzip(os.path.abspath(os.path.join(FOOLTRADER_STORE_PATH, os.pardir, "data.zip")), FOOLTRADER_STORE_PATH)
    # unzip("/home/xuanqi/workspace/github/fooltrader/data/future/shfe/2009_shfe_history_data.zip",
    #       get_exchange_dir(security_type='future', exchange='shfe'))
