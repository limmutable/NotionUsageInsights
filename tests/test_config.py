"""
Unit tests for config module
"""
import os
import pytest
from pathlib import Path
from config import Config


class TestConfig:
    """Test configuration validation and settings"""

    def test_config_has_notion_token(self):
        """Test that Notion token is set"""
        assert Config.NOTION_TOKEN is not None
        assert len(Config.NOTION_TOKEN) > 0

    def test_notion_token_format(self):
        """Test that Notion token has valid format"""
        token = Config.NOTION_TOKEN
        valid_prefixes = ('secret_', 'ntn_', 'sntn_')
        assert any(token.startswith(prefix) for prefix in valid_prefixes), \
            f"Token should start with one of {valid_prefixes}"

    def test_rate_limit_positive(self):
        """Test that rate limit is positive"""
        assert Config.REQUESTS_PER_SECOND > 0

    def test_directory_paths_exist(self):
        """Test that directory paths are set"""
        assert Config.EXPORT_DIR is not None
        assert Config.OUTPUT_DIR is not None
        assert Config.CACHE_DIR is not None

    def test_output_cache_dirs_created(self):
        """Test that output and cache directories exist"""
        assert Path(Config.OUTPUT_DIR).exists()
        assert Path(Config.CACHE_DIR).exists()

    def test_export_dir_has_files(self):
        """Test that export directory contains .md files"""
        export_path = Path(Config.EXPORT_DIR)
        assert export_path.exists()
        md_files = list(export_path.rglob('*.md'))
        assert len(md_files) > 0, "Export directory should contain .md files"

    def test_thresholds_are_integers(self):
        """Test that all threshold values are integers"""
        assert isinstance(Config.STALE_THRESHOLD_DAYS, int)
        assert isinstance(Config.VERY_STALE_THRESHOLD_DAYS, int)
        assert isinstance(Config.POWER_USER_THRESHOLD, int)
        assert isinstance(Config.ACTIVE_USER_THRESHOLD, int)
        assert isinstance(Config.OCCASIONAL_USER_THRESHOLD, int)

    def test_threshold_hierarchy(self):
        """Test that user thresholds are in correct order"""
        assert Config.POWER_USER_THRESHOLD > Config.ACTIVE_USER_THRESHOLD
        assert Config.ACTIVE_USER_THRESHOLD > Config.OCCASIONAL_USER_THRESHOLD
        assert Config.OCCASIONAL_USER_THRESHOLD > 0

    def test_staleness_threshold_hierarchy(self):
        """Test that staleness thresholds are in correct order"""
        assert Config.VERY_STALE_THRESHOLD_DAYS > Config.STALE_THRESHOLD_DAYS
        assert Config.STALE_THRESHOLD_DAYS > 0

    def test_cost_parameters(self):
        """Test that cost parameters are valid"""
        assert Config.MONTHLY_COST_PER_USER > 0
        assert Config.BLENDED_HOURLY_RATE > 0

    def test_validate_passes(self):
        """Test that config validation passes with valid config"""
        # Should not raise exception
        assert Config.validate() == True

    def test_print_config_runs(self, capsys):
        """Test that print_config() runs without errors"""
        Config.print_config()
        captured = capsys.readouterr()
        assert "CONFIGURATION" in captured.out
        assert "Notion Token" in captured.out
