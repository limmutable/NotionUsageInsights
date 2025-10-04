"""
Configuration and constants for Notion Analytics
"""
import os
from pathlib import Path
from typing import ClassVar
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Notion Workspace Analytics"""

    # ==================== API Configuration ====================
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    REQUESTS_PER_SECOND = 3  # Notion API rate limit

    # ==================== Directory Paths ====================
    # Get from environment or use defaults
    EXPORT_DIR = os.getenv('EXPORT_DIR', './data/export')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './data/output')
    CACHE_DIR = os.getenv('CACHE_DIR', './data/cache')

    # ==================== Analysis Parameters ====================
    ANALYSIS_START_YEAR = 2020

    # Staleness thresholds (in days)
    STALE_THRESHOLD_DAYS = int(os.getenv('STALE_THRESHOLD_DAYS', 365))      # 12 months
    VERY_STALE_THRESHOLD_DAYS = int(os.getenv('VERY_STALE_THRESHOLD_DAYS', 730))  # 24 months

    # User segmentation thresholds (pages per year)
    POWER_USER_THRESHOLD = int(os.getenv('POWER_USER_THRESHOLD', 100))
    ACTIVE_USER_THRESHOLD = int(os.getenv('ACTIVE_USER_THRESHOLD', 20))
    OCCASIONAL_USER_THRESHOLD = int(os.getenv('OCCASIONAL_USER_THRESHOLD', 5))

    # ==================== Cost Parameters ====================
    MONTHLY_COST_PER_USER = int(os.getenv('MONTHLY_COST_PER_USER', 12))  # Business plan
    BLENDED_HOURLY_RATE = int(os.getenv('BLENDED_HOURLY_RATE', 48))      # For ROI calculations

    # ==================== Optional Configuration ====================
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration before running
        Raises ValueError if configuration is invalid
        """
        errors = []

        # Check Notion token
        if not cls.NOTION_TOKEN:
            errors.append("❌ NOTION_TOKEN not set in .env file")
        elif not (cls.NOTION_TOKEN.startswith('secret_') or cls.NOTION_TOKEN.startswith('ntn_')):
            errors.append("❌ NOTION_TOKEN appears invalid (should start with 'secret_' or 'ntn_')")

        # Check export directory exists
        export_path = Path(cls.EXPORT_DIR)
        if not export_path.exists():
            errors.append(f"❌ Export directory not found: {cls.EXPORT_DIR}")
        elif not any(export_path.rglob('*.md')):
            errors.append(f"❌ No .md files found in export directory: {cls.EXPORT_DIR}")

        # Create output directories if they don't exist
        try:
            Path(cls.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            Path(cls.CACHE_DIR).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"❌ Could not create output directories: {e}")

        # Validate numeric parameters
        if cls.REQUESTS_PER_SECOND <= 0:
            errors.append("❌ REQUESTS_PER_SECOND must be > 0")

        if cls.POWER_USER_THRESHOLD <= cls.ACTIVE_USER_THRESHOLD:
            errors.append("❌ POWER_USER_THRESHOLD must be > ACTIVE_USER_THRESHOLD")

        if cls.ACTIVE_USER_THRESHOLD <= cls.OCCASIONAL_USER_THRESHOLD:
            errors.append("❌ ACTIVE_USER_THRESHOLD must be > OCCASIONAL_USER_THRESHOLD")

        # If there are errors, raise exception
        if errors:
            error_msg = "\n".join(errors)
            raise ValueError(f"\n\nConfiguration Validation Failed:\n{error_msg}\n")

        return True

    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (for debugging)"""
        print("=" * 60)
        print("CONFIGURATION")
        print("=" * 60)
        print(f"Notion Token: {'✓ Set' if cls.NOTION_TOKEN else '✗ Not Set'}")
        print(f"Export Directory: {cls.EXPORT_DIR}")
        print(f"Output Directory: {cls.OUTPUT_DIR}")
        print(f"Cache Directory: {cls.CACHE_DIR}")
        print(f"Rate Limit: {cls.REQUESTS_PER_SECOND} requests/second")
        print(f"Stale Threshold: {cls.STALE_THRESHOLD_DAYS} days")
        print(f"Power User Threshold: {cls.POWER_USER_THRESHOLD} pages/year")
        print(f"Monthly Cost/User: ${cls.MONTHLY_COST_PER_USER}")
        print("=" * 60)


# Validate configuration when module is imported
# This ensures early failure if config is invalid
if __name__ != "__main__":
    try:
        Config.validate()
    except ValueError as e:
        print(e)
        print("\n💡 Tip: Check your .env file and ensure:")
        print("   1. NOTION_TOKEN is set correctly")
        print("   2. Workspace export is in data/export/ directory")
        print("   3. All paths are correct")
        raise
