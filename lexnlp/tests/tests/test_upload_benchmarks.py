"""Unit tests for routines for uploading benchmarks to ElasticSearch.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
import tempfile
from datetime import datetime

from unittest import TestCase

from lexnlp.tests import lexnlp_tests, upload_benchmarks


class TestBenchmark(TestCase):

    def test_safe_convert(self):
        self.assertIsNone(upload_benchmarks.safe_int("ggg"))

    def test_process_data(self):
        def fff():
            print("fff")

        _handle, benchmark_file = tempfile.mkstemp()
        try:
            for _i in range(55):
                lexnlp_tests.benchmark(lexnlp_tests.build_extraction_func_name(fff), fff, benchmark_file=benchmark_file)
            res = []

            # pylint: disable=unnecessary-lambda
            upload_benchmarks.process_data(benchmark_file, 'index2',
                                           lambda actions: res.extend(actions))

            d1 = res[0]
            self.assertEqual('fff(text)', d1['_source']['function'])
        finally:
            if benchmark_file:
                os.remove(benchmark_file)

    def test_parse_args(self):
        args = ['--es-url=elk-a.contraxsuite.com:443/es',
                '--es-username=benchmark',
                '--es-password=pass',
                '--es-use-ssl=true',
                '--es-verify-certs=true',
                '--es-index-prefix=benchmarks']
        cmd_args = upload_benchmarks.parse_args(args)
        self.assertEqual(lexnlp_tests.FN_BENCHMARKS, cmd_args.csv_file)
        self.assertEqual('elk-a.contraxsuite.com:443/es', cmd_args.url)
        self.assertEqual('benchmark', cmd_args.username)
        self.assertEqual(True, cmd_args.use_ssl)
        self.assertEqual(True, cmd_args.verify_certs)
        self.assertEqual('benchmarks', cmd_args.index_prefix)

    def test_build_index_name(self):
        index_prefix = 'benchmarks'
        index = upload_benchmarks.build_index_name(index_prefix, datetime(year=2017, month=10, day=22))
        self.assertEqual('benchmarks-2017-10-22', index)
