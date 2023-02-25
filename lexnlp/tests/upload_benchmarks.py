__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import argparse
import csv
import sys
from datetime import datetime
from typing import Callable, List, Dict

from elasticsearch import Elasticsearch, helpers

from lexnlp.tests import lexnlp_tests


def safe():
    def dec(func):
        def _dec(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError:
                return None

        return _dec

    return dec


safe_int = safe()(int)

safe_float = safe()(float)


def process_data(csv_file_name: str, index: str, process_func: Callable[[List[Dict]], int]):
    total = 0
    with open(csv_file_name, 'r', encoding='utf8') as f:
        r = csv.DictReader(f)
        actions = []

        for row in r:
            es_op = {
                '_index': index,
                '_type': 'benchmark',
                '_source': {
                    'date': row['date'],
                    'function': row['function'],
                    'text_size_chars': safe_int(row['text_size_chars']),
                    'exec_time_sec': safe_float(row['exec_time_sec']),
                    'max_memory_usage_mb': safe_float(row['max_memory_usage_mb']),
                    'sys_cpu_count': safe_int(row['sys_cpu_count']),
                    'sys_cpu_freq': safe_float(row['sys_cpu_freq']),
                    'sys_ram_total': safe_int(row['sys_ram_total']),
                    'sys_os': row['sys_os'],
                    'sys_node_name': row['sys_node_name'],
                    'sys_arch': row['sys_arch']
                }
            }

            if len(actions) < 50:
                actions.append(es_op)
            else:
                process_func(actions)
                total = total + len(actions)
                actions = []
    if len(actions) > 0:
        total = total + len(actions)
        process_func(actions)
    return total


def parse_args(args):
    parser = argparse.ArgumentParser(description='Upload benchmarks to ElasticSearch')
    parser.add_argument('--csv-file', dest='csv_file', type=str, default=lexnlp_tests.FN_BENCHMARKS,
                        help='Path/name of csv file with benchmarks')
    parser.add_argument('--es-url', dest='url', type=str, default='localhost:9200',
                        help='ElasticSearch host:port/path')
    parser.add_argument('--es-username', dest='username', type=str, default=None,
                        help='ElasticSearch Username')
    parser.add_argument('--es-password', dest='password', type=str, default=None,
                        help='ElasticSearch Password')
    parser.add_argument('--es-use-ssl', dest='use_ssl', type=bool, default=False,
                        help='ElasticSearch use SSL')
    parser.add_argument('--es-verify-certs', dest='verify_certs', type=bool, default=True,
                        help='ElasticSearch verify_certs')
    parser.add_argument('--es-index-prefix', dest='index_prefix', type=str, default='benchmarks',
                        help='ElasticSearch index prefix')

    args = parser.parse_args(args)
    print('Benchmark file: {0}'.format(args.csv_file))
    print('ElasticSearch URL: {0}'.format(args.url))
    return args


def build_index_name(index_prefix: str, d: datetime.date) -> str:
    today = d.strftime('%Y-%m-%d')
    index = '{0}-{1}'.format(index_prefix, today)
    print('Index: {0}'.format(index))
    return index


if __name__ == "__main__":

    cmd_args = parse_args(sys.argv[1:])
    index_name = build_index_name(cmd_args.index_prefix, datetime.utcnow().date())

    es = Elasticsearch(hosts=[cmd_args.url],
                       http_auth=(cmd_args.username, cmd_args.password) if cmd_args.username else None,
                       use_ssl=cmd_args.use_ssl,
                       verify_certs=cmd_args.verify_certs)

    processed = process_data(cmd_args.csv_file, index=index_name,
                             process_func=lambda actions: helpers.bulk(es, actions))
    print('Indexed {0} benchmarks'.format(processed))
