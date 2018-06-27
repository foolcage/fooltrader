# -*- coding: utf-8 -*-
import argparse

import fooltrader.botsamples

if __name__ == '__main__':
    import pkgutil

    for _, modname, is_pkg in pkgutil.iter_modules(fooltrader.botsamples.__path__):
        if not is_pkg:
            exec("from fooltrader.botsamples.{} import *".format(modname))

    parser = argparse.ArgumentParser()
    parser.add_argument('bot_name', help='the bot you want to run')
    parser.add_argument('--security_item', help='the security item you want to watch')
    parser.add_argument('--start_date', help='the start date')

    args = parser.parse_args()
    print(args)

    bot_name = args.bot_name
    bot_class = ''.join([item.title() for item in bot_name.split('_')])

    # exec("from fooltrader.botsamples.{} import {}".format(bot_name, bot_class))

    if args.security_item:
        the_bot = eval("{}(security_item='{}')".format(bot_class, args.security_item))
    else:
        the_bot = eval("{}()".format(bot_class))

    the_bot.run()
