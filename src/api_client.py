"""
Notion API client with rate limiting and caching
"""
import time
import pickle
from pathlib import Path
from typing import List, Dict, Optional
from notion_client import Client
from tqdm import tqdm
from config import Config


class NotionAPIClient:
    """Wrapper for Notion API with rate limiting and caching"""

    def __init__(self):
        """Initialize Notion client with authentication"""
        self.client = Client(auth=Config.NOTION_TOKEN)
        self.rate_limit_delay = 1.0 / Config.REQUESTS_PER_SECOND

    def _rate_limit(self):
        """Sleep to respect rate limits"""
        time.sleep(self.rate_limit_delay)

    def _get_cache_path(self, cache_name: str) -> Path:
        """Get path for cache file"""
        return Path(Config.CACHE_DIR) / f"{cache_name}.pkl"

    def _load_cache(self, cache_name: str) -> Optional[any]:
        """Load data from cache if exists"""
        cache_path = self._get_cache_path(cache_name)
        if cache_path.exists():
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        return None

    def _save_cache(self, cache_name: str, data: any):
        """Save data to cache"""
        cache_path = self._get_cache_path(cache_name)
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)

    def get_all_users(self, use_cache: bool = True) -> Dict[str, Dict]:
        """
        Fetch all workspace users

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            Dict mapping user_id to user info: {user_id: {name, email, type}}
        """
        if use_cache:
            cached = self._load_cache('users')
            if cached:
                print("✓ Loaded users from cache")
                return cached

        print("Fetching users from API...")
        users = {}
        has_more = True
        start_cursor = None

        while has_more:
            response = self.client.users.list(start_cursor=start_cursor)

            for user in response['results']:
                users[user['id']] = {
                    'id': user['id'],
                    'name': user.get('name', 'Unknown'),
                    'email': user.get('person', {}).get('email', 'N/A'),
                    'type': user['type']  # 'person' or 'bot'
                }

            has_more = response.get('has_more', False)
            start_cursor = response.get('next_cursor')
            self._rate_limit()

        self._save_cache('users', users)
        print(f"✓ Fetched {len(users)} users")
        return users

    def search_all_pages(self, use_cache: bool = True) -> List[Dict]:
        """
        Search all pages via API

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            List of page objects with basic metadata
        """
        if use_cache:
            cached = self._load_cache('search_results')
            if cached:
                print("✓ Loaded search results from cache")
                return cached

        print("Searching all pages via API...")
        all_pages = []
        has_more = True
        start_cursor = None

        with tqdm(desc="Searching pages", unit=" pages") as pbar:
            while has_more:
                response = self.client.search(
                    filter={"property": "object", "value": "page"},
                    start_cursor=start_cursor,
                    page_size=100
                )

                batch = response['results']
                all_pages.extend(batch)
                pbar.update(len(batch))

                has_more = response.get('has_more', False)
                start_cursor = response.get('next_cursor')
                self._rate_limit()

        self._save_cache('search_results', all_pages)
        print(f"✓ Found {len(all_pages)} pages")
        return all_pages

    def get_page_details(self, page_id: str) -> Optional[Dict]:
        """
        Retrieve full metadata for a single page

        Args:
            page_id: Notion page ID

        Returns:
            Dict with page details or None if error
        """
        try:
            page = self.client.pages.retrieve(page_id=page_id)
            self._rate_limit()

            return {
                'id': page['id'],
                'created_time': page['created_time'],
                'created_by': page['created_by']['id'],
                'last_edited_time': page['last_edited_time'],
                'last_edited_by': page['last_edited_by']['id'],
                'url': page['url'],
                'archived': page.get('archived', False)
            }
        except Exception as e:
            print(f"✗ Error fetching page {page_id}: {str(e)[:100]}")
            return None

    def enrich_pages(self, page_ids: List[str], use_cache: bool = True,
                     force_refresh: bool = False) -> List[Dict]:
        """
        Fetch detailed metadata for multiple pages
        This is the slowest operation (1 hour per 10K pages)

        Args:
            page_ids: List of Notion page IDs
            use_cache: Whether to use cached data if available
            force_refresh: Force re-fetching even if cache exists

        Returns:
            List of dicts with page details
        """
        cache_name = 'enriched_pages'

        if use_cache and not force_refresh:
            cached = self._load_cache(cache_name)
            if cached:
                print("✓ Loaded enriched pages from cache")
                return cached

        print(f"\nEnriching {len(page_ids)} pages...")
        print(f"⏱️  Estimated time: {len(page_ids) / 180:.1f} minutes")

        enriched = []

        with tqdm(total=len(page_ids), desc="Fetching metadata", unit=" pages") as pbar:
            for page_id in page_ids:
                details = self.get_page_details(page_id)
                if details:
                    enriched.append(details)
                pbar.update(1)

                # Save checkpoint every 1000 pages
                if len(enriched) % 1000 == 0:
                    self._save_cache(f"{cache_name}_checkpoint", enriched)

        self._save_cache(cache_name, enriched)
        print(f"✓ Enriched {len(enriched)} pages")
        return enriched
