#!/usr/bin/env python
"""
Benchmark script to measure performance before and after optimization.
Run this script to get precise timing measurements.

Usage:
    python profiling/benchmark.py [function_name] [iterations]
    
Examples:
    python profiling/benchmark.py sanitize_html 1000
    python profiling/benchmark.py get_signature_number 500
"""

import os
import sys
import time
import statistics
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pytition.settings.test')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pytition'))
django.setup()

from django.contrib.auth import get_user_model
from petition.models import Organization, Petition, PytitionUser, Signature
from petition.helpers import sanitize_html


def benchmark_function(func, args=(), kwargs=None, iterations=100, warmup=10):
    """
    Benchmark a function with precise timing.
    
    Returns dict with: min, max, mean, median, stdev, total
    """
    if kwargs is None:
        kwargs = {}
    
    # Warmup runs (not measured)
    for _ in range(warmup):
        func(*args, **kwargs)
    
    # Measured runs
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        'iterations': iterations,
        'min': min(times),
        'max': max(times),
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'total': sum(times),
        'times': times
    }


def print_benchmark_results(name, results):
    """Pretty print benchmark results."""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: {name}")
    print(f"{'='*60}")
    print(f"  Iterations: {results['iterations']}")
    print(f"  Total time: {results['total']*1000:.4f} ms")
    print(f"  Mean:       {results['mean']*1000:.4f} ms")
    print(f"  Median:     {results['median']*1000:.4f} ms")
    print(f"  Min:        {results['min']*1000:.4f} ms")
    print(f"  Max:        {results['max']*1000:.4f} ms")
    print(f"  Std Dev:    {results['stdev']*1000:.4f} ms")
    print(f"{'='*60}")


def compare_results(before, after, name=""):
    """Compare two benchmark results and show improvement."""
    improvement = ((before['mean'] - after['mean']) / before['mean']) * 100
    speedup = before['mean'] / after['mean'] if after['mean'] > 0 else float('inf')
    
    print(f"\n{'='*60}")
    print(f"COMPARISON: {name}")
    print(f"{'='*60}")
    print(f"  BEFORE: {before['mean']*1000:.4f} ms (mean)")
    print(f"  AFTER:  {after['mean']*1000:.4f} ms (mean)")
    print(f"  ")
    print(f"  Improvement: {improvement:.2f}%")
    print(f"  Speedup:     {speedup:.2f}x")
    print(f"{'='*60}")
    
    return {'improvement_percent': improvement, 'speedup': speedup}


# ============================================================
# BENCHMARK FUNCTIONS - Add your benchmarks here
# ============================================================

def benchmark_sanitize_html(iterations=1000):
    """Benchmark the sanitize_html function."""
    # Test data
    html_samples = [
        '<p>Simple paragraph with <strong>bold</strong> text</p>',
        '<div onclick="alert(1)"><script>alert("xss")</script>Content</div>',
        '<p>' + 'Lorem ipsum dolor sit amet. ' * 100 + '</p>',
    ]
    
    def run_sanitize():
        for html in html_samples:
            sanitize_html(html)
    
    results = benchmark_function(run_sanitize, iterations=iterations)
    print_benchmark_results("sanitize_html", results)
    return results


def benchmark_signature_count(iterations=500):
    """Benchmark petition signature counting."""
    # Setup
    User = get_user_model()
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0)
    
    # Create test data
    User.objects.filter(username='benchuser').delete()
    user = User.objects.create_user('benchuser', password='test')
    pu = PytitionUser.objects.get(user=user)
    
    petition = Petition.objects.create(
        title='Benchmark Petition',
        text='Test',
        user=pu
    )
    
    # Create signatures
    for i in range(200):
        Signature.objects.create(
            first_name=f'First{i}',
            last_name=f'Last{i}',
            email=f'bench{i}@test.com',
            petition=petition,
            confirmed=(i % 2 == 0)
        )
    
    def run_count():
        petition.get_signature_number(confirmed=True)
        petition.get_signature_number(confirmed=False)
        petition.get_signature_number()
    
    results = benchmark_function(run_count, iterations=iterations)
    print_benchmark_results("get_signature_number", results)
    
    # Cleanup
    petition.delete()
    User.objects.filter(username='benchuser').delete()
    
    return results


def benchmark_petition_queries(iterations=200):
    """Benchmark petition database queries."""
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0)
    
    # Setup test data
    User = get_user_model()
    User.objects.filter(username__startswith='qbench').delete()
    
    users = []
    for i in range(5):
        user = User.objects.create_user(f'qbench{i}', password='test')
        users.append(user)
    
    for i in range(30):
        pu = PytitionUser.objects.get(user=users[i % 5])
        Petition.objects.create(
            title=f'Query Bench {i}',
            text='Test content ' * 50,
            user=pu,
            published=(i % 2 == 0)
        )
    
    def run_queries():
        # Typical view queries
        list(Petition.objects.filter(published=True)[:10])
        list(Petition.objects.filter(title__icontains='Bench')[:5])
        Petition.objects.filter(published=True).count()
    
    results = benchmark_function(run_queries, iterations=iterations)
    print_benchmark_results("petition_queries", results)
    
    # Cleanup
    Petition.objects.filter(title__startswith='Query Bench').delete()
    User.objects.filter(username__startswith='qbench').delete()
    
    return results


def main():
    """Run benchmarks."""
    print("=" * 60)
    print("PYTITION BENCHMARK SUITE")
    print("=" * 60)
    
    benchmarks = {
        'sanitize_html': benchmark_sanitize_html,
        'signature_count': benchmark_signature_count,
        'petition_queries': benchmark_petition_queries,
    }
    
    if len(sys.argv) > 1:
        name = sys.argv[1]
        iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        
        if name in benchmarks:
            benchmarks[name](iterations=iterations)
        elif name == 'all':
            for bname, bfunc in benchmarks.items():
                try:
                    bfunc()
                except Exception as e:
                    print(f"Error in {bname}: {e}")
        else:
            print(f"Unknown benchmark: {name}")
            print(f"Available: {', '.join(benchmarks.keys())}, all")
    else:
        print("Usage: python profiling/benchmark.py [benchmark_name] [iterations]")
        print(f"Available benchmarks: {', '.join(benchmarks.keys())}, all")
        print("\nRunning all benchmarks with default iterations...")
        for bname, bfunc in benchmarks.items():
            try:
                bfunc()
            except Exception as e:
                print(f"Error in {bname}: {e}")


if __name__ == '__main__':
    main()
