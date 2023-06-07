import cProfile
import pstats
from pstats import SortKey
from datetime import timedelta
from smarterbombing.aggregrator.damage_graph_aggregator import DamageGraphAggregator
from smarterbombing.parsing.combat_log_parser import parse_combat_log_line

def _filter_none(event: dict):
    return event is not None

def _apply_character_name(event: dict):
    event['character'] = 'Ageliten'
    return event

def run_benchmark(aggregator: DamageGraphAggregator):
    aggregator.aggregate(10)

def run_benchmark_with_file(log_file: str, output_file: str = 'benchmark_stats.txt'):
    with open(log_file, 'r', encoding='UTF8') as file:
        events = filter(_filter_none, map(parse_combat_log_line, file.readlines()))
        events = map(_apply_character_name, events)

    aggregator = DamageGraphAggregator(timedelta(minutes=5))
    aggregator.append_events(events)

    global_env = {}

    local_env = {}
    local_env['run_benchmark'] = run_benchmark
    local_env['aggregator'] = aggregator

    cProfile.runctx('run_benchmark(aggregator)', global_env, local_env, output_file)

run_benchmark_with_file('benchmark/data/sample_log_97000.txt',
                        'benchmark/results/parse_combat_log_line_97000.txt')

perf_results = pstats.Stats('benchmark/results/parse_combat_log_line_97000.txt')
perf_results.sort_stats(SortKey.CUMULATIVE)
perf_results.print_stats(16)

perf_results.sort_stats(SortKey.TIME)
perf_results.print_stats(16)
