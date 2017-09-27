import argparse

parser = argparse.ArgumentParser()
parser.add_argument("func", choices=['init_trading_dates'],
                    help="display a square of a given number")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")
args = parser.parse_args()
answer = args.square ** 2
if args.verbose:
    print("the square of {} equals {}".format(args.square, answer))
else:
    print(answer)
