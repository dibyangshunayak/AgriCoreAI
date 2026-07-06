# =====================================================================
# FILE: backend/test_planner_dag.py
# DESCRIPTION: Unit tests for Tool Registry, Planner DAG generation,
#              and topological sorting logic.
# =====================================================================

import sys
from pathlib import Path

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

import unittest
from unittest.mock import patch, MagicMock
from app.tools.registry import registry
from app.services.planner import generate_execution_plan
from app.agents.coordinator_agent import normalize_steps, topological_sort, get_status_for_step


class TestToolRegistry(unittest.TestCase):
    def test_registry_registration(self):
        """Test that tools are registered and retrievable."""
        weather_tool = registry.get_tool("weather_api")
        self.assertIsNotNone(weather_tool)
        self.assertEqual(weather_tool.name, "weather_api")
        
        geocode_tool = registry.get_tool("reverse_geocode")
        self.assertIsNotNone(geocode_tool)
        self.assertEqual(geocode_tool.name, "reverse_geocode")

    def test_registry_metadata(self):
        """Test that registry metadata format contains names and descriptions."""
        meta = registry.get_tools_metadata()
        names = [m["name"] for m in meta]
        self.assertIn("weather_api", names)
        self.assertIn("reverse_geocode", names)


class TestPlannerDAG(unittest.TestCase):
    @patch("app.services.planner.generate_text")
    def test_planner_reasoning_and_dag(self, mock_generate_text):
        """Test that the planner generates a proper execution DAG."""
        mock_response = """{
            "reasoning": "Farmer wants to check irrigation. Need weather forecast to inspect rain, and crop details.",
            "steps": [
                {"id": "step_1", "agent": "weather", "tool": "weather_api", "depends_on": [], "action": "Fetch weather forecast"},
                {"id": "step_2", "agent": "crop", "tool": null, "depends_on": ["step_1"], "action": "Fetch crop guidelines and combine with weather"}
            ],
            "required_data": ["gps_coordinates"],
            "response_tone": "scientific"
        }"""
        mock_generate_text.return_value = mock_response

        plan = generate_execution_plan(
            user_query="Should I irrigate my tomatoes tomorrow?",
            gps_available=True
        )

        self.assertIn("reasoning", plan)
        self.assertEqual(len(plan["steps"]), 2)
        self.assertEqual(plan["steps"][0]["agent"], "weather")
        self.assertEqual(plan["steps"][1]["depends_on"], ["step_1"])

    def test_step_normalization_and_sorting(self):
        """Test normalization and topological sorting of steps."""
        legacy_steps = [
            {"step": 2, "agent": "crop", "depends_on": [1]},
            {"step": 1, "agent": "weather", "depends_on": []}
        ]
        
        normalized = normalize_steps(legacy_steps)
        self.assertEqual(normalized[0]["id"], "step_2")
        self.assertEqual(normalized[0]["depends_on"], ["step_1"])
        
        sorted_steps = topological_sort(normalized)
        # step_1 must come before step_2 because step_2 depends on step_1
        self.assertEqual(sorted_steps[0]["id"], "step_1")
        self.assertEqual(sorted_steps[1]["id"], "step_2")

    def test_status_mapping(self):
        """Test that correct status strings are mapped to agents."""
        weather_step = {"agent": "weather"}
        disease_step = {"agent": "disease"}
        
        self.assertEqual(get_status_for_step(weather_step, False), "Checking weather...")
        self.assertEqual(get_status_for_step(disease_step, True), "Analyzing image...")
        self.assertEqual(get_status_for_step(disease_step, False), "Consulting disease expert...")


if __name__ == "__main__":
    unittest.main()
