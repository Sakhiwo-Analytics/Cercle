import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

# Mock authentication middleware
@pytest.fixture(autouse=True)
def mock_auth():
    with patch("app.api.deps.get_current_user") as mock:
        mock.return_value = {
            "id": "user-123",
            "email": "test@example.com",
            "user_metadata": {"full_name": "Test User"}
        }
        yield mock

# Mock Supabase client
@pytest.fixture
def mock_supabase():
    with patch("app.core.database.supabase") as mock:
        yield mock

# Mock Redis client
@pytest.fixture
def mock_redis():
    with patch("app.core.cache.redis_client") as mock:
        yield mock

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_submit_research_query(mock_supabase, mock_redis):
    # Mock Supabase insert
    mock_supabase.from_().insert().execute.return_value = MagicMock(
        data=[{
            "id": "query-123",
            "user_id": "user-123",
            "query_text": "Impact of AI on education",
            "status": "pending"
        }]
    )
    
    # Mock Redis set
    mock_redis.set.return_value = True
    
    response = client.post(
        "/api/research/query",
        json={"query": "Impact of AI on education", "project_id": "project-123"}
    )
    
    assert response.status_code == 202
    assert "id" in response.json()
    assert response.json()["status"] == "pending"
    
    # Verify Supabase was called correctly
    mock_supabase.from_.assert_called_once_with("research_queries")
    mock_supabase.from_().insert.assert_called_once()
    
    # Verify Redis was used for the task queue
    mock_redis.set.assert_called_once()

def test_get_research_queries(mock_supabase):
    # Mock Supabase select
    mock_supabase.from_().select().eq().order().execute.return_value = MagicMock(
        data=[
            {
                "id": "query-123",
                "user_id": "user-123",
                "query_text": "Impact of AI on education",
                "status": "completed",
                "result_data": {"sources": [], "summary": "AI is transforming education..."},
                "created_at": "2023-04-20T14:30:00Z"
            },
            {
                "id": "query-456",
                "user_id": "user-123",
                "query_text": "Machine learning in healthcare",
                "status": "completed",
                "result_data": {"sources": [], "summary": "Machine learning applications in healthcare..."},
                "created_at": "2023-04-19T10:15:00Z"
            }
        ]
    )
    
    response = client.get("/api/research/queries")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == "query-123"
    assert response.json()[1]["id"] == "query-456"
    
    # Verify Supabase was called correctly
    mock_supabase.from_.assert_called_once_with("research_queries")
    mock_supabase.from_().select.assert_called_once()
    mock_supabase.from_().select().eq.assert_called_once_with("user_id", "user-123")
    mock_supabase.from_().select().eq().order.assert_called_once_with("created_at", desc=True)

def test_get_research_query_by_id(mock_supabase):
    # Mock Supabase select
    mock_supabase.from_().select().eq().eq().execute.return_value = MagicMock(
        data=[{
            "id": "query-123",
            "user_id": "user-123",
            "query_text": "Impact of AI on education",
            "status": "completed",
            "result_data": {"sources": [], "summary": "AI is transforming education..."},
            "created_at": "2023-04-20T14:30:00Z"
        }]
    )
    
    response = client.get("/api/research/queries/query-123")
    
    assert response.status_code == 200
    assert response.json()["id"] == "query-123"
    assert response.json()["query_text"] == "Impact of AI on education"
    
    # Verify Supabase was called correctly
    mock_supabase.from_.assert_called_once_with("research_queries")
    mock_supabase.from_().select.assert_called_once()
    mock_supabase.from_().select().eq.assert_called_once_with("id", "query-123")
    mock_supabase.from_().select().eq().eq.assert_called_once_with("user_id", "user-123")

def test_get_research_query_not_found(mock_supabase):
    # Mock Supabase select with empty result
    mock_supabase.from_().select().eq().eq().execute.return_value = MagicMock(data=[])
    
    response = client.get("/api/research/queries/nonexistent-id")
    
    assert response.status_code == 404
    assert "detail" in response.json()
    
    # Verify Supabase was called correctly
    mock_supabase.from_.assert_called_once_with("research_queries")

def test_submit_research_query_validation_error():
    # Test with empty query
    response = client.post(
        "/api/research/query",
        json={"query": "", "project_id": "project-123"}
    )
    
    assert response.status_code == 422
    
    # Test with query that's too long
    response = client.post(
        "/api/research/query",
        json={"query": "a" * 1001, "project_id": "project-123"}
    )
    
    assert response.status_code == 422
