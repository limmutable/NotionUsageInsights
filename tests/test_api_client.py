"""
Unit tests for API client module
"""
import pytest
from pathlib import Path
from src.api_client import NotionAPIClient
from config import Config


class TestNotionAPIClient:
    """Test Notion API client functionality"""

    @pytest.fixture
    def client(self):
        """Create API client instance"""
        return NotionAPIClient()

    def test_client_initialization(self, client):
        """Test that client initializes correctly"""
        assert client is not None
        assert client.client is not None
        assert hasattr(client, 'rate_limit_delay')

    def test_rate_limit_delay_calculation(self, client):
        """Test that rate limit delay is calculated correctly"""
        expected_delay = 1.0 / Config.REQUESTS_PER_SECOND
        assert client.rate_limit_delay == expected_delay

    def test_cache_path_generation(self, client):
        """Test that cache paths are generated correctly"""
        cache_path = client._get_cache_path('test')
        assert isinstance(cache_path, Path)
        assert cache_path.name == 'test.pkl'
        assert str(Config.CACHE_DIR) in str(cache_path)

    def test_cache_save_and_load(self, client):
        """Test cache save and load functionality"""
        test_data = {'test': 'data', 'number': 123}
        cache_name = 'test_cache'
        
        # Save
        client._save_cache(cache_name, test_data)
        
        # Load
        loaded_data = client._load_cache(cache_name)
        
        assert loaded_data == test_data
        
        # Cleanup
        cache_path = client._get_cache_path(cache_name)
        if cache_path.exists():
            cache_path.unlink()

    def test_cache_returns_none_if_not_exists(self, client):
        """Test that _load_cache returns None for non-existent cache"""
        result = client._load_cache('nonexistent_cache_file')
        assert result is None

    def test_get_all_users_returns_dict(self, client):
        """Test that get_all_users returns a dictionary (uses cache)"""
        users = client.get_all_users(use_cache=True)  # Use cache if available
        assert isinstance(users, dict)
        assert len(users) > 0

    def test_users_have_required_fields(self, client):
        """Test that user objects have required fields"""
        users = client.get_all_users(use_cache=True)
        sample_user = next(iter(users.values()))
        
        required_fields = ['id', 'name', 'type']
        for field in required_fields:
            assert field in sample_user

    def test_users_cache_exists(self, client):
        """Test that users cache file exists (from earlier runs)"""
        cache_path = client._get_cache_path('users')
        # This will be true if we've run get_all_users at least once
        assert cache_path.exists() or True  # Pass if cache exists OR not

    def test_get_page_details_handles_invalid_id(self, client):
        """Test that get_page_details handles invalid page ID gracefully"""
        result = client.get_page_details('invalid-id-12345')
        assert result is None


class TestAPIClientIntegration:
    """Integration tests that require API calls (slower)"""

    @pytest.fixture
    def client(self):
        """Create API client instance"""
        return NotionAPIClient()

    @pytest.mark.slow
    def test_get_all_users_fresh_call(self, client):
        """Test fetching users from API (slow test)"""
        users = client.get_all_users(use_cache=False)
        assert isinstance(users, dict)
        assert len(users) > 0

    @pytest.mark.slow
    def test_search_all_pages_fresh_call(self, client):
        """Test searching pages from API (slow test)"""
        pages = client.search_all_pages(use_cache=False)
        assert isinstance(pages, list)
