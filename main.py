import os
import sys
from router.query_router import QueryRouter
from models.gemini_models import GeminiModels
from evaluation.evaluator import Evaluator
from config import Config

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), ".")
    )
)


class DynamicRoutingApp:
    def __init__(self):
        self.config = Config()
        self.router = QueryRouter()
        self.evaluator = Evaluator()
        self.running = True

    def print_header(self):
        print("="*50)
        print("MODEL_PROVIDER: ", self.config.MODEL_PROVIDER)
        print("CACHE_ENABLED: ", self.config.CACHE_ENABLED)
        print("FALLBACK_ENABLED: ", self.config.FALLBACK_ENABLED)
        print("MAX_RETRIES: ", self.config.MAX_RETRIES)
        print("="*50)

        print("type 'exit' to Quit application")
        print("type 'evaluate' to run evaluation")
        print("type 'list' to show all available LLMs")

        print("="*50)

    def process_query(self, query: str):
        self.evaluator.start_timer()
        result = self.router.route_query_and_return_response(query)
        elapsed = self.evaluator.stop_timer()
        self.display_result(result, elapsed)

    def display_result(self, result, elapsed_time: float):
        print("-"*50)
        print("query: ", result["query"])
        print("complexity: ", result["complexity"])
        print("model: ", result["model_name"])
        print("from cache: ", result["cached"])
        print(f"Time: {elapsed_time:.3f}s")
        print("response: ", result["response"])
        print("-"*50)

    def handle_command(self, command: str):
        if command == "evaluate":
            self.evaluator.evaluate_system(self.router)
            self.running = False
            print("Exiting application")
            print("="*50)

        elif command == "exit":
            self.running = False
            print("Exiting application")
            print("="*50)

        elif command == "list":
            GeminiModels().Print_all_available_Gemini_models()

        else:
            self.process_query(command)

    def run(self):
        self.print_header()
        while self.running:
            query = input("Query> ").strip()
            if query:
                self.handle_command(query)


def main():
    app = DynamicRoutingApp()
    app.run()


if __name__ == "__main__":
    main()
