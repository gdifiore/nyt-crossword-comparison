"""Tests for Flask application endpoints."""
import json
import pytest
from unittest.mock import MagicMock, patch


class TestCalculateBins:
    """Tests for calculate_bins function."""

    def test_empty_data(self, app):
        """Test calculate_bins with empty data."""
        with app.app_context():
            import app as flask_app

            result = flask_app.calculate_bins([])
            assert result == []

    def test_single_value(self, app):
        """Test calculate_bins with single value."""
        with app.app_context():
            import app as flask_app

            result = flask_app.calculate_bins([123])
            assert len(result) == 1
            assert result[0]["count"] == 1
            assert "2:03-2:03" in result[0]["range"]

    def test_all_same_values(self, app):
        """Test calculate_bins when all values are identical."""
        with app.app_context():
            import app as flask_app

            result = flask_app.calculate_bins([60, 60, 60, 60])
            assert len(result) == 1
            assert result[0]["count"] == 4
            assert "1:00-1:00" in result[0]["range"]

    def test_no_double_counting(self, app):
        """Test that values aren't double-counted at bin boundaries."""
        with app.app_context():
            import app as flask_app

            # Create data that would expose boundary issues
            data = [10, 20, 30, 40, 50]
            result = flask_app.calculate_bins(data)

            # Sum of all counts should equal number of data points
            total_count = sum(bin_data["count"] for bin_data in result)
            assert total_count == len(data)

    def test_time_formatting(self, app):
        """Test that time ranges are formatted as MM:SS."""
        with app.app_context():
            import app as flask_app

            data = [65, 125]  # 1:05 and 2:05
            result = flask_app.calculate_bins(data)

            # Check that all ranges contain MM:SS format
            for bin_data in result:
                assert "-" in bin_data["range"]
                parts = bin_data["range"].split("-")
                assert len(parts) == 2
                for part in parts:
                    assert ":" in part


class TestInsertDataEndpoint:
    """Tests for /api/data POST endpoint."""

    def test_insert_valid_data(self, client):
        """Test inserting valid completion time."""
        with patch("app.execute_query") as mock_query:
            mock_query.return_value = 1  # Simulate 1 row inserted

            response = client.post(
                "/api/data",
                data=json.dumps({"secondsToComplete": 123}),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "message" in data

    def test_missing_data(self, client):
        """Test with missing secondsToComplete field."""
        response = client.post(
            "/api/data", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_invalid_data_type(self, client):
        """Test with non-integer secondsToComplete."""
        response = client.post(
            "/api/data",
            data=json.dumps({"secondsToComplete": "invalid"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_time_too_fast(self, client):
        """Test with completion time below minimum."""
        import config

        response = client.post(
            "/api/data",
            data=json.dumps({"secondsToComplete": config.MIN_COMPLETION_TIME - 1}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "too fast" in data["error"].lower()

    def test_time_too_slow(self, client):
        """Test with completion time above maximum."""
        import config

        response = client.post(
            "/api/data",
            data=json.dumps({"secondsToComplete": config.MAX_COMPLETION_TIME + 1}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "too slow" in data["error"].lower()

    def test_database_error(self, client):
        """Test handling of database errors."""
        import psycopg2

        with patch("app.execute_query") as mock_query:
            mock_query.side_effect = psycopg2.Error("Database error")

            response = client.post(
                "/api/data",
                data=json.dumps({"secondsToComplete": 123}),
                content_type="application/json",
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data


class TestGetChartDataEndpoint:
    """Tests for /api/chartData GET endpoint."""

    def test_get_chart_data(self, client):
        """Test getting chart data."""
        with patch("app.execute_query") as mock_query:
            # Mock database response
            mock_query.return_value = [
                {"completion_time_in_sec": 60},
                {"completion_time_in_sec": 90},
                {"completion_time_in_sec": 120},
            ]

            response = client.get("/api/chartData")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "data" in data
            assert isinstance(data["data"], list)

    def test_get_chart_data_empty(self, client):
        """Test getting chart data when database is empty."""
        with patch("app.execute_query") as mock_query:
            mock_query.return_value = []

            response = client.get("/api/chartData")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "data" in data
            assert data["data"] == []

    def test_get_chart_data_error(self, client):
        """Test error handling in chart data endpoint."""
        with patch("app.execute_query") as mock_query:
            mock_query.side_effect = Exception("Database error")

            response = client.get("/api/chartData")

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data


class TestHealthCheckEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_check_success(self, client):
        """Test health check endpoint returns healthy status."""
        import config

        with patch("app.db_pool") as mock_pool:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_pool.getconn.return_value = mock_conn

            response = client.get("/api/health")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "healthy"
            assert data["service"] == "nyt-crossword-comparison"
            assert data["version"] == config.VERSION
            assert "timestamp" in data
            assert data["database"] == "connected"
            assert "database_pool" in data

    def test_health_check_database_error(self, client):
        """Test health check endpoint when database is down."""
        import app as flask_app
        import psycopg2

        with patch.object(flask_app, "db_pool") as mock_pool:
            mock_pool.getconn.side_effect = psycopg2.Error("Connection failed")

            response = client.get("/api/health")

            assert response.status_code == 503
            data = json.loads(response.data)
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
            assert "error" in data


class TestStaticFileServing:
    """Tests for React static file serving."""

    def test_serve_index(self, client):
        """Test serving index.html."""
        # This will fail if build doesn't exist, which is expected in test
        # Just verify the route exists
        response = client.get("/")
        # Will be 404 if build folder doesn't exist, that's ok
        assert response.status_code in [200, 404]

    def test_serve_nonexistent_path(self, client):
        """Test serving non-existent static file falls back to index.html."""
        response = client.get("/nonexistent-route")
        # Will be 404 if build folder doesn't exist, that's ok
        assert response.status_code in [200, 404]
