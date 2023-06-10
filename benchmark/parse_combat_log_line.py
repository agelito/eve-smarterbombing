import cProfile
import pstats
from pstats import SortKey
from smarterbombing.parsing.combat_log_parser import parse_combat_log_line

def _run_benchmark(lines):
    list(map(parse_combat_log_line, lines))

def _run_benchmark_with_file(log_file: str, output_file: str = 'benchmark_stats.txt'):
    with open(log_file, 'r', encoding='UTF8') as file:
        lines = file.readlines()

    global_env = {}

    local_env = {}
    local_env['run_benchmark'] = _run_benchmark
    local_env['lines'] = lines

    cProfile.runctx('run_benchmark(lines)', global_env, local_env, output_file)

_run_benchmark_with_file('benchmark/data/sample_log_97000.txt',
                        'benchmark/results/parse_combat_log_line_97000.pst')

perf_results = pstats.Stats('benchmark/results/parse_combat_log_line_97000.pst')
perf_results.sort_stats(SortKey.CUMULATIVE)

perf_results.print_stats()
perf_results.print_callers(16)
