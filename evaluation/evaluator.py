import time
import json
import os
from datetime import datetime


class Evaluator:
    def __init__(self):
        self.test_queries_file = os.path.join("data", "test_queries.json")
        self.test_queries = self._load_test_queries()

    def _load_test_queries(self):
        if os.path.exists(self.test_queries_file):
            with open(self.test_queries_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _get_test_set(self):
        return self.test_queries.get("queries")

    def _calculate_accuracy(self, queries, results):
        correct = 0
        for i, query_data in enumerate(queries):
            true_label = query_data["true_label"]
            predicted_label = results[i]["complexity"]
            if true_label == predicted_label:
                correct += 1
        return (correct / len(queries)) * 100

    def test_system(self, router):
        queries = self._get_test_set()
        results = []

        print("Testing Routing System...")
        start_time = time.time()

        for query_data in queries:
            query = query_data["text"]
            query_start = time.time()
            response = router.route_query_and_return_response(
                query,
                use_cache=True
                )
            
            query_time = time.time() - query_start
            
            results.append({
                "query": query[:50] + "...",
                "response": response["response"][:50] + "...",
                "complexity": response["complexity"],
                "time": query_time
            })
            
            # Sleep for advanced model to avoid rate limits
            if response["complexity"] == "advanced":
                print("Waiting 30 seconds for advanced model rate limit...")
                time.sleep(30)

        total_time = time.time() - start_time

        accuracy = self._calculate_accuracy(queries, results)

        return {
            "test_type": "Routing System",
            "queries_tested": len(queries),
            "total_time": total_time,
            "average_time": total_time / len(queries),
            "details": results,
            "accuracy": accuracy
        }

    def test_single_model(self, router, model_level):
        queries = self._get_test_set()
        results = []

        print(f"Testing {model_level.title()} Model...")
        start_time = time.time()

        for query_data in queries:
            query = query_data["text"]
            query_start = time.time()
            response = router.model.generate(query, model_level)
            query_time = time.time() - query_start
            
            results.append({
                "query": query[:50] + "...",
                "response": response[:50] + "...",
                "complexity": model_level,
                "time": query_time
            })
            
            # Sleep for advanced model to avoid rate limits
            if model_level == "advanced":
                print("Waiting 30 seconds for advanced model rate limit...")
                time.sleep(30)

        total_time = time.time() - start_time

        return {
            "test_type": f"{model_level.title()} Model",
            "queries_tested": len(queries),
            "total_time": total_time,
            "average_time": total_time / len(queries),
            "details": results,
            "accuracy": None  # Not applicable
        }

    def evaluate_system(self, router):
        print("="*60)
        print("EVALUATION START")
        print("="*60)

        all_results = []

        all_results.append(self.test_system(router))

        for level in ["simple", "medium", "advanced"]:
            all_results.append(self.test_single_model(router, level))

        self._print_results(all_results)
        self._save_results(all_results)

        print("="*60)
        print("EVALUATION COMPLETE")
        print("="*60)

    def _print_results(self, results):
        print("RESULTS SUMMARY")
        print("-"*40)

        for result in results:
            print(f"{result['test_type']}:")
            print(f"  Queries: {result['queries_tested']}")
            print(f"  Total Time: {result['total_time']:.2f}s")
            print(f"  Average Time: {result['average_time']:.2f}s")
            accuracy_text = (
                f"{result['accuracy']:.1f}%"
                if result['accuracy'] is not None else "N/A"
            )
            print(f"  Accuracy: {accuracy_text}")

        routing_avg = results[0]["average_time"]
        advanced_avg = results[3]["average_time"]

        savings = ((advanced_avg - routing_avg) / advanced_avg) * 100
        print(
            f"Routing is {savings:.1f}% faster than using the Advanced "
            "model for all queries"
        )

    def _save_results(self, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join("data", "evaluation_reports")
        os.makedirs(report_dir, exist_ok=True)

        report_file = os.path.join(report_dir, f"evaluation_{timestamp}.json")

        with open(report_file, 'w') as f:
            # dump(content, file path, space=2, keep non-ASCII chars)
            json.dump({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "results": results
            }, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {report_file}")

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        if self.start_time is None:
            return 0.0

        elapsed = time.time() - self.start_time
        self.start_time = None
        return elapsed
