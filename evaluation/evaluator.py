import time
import json
import os
import random
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TestResult:
    scenario_name: str
    queries_tested: int
    correct_classifications: int
    average_time: float
    total_time: float
    cache_hits: int


class Evaluator:    
    def __init__(self):
        self.test_queries_file = os.path.join("data", "test_queries.json")
        self.test_queries = self._load_test_queries()
        self.start_time = None
        
    def _load_test_queries(self):
        if os.path.exists(self.test_queries_file):
            with open(self.test_queries_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def _select_random_queries(self, count=10):
        all_queries = []
        for complexity, queries in self.test_queries.items():
            for q in queries:
                all_queries.append({
                    "query": q,
                    "true_complexity": complexity
                })
        return random.sample(all_queries, count)
    
    def _test_routing(self, router, queries, use_cache):
        results = []
        
        for q in queries:
            start = time.time()
            response = router.route_query_and_return_response(q["query"], use_cache=use_cache)
            elapsed = time.time() - start
            
            predicted = response.complexity
            correct = (predicted == q["true_complexity"])
            
            results.append({
                "time": elapsed,
                "correct": correct,
                "cached": response.cached
            })
        
        return results
    
    def _test_single_model(self, router, queries, model_level):
        times = []
        
        for q in queries:
            start = time.time()
            router.model.generate(q["query"], model_level)
            elapsed = time.time() - start
            times.append(elapsed)
        
        return times
    
    def _calculate_metrics(self, results, scenario_name):
        total_time = sum(r["time"] for r in results)
        correct = sum(1 for r in results if r["correct"])
        cached = sum(1 for r in results if r["cached"])
        
        return TestResult(
            scenario_name=scenario_name,
            queries_tested=len(results),
            correct_classifications=correct,
            average_time=total_time / len(results),
            total_time=total_time,
            cache_hits=cached
        )
       
    def _generate_report(self, results, test_queries):
        lines = []
        lines.append("SYSTEM EVALUATION REPORT")
        lines.append("="*60)
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total queries tested: {len(test_queries)}")
        
        # Query distribution
        complexity_count = {}
        for q in test_queries:
            c = q["true_complexity"]
            complexity_count[c] = complexity_count.get(c, 0) + 1
        
        lines.append("\nQuery Distribution:")
        for complexity, count in complexity_count.items():
            lines.append(f"  {complexity}: {count}")
        
        # Results summary
        lines.append("\nTest Results:")
        lines.append("-"*40)
        
        for r in results:
            lines.append(f"\n{r.scenario_name}:")
            lines.append(f"  Average Time: {r.average_time:.3f}s")
            lines.append(f"  Total Time: {r.total_time:.3f}s")
            
            if r.correct_classifications > 0:
                accuracy = (r.correct_classifications / r.queries_tested) * 100
                lines.append(f"  Accuracy: {accuracy:.1f}%")
            
            if r.cache_hits > 0:
                cache_rate = (r.cache_hits / r.queries_tested) * 100
                lines.append(f"  Cache Hit Rate: {cache_rate:.1f}%")
        
        # Performance comparison
        lines.append("\nPerformance Analysis:")
        lines.append("-"*40)
        
        normal_cache = results[0]
        normal_no_cache = results[1]
        
        # Cache improvement
        if normal_no_cache.average_time > 0:
            cache_improvement = ((normal_no_cache.average_time - normal_cache.average_time) / normal_no_cache.average_time) * 100
            lines.append(f"Cache Improvement: {cache_improvement:.1f}% faster")
        
        # Routing effectiveness
        advanced = results[2]
        if advanced.average_time > 0:
            routing_savings = ((advanced.average_time - normal_no_cache.average_time) / advanced.average_time) * 100
            lines.append(f"Routing Savings: {routing_savings:.1f}% faster than always using advanced model")
        
        lines.append("\n" + "="*60)
        
        # Print to console
        report_text = "\n".join(lines)
        print(report_text)
        
        return report_text
    
    def start_timer(self):
        self.start_time = time.time()
    
    def stop_timer(self):
        if self.start_time is None:
            return 0.0
        elapsed = time.time() - self.start_time
        self.start_time = None
        return elapsed
    
    def evaluate_system(self, router):
        print("Starting System Evaluation...")
        print("="*60)
        
        # Select random queries
        test_queries = self._select_random_queries(10)
        print(f"Selected {len(test_queries)} test queries")
        
        all_results = []
        
        # Test 1: With cache
        print("Running Test 1: Normal routing with cache")
        results = self._test_routing(router, test_queries, use_cache=True)
        all_results.append(self._calculate_metrics(results, "Normal (Cache ON)"))
        
        # Test 2: Without cache
        print("Running Test 2: Normal routing without cache")
        results = self._test_routing(router, test_queries, use_cache=False)
        all_results.append(self._calculate_metrics(results, "Normal (Cache OFF)"))
        
        # Test 3-5: Individual models
        for level, name in [("advanced", "Advanced"), ("medium", "Medium"), ("simple", "Simple")]:
            print(f"Running Test: {name} model only")
            times = self._test_single_model(router, test_queries, level)
            
            # Create TestResult for single model
            result = TestResult(
                scenario_name=f"{name} Model Only",
                queries_tested=len(times),
                correct_classifications=0,  # Not applicable
                average_time=sum(times) / len(times),
                total_time=sum(times),
                cache_hits=0
            )
            all_results.append(result)
        
        # Generate and save report
        report = self._generate_report(all_results, test_queries)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join("data", "evaluation_reports")
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, f"evaluation_{timestamp}.txt")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\nReport saved to: {report_file}")
        print("="*60)

