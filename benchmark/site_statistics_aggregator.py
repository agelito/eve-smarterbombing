import cProfile
import pstats
from pstats import SortKey
from smarterbombing.aggregrator.site_statistics_aggregator import SiteStatisticsAggregator
from smarterbombing.logs.log_reader import LogReader

def _run_benchmark(aggregator: SiteStatisticsAggregator):
    aggregator.aggregate()

def _run_benchmark_with_file(log_file: str, output_file: str = 'benchmark_stats.txt'):
    friendly_characters = ['Ageliten', 'Fresar Ronunken', 'Mr Vesuvio', 'Yeol Ramyun']

    log_reader = LogReader({
        'path': log_file,
        'character': 'Fresar Ronuken',
    }, friendly_characters, [])
    log_reader.open()

    events = log_reader.read_log_events()

    aggregator = SiteStatisticsAggregator(30)
    aggregator.append_events(events)

    global_env = {}

    local_env = {}
    local_env['run_benchmark'] = _run_benchmark
    local_env['aggregator'] = aggregator

    cProfile.runctx('run_benchmark(aggregator)', global_env, local_env, output_file)

_run_benchmark_with_file('benchmark/data/sample_log_97000.txt',
                         'benchmark/results/parse_combat_log_line_97000.txt')

perf_results = pstats.Stats('benchmark/results/parse_combat_log_line_97000.txt')
perf_results.sort_stats(SortKey.CUMULATIVE)
perf_results.print_stats(16)

perf_results.sort_stats(SortKey.TIME)
perf_results.print_stats(16)
