import streamlit as st
import json
import os
from datetime import datetime

from router.query_router import QueryRouter
from evaluation.evaluator import Evaluator
from config import Config


class DynamicRoutingUI:
    def __init__(self):
        """Initialize the UI components"""
        self.config = Config()
        self.router = QueryRouter()
        self.evaluator = Evaluator()
        self.setup_page_config()

    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Dynamic Routing System",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def render_sidebar(self):
        """Render sidebar with configuration options"""
        st.sidebar.title("Configuration")

        # Model Provider
        st.sidebar.subheader("Model Provider")
        model_provider = st.sidebar.selectbox(
            "Select Model Provider",
            ["gemini", "mock"],
            index=0 if self.config.MODEL_PROVIDER == "gemini" else 1
        )

        if model_provider != self.config.MODEL_PROVIDER:
            self.config.MODEL_PROVIDER = model_provider
            self.router = QueryRouter()
            st.sidebar.success(f"Switched to {model_provider} mode")

        # Model Level Selection
        st.sidebar.subheader("Model Level")
        model_level = st.sidebar.selectbox(
            "Select Model Level",
            ["auto", "simple", "medium", "advanced"],
            index=0
        )

        # Cache Settings
        st.sidebar.subheader("Cache Settings")
        cache_enabled = st.sidebar.checkbox(
            "Enable Cache",
            value=self.config.CACHE_ENABLED
        )
        self.config.CACHE_ENABLED = cache_enabled

        # Current Settings Display
        st.sidebar.subheader("Current Settings")
        st.sidebar.write(f"**Model Provider:** {self.config.MODEL_PROVIDER}")
        st.sidebar.write(f"**Model Level:** {model_level}")
        cache_status = 'Enabled' if self.config.CACHE_ENABLED else 'Disabled'
        st.sidebar.write(f"**Cache:** {cache_status}")

        # Store model level for use in query processing
        st.session_state.model_level = model_level

    def render_query_tab(self):
        """Render the main query tab"""
        st.subheader("Query Interface")

        # Query input
        query = st.text_area(
            "Enter your query:",
            placeholder="Type your question here...",
            height=100
        )

        # Options
        col1, col2 = st.columns([1, 4])

        with col1:
            send_button = st.button("Send Query", type="primary")

        with col2:
            show_details = st.checkbox("Show Response Details")

        # Process query
        if send_button and query.strip():
            with st.spinner("Processing query..."):
                try:
                    # Start timing
                    self.evaluator.start_timer()

                    # Get model level from session state
                    model_level = st.session_state.get('model_level', 'auto')

                    # Route query with specific model level if not auto
                    if model_level == 'auto':
                        result = self.router.route_query_and_return_response(
                            query
                        )
                    else:
                        # Use specific model level
                        response = self.router.model.generate(
                            query,
                            model_level
                        )
                        result = {
                            "query": query,
                            "response": response,
                            "complexity": model_level,
                            "model_name": self.router._get_model_name(
                                model_level
                                ),
                            "cached": False
                        }

                    # Stop timing
                    elapsed = self.evaluator.stop_timer()

                    # Display response
                    st.success("Query processed successfully!")

                    # Response content
                    st.subheader("Response:")
                    st.write(result["response"])

                    # Details if requested
                    if show_details:
                        st.subheader("Response Details:")

                        details_col1, details_col2 = st.columns(2)

                        with details_col1:
                            st.write(f"**Query:** {result['query']}")
                            st.write(f"**Complexity:** {result['complexity']}")
                            st.write(f"**Model Used:** {result['model_name']}")
                            level_mode = (
                                'Auto' if model_level == 'auto' else 'Manual'
                            )
                            st.write(f"**Level Mode:** {level_mode}")

                        with details_col2:
                            from_cache = 'Yes' if result['cached'] else 'No'
                            st.write(f"**From Cache:** {from_cache}")
                            st.write(f"**Processing Time:** {elapsed:.3f}s")
                            st.write(
                                f"**Response Length:** "
                                f"{len(result['response'])} characters"
                            )

                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")

        elif send_button and not query.strip():
            st.warning("Please enter a query before sending.")

    def render_evaluation_tab(self):
        """Render the evaluation results tab"""
        st.subheader("Evaluation Results")

        # Check for evaluation reports
        reports_dir = os.path.join("data", "evaluation_reports")

        if not os.path.exists(reports_dir):
            st.info("No evaluation reports found. Run an evaluation first.")
            return

        # Get latest report
        report_files = [
            f for f in os.listdir(reports_dir)
        ]

        if not report_files:
            st.info("No evaluation reports found.")
            return

        # Sort by modification time
        report_files.sort(
            key=lambda x: os.path.getmtime(
                os.path.join(reports_dir, x)
            ), reverse=True)

        # Display report selector
        selected_report = st.selectbox(
            "Select Report:",
            report_files,
            index=0
        )

        # Display report content
        report_path = os.path.join(reports_dir, selected_report)

        try:
            st.subheader(f"Report: {selected_report}")
            if selected_report.lower().endswith(".json"):
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_json = json.load(f)
                st.json(report_json)
            else:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                st.text(report_content)

            # Report metadata
            file_stats = os.stat(report_path)
            st.caption(f"Last modified: {datetime.fromtimestamp(
                file_stats.st_mtime
            )}")

        except Exception as e:
            st.error(f"Error reading report: {str(e)}")

    def render_test_queries_tab(self):
        """Render the test queries management tab"""
        st.subheader("Test Queries")

        # Load test queries
        test_queries_file = os.path.join("data", "test_queries.json")

        if not os.path.exists(test_queries_file):
            st.error("Test queries file not found!")
            return

        try:
            with open(test_queries_file, 'r', encoding='utf-8') as f:
                test_queries = json.load(f)

            # Display JSON content
            st.json(test_queries)

        except Exception as e:
            st.error(f"Error loading test queries: {str(e)}")

    def render_cache_tab(self):
        """Render the cache management tab"""
        st.subheader("Cache")

        # Load cache file
        cache_file = os.path.join("data", "cache", "query_cache.json")

        if not os.path.exists(cache_file):
            st.info("Cache file not found.")
            return

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # Display JSON content
            st.json(cache_data)

        except Exception as e:
            st.error(f"Error loading cache: {str(e)}")

    def render_tabs(self):
        """Render main application tabs"""
        tabs = st.tabs([
            "Query Interface",
            "Evaluation Results",
            "Test Queries",
            "Cache"
        ])

        with tabs[0]:
            self.render_query_tab()

        with tabs[1]:
            self.render_evaluation_tab()

        with tabs[2]:
            self.render_test_queries_tab()

        with tabs[3]:
            self.render_cache_tab()

    def render_header(self):
        """Render application header"""
        st.title("Dynamic Routing System")
        st.markdown("---")

    def run(self):
        """Main method to run the application"""
        self.render_header()
        self.render_sidebar()
        self.render_tabs()


def main():
    """Main application entry point"""
    app = DynamicRoutingUI()
    app.run()


if __name__ == "__main__":
    main()
