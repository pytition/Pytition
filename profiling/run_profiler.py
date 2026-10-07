#!/usr/bin/env python
"""
Profiling script for Pytition project.
This script runs selected tests/scenarios with cProfile and generates reports.

Usage:
    python profiling/run_profiler.py [scenario]
    
Scenarios:
    sanitize    - Profile HTML sanitization (default)
    models      - Profile model operations
    signatures  - Profile signature creation
    queries     - Profile database queries
    all         - Run all scenarios
"""

import cProfile
import pstats
import io
import os
import sys
import django
import time
from pstats import SortKey

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pytition.settings.test')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pytition'))
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from petition.models import Organization, Petition, PytitionUser, Signature, Permission
from petition.helpers import sanitize_html, get_client_ip


def setup_test_data():
    """Create test data for profiling."""
    User = get_user_model()
    
    # Cleanup
    Signature.objects.all().delete()
    Petition.objects.all().delete()
    Organization.objects.all().delete()
    User.objects.all().delete()
    
    # Create users
    users = []
    for i in range(10):
        user = User.objects.create_user(f'user{i}', password='testpass', email=f'user{i}@test.com')
        users.append(user)
    
    # Create organizations
    orgs = []
    for i in range(5):
        org = Organization.objects.create(name=f'Organization{i}')
        orgs.append(org)
    
    # Create petitions
    petitions = []
    for i in range(50):
        pu = PytitionUser.objects.get(user=users[i % 10])
        petition = Petition.objects.create(
            title=f'Test Petition {i}',
            text=f'<p>This is test petition number {i} with some <strong>HTML</strong> content.</p>',
            user=pu,
            published=True
        )
        petitions.append(petition)
    
    # Create signatures
    for petition in petitions[:10]:
        for j in range(100):
            Signature.objects.create(
                first_name=f'Signer{j}',
                last_name=f'Test{j}',
                email=f'signer{j}_{petition.id}@test.com',
                petition=petition,
                confirmed=True
            )
    
    return users, orgs, petitions


def scenario_sanitize_html():
    """
    Profile sanitize_html function - potential bottleneck.
    This function uses lxml to clean HTML and remove XSS attacks.
    """
    html_samples = [
        '<p>Simple paragraph</p>',
        '<div onclick="alert(1)">Malicious <script>alert("xss")</script> content</div>',
        '<p>' + 'Lorem ipsum dolor sit amet. ' * 500 + '</p>',  # Large content
        '<table><tr><td>' + '</td><td>'.join(['cell'] * 50) + '</td></tr></table>',
        '<div>' + '<span style="color:red;">nested content </span>' * 200 + '</div>',
    ]
    
    results = []
    for iteration in range(200):  # Run multiple times for accuracy
        for html in html_samples:
            result = sanitize_html(html)
            results.append(len(result))
    return results


def scenario_model_operations():
    """Profile model CRUD operations."""
    User = get_user_model()
    
    # Cleanup first
    Signature.objects.all().delete()
    Petition.objects.filter(title__startswith='Profile Test').delete()
    User.objects.filter(username__startswith='profuser').delete()
    
    results = []
    
    # Create operations
    for i in range(50):
        user = User.objects.create_user(f'profuser{i}', password='test', email=f'prof{i}@test.com')
        pu = PytitionUser.objects.get(user=user)
        petition = Petition.objects.create(
            title=f'Profile Test {i}',
            text='Test content ' * 100,
            user=pu
        )
        results.append(petition.id)
    
    # Read operations
    for _ in range(100):
        petitions = list(Petition.objects.filter(title__startswith='Profile Test')[:25])
        results.append(len(petitions))
    
    # Update operations
    petitions = Petition.objects.filter(title__startswith='Profile Test')
    for p in petitions[:25]:
        p.title = p.title + ' Updated'
        p.save()
    
    return results


def scenario_signature_creation():
    """Profile signature creation - often a bottleneck due to validation."""
    User = get_user_model()
    
    # Cleanup
    User.objects.filter(username='sigprofuser').delete()
    
    # Setup
    user = User.objects.create_user('sigprofuser', password='test', email='sigprof@test.com')
    pu = PytitionUser.objects.get(user=user)
    petition = Petition.objects.create(
        title='Signature Profile Test',
        text='Test content for signature profiling',
        user=pu,
        published=True
    )
    
    results = []
    for i in range(300):  # Create many signatures
        sig = Signature.objects.create(
            first_name=f'First{i}',
            last_name=f'Last{i}',
            email=f'sig{i}@proftest.com',
            petition=petition
        )
        results.append(sig.id)
    
    # Query signatures multiple times
    for _ in range(100):
        count = petition.get_signature_number(confirmed=False)
        results.append(count)
    
    return results


def scenario_petition_queries():
    """Profile complex petition queries."""
    from django.db.models import Count, Q
    
    setup_test_data()
    
    results = []
    
    for _ in range(50):
        # Complex query with filtering and related data
        petitions = Petition.objects.filter(
            published=True,
            moderated=False
        ).select_related('user', 'org').prefetch_related('signature_set')[:20]
        
        for p in petitions:
            # Access related data - triggers lazy loading if not prefetched
            sig_count = p.signature_set.count()
            owner = p.owner_name
            results.append(sig_count)
        
        # Aggregation queries
        stats = Petition.objects.aggregate(
            total=Count('id'),
            published=Count('id', filter=Q(published=True))
        )
        results.append(stats['total'])
        
        # Search-like query
        search_results = Petition.objects.filter(
            Q(title__icontains='test') | Q(text__icontains='petition')
        ).filter(published=True)[:10]
        results.append(len(list(search_results)))
    
    return results


def run_profiler(scenario_func, scenario_name):
    """Run cProfile on a scenario and generate report."""
    print(f"\n{'='*70}")
    print(f"PROFILING: {scenario_name}")
    print(f"{'='*70}")
    
    profiler = cProfile.Profile()
    
    # Run with profiling
    profiler.enable()
    start_time = time.time()
    result = scenario_func()
    end_time = time.time()
    profiler.disable()
    
    elapsed = end_time - start_time
    print(f"\n>>> Total execution time: {elapsed:.4f} seconds")
    print(f">>> Operations completed: {len(result)}")
    
    # Generate stats
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats(SortKey.CUMULATIVE)
    
    # Print top 30 functions by cumulative time
    print(f"\n{'─'*70}")
    print(f"TOP 30 FUNCTIONS BY CUMULATIVE TIME:")
    print(f"{'─'*70}")
    stats.print_stats(30)
    
    # Also show by total time (time spent in function itself)
    print(f"\n{'─'*70}")
    print(f"TOP 15 FUNCTIONS BY TOTAL TIME (excluding subcalls):")
    print(f"{'─'*70}")
    stats.sort_stats(SortKey.TIME)
    stats.print_stats(15)
    
    # Save to file for snakeviz visualization
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    profile_file = os.path.join(results_dir, f'{scenario_name}.prof')
    profiler.dump_stats(profile_file)
    
    print(f"\n>>> Profile saved to: {profile_file}")
    print(f">>> Visualize with: pdm run snakeviz {profile_file}")
    
    return stats, elapsed


def main():
    """Main entry point."""
    scenarios = {
        'sanitize': ('HTML Sanitization (sanitize_html)', scenario_sanitize_html),
        'models': ('Model CRUD Operations', scenario_model_operations),
        'signatures': ('Signature Creation', scenario_signature_creation),
        'queries': ('Database Queries', scenario_petition_queries),
    }
    
    # Parse command line
    if len(sys.argv) > 1:
        scenario_key = sys.argv[1]
        if scenario_key == 'all':
            selected = list(scenarios.keys())
        elif scenario_key in scenarios:
            selected = [scenario_key]
        else:
            print(f"Unknown scenario: {scenario_key}")
            print(f"Available scenarios: {', '.join(scenarios.keys())}, all")
            sys.exit(1)
    else:
        selected = ['sanitize']  # Default
    
    print("=" * 70)
    print("PYTITION PROFILER - Time Profiling")
    print("=" * 70)
    print(f"Selected scenarios: {', '.join(selected)}")
    
    # Run Django migrations for test DB
    from django.core.management import call_command
    print("\nSetting up test database...")
    call_command('migrate', '--run-syncdb', verbosity=0)
    print("Database ready.\n")
    
    results = {}
    for key in selected:
        name, func = scenarios[key]
        try:
            stats, elapsed = run_profiler(func, key)
            results[key] = {'time': elapsed, 'status': 'OK'}
        except Exception as e:
            import traceback
            print(f"Error in {key}: {e}")
            traceback.print_exc()
            results[key] = {'time': 0, 'status': f'ERROR: {e}'}
    
    # Summary
    print("\n" + "=" * 70)
    print("PROFILING SUMMARY")
    print("=" * 70)
    for key, data in results.items():
        status_icon = "✓" if data['status'] == 'OK' else "✗"
        print(f"  {status_icon} {key}: {data['time']:.4f}s - {data['status']}")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Review the output above to identify bottlenecks")
    print("2. Use snakeviz for visual analysis:")
    print("   pdm run snakeviz profiling/results/<scenario>.prof")
    print("3. Focus on functions with highest cumulative/total time")
    print("=" * 70)


if __name__ == '__main__':
    main()
