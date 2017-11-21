# vim: set fileencoding=utf-8 :

import argparse
import gzip
import sys

import gncxml

def main(prog="gncxml"):
    args = build_argparser(prog).parse_args()

    try:
        with gzip.open(args.file) as f:
            book = gncxml.Book(f)
    except OSError as err:
        sys.exit("error: {0} '{1}'".format(err, args.file.name))

    df = None
    tp = None
    if args.type in {"account", "act"}:
        tp = "account"
        df = book.list_accounts()
    elif args.type in {"commodity", "cmdty"}:
        tp = "commodity"
        df = book.list_commodities()
    elif args.type in {"price"}:
        tp = "price"
        df = book.list_prices()
    elif args.type in {"split", "sp"}:
        tp = "split"
        df = book.list_splits()
    elif args.type in {"transaction", "trn"}:
        tp = "transaction"
        df = book.list_transactions()

    df.reset_index(inplace=True)
    if not args.long:
        df = df[get_select_cols(tp)]

    if args.csv:
        print(df.to_csv(index=False))
    else:
        print(df.to_string(index=False))


def build_argparser(prog):
    parser = argparse.ArgumentParser(
            prog=prog,
            description="Extract entries from GnuCash data file."
            )
    parser.add_argument(
            "type",
            choices=["account", "act", "commodity", "cmdty", "price", "split", "sp", "transaction", "trn"],
            help="type of data to extract (account | commodity | price | split | transaction)",
            metavar="TYPE"
            )
    parser.add_argument(
            "file",
            nargs="?",
            default=sys.stdin.buffer,
            type=argparse.FileType("rb"),
            help="GnuCash data file (gzipped XML format)",
            metavar="FILE"
            )
    parser.add_argument("-l", "--long", action="store_true", help="list in long format")
    parser.add_argument("--csv", action="store_true", help="output in csv format")
    return parser


def get_select_cols(tp):
    return {
            "account": ["path", "toplevel", "code", "description", "cmd_space", "cmd_id"],
            "commodity": ["space", "id", "name", "quote_source"],
            "price": ["time", "cmd_space", "cmd_id", "crncy_space", "crncy_id", "source", "type", "value"],
            "split": [
                'trn_date', 'trn_description', 'trn_crncy_space', 'trn_crncy_id',
                'act_path', 'act_toplevel', 'act_code', 'act_cmd_space', 'act_cmd_id',
                'memo', 'reconciled', 'quantity', 'value',
                ],
            "transaction": ["date", "description", "crncy_space", "crncy_id"],
            }[tp]
