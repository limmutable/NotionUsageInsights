"""
Export extractor for Notion workspace exports
Extracts page IDs and metadata from exported .md files
"""
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from config import Config


class ExportExtractor:
    """Extract page IDs and metadata from Notion workspace exports"""

    # Regex pattern for 32-character hex UUID (without hyphens)
    UUID_PATTERN = re.compile(r'([a-f0-9]{32})')

    # Regex pattern for formatted UUID with hyphens
    UUID_WITH_HYPHENS = re.compile(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})')

    def __init__(self, export_dir: Optional[str] = None):
        """
        Initialize extractor with export directory

        Args:
            export_dir: Path to Notion export directory (uses Config.EXPORT_DIR if None)
        """
        self.export_dir = Path(export_dir) if export_dir else Path(Config.EXPORT_DIR)

    @staticmethod
    def format_uuid(uuid_hex: str) -> str:
        """
        Format 32-char hex string as proper UUID with hyphens

        Args:
            uuid_hex: 32-character hex string (e.g., "abc123...")

        Returns:
            Formatted UUID (e.g., "abc12345-1234-1234-1234-123456789abc")
        """
        if len(uuid_hex) != 32:
            raise ValueError(f"UUID must be 32 characters, got {len(uuid_hex)}")

        return f"{uuid_hex[0:8]}-{uuid_hex[8:12]}-{uuid_hex[12:16]}-{uuid_hex[16:20]}-{uuid_hex[20:32]}"

    def extract_page_ids(self, export_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract page IDs from all .md files in export directory

        Args:
            export_dir: Override default export directory

        Returns:
            List of dicts with keys: id, title, path, file_size_kb
        """
        search_dir = Path(export_dir) if export_dir else self.export_dir

        if not search_dir.exists():
            raise ValueError(f"Export directory not found: {search_dir}")

        pages = []
        md_files = list(search_dir.rglob("*.md"))

        for file_path in md_files:
            # Extract UUID from filename
            filename = file_path.stem  # Filename without extension

            # Find 32-char hex UUID in filename
            match = self.UUID_PATTERN.search(filename)
            if not match:
                # Skip files without valid UUID (e.g., README.md)
                continue

            uuid_hex = match.group(1)

            # Format as proper UUID
            page_id = self.format_uuid(uuid_hex)

            # Extract title (remove UUID and extra spaces)
            title = filename.replace(uuid_hex, '').strip()

            # Get relative path from export root
            try:
                rel_path = file_path.relative_to(search_dir)
            except ValueError:
                rel_path = file_path

            # Get file size in KB
            file_size_kb = file_path.stat().st_size / 1024

            pages.append({
                'id': page_id,
                'title': title,
                'path': str(rel_path),
                'file_size_kb': round(file_size_kb, 2)
            })

        return pages

    def detect_databases(self, export_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Detect database folders in export (folders with matching CSV files)

        Args:
            export_dir: Override default export directory

        Returns:
            List of dicts with keys: name, path, entries, has_csv
        """
        search_dir = Path(export_dir) if export_dir else self.export_dir

        if not search_dir.exists():
            raise ValueError(f"Export directory not found: {search_dir}")

        databases = []

        # Find all directories that contain CSV files
        csv_files = list(search_dir.rglob("*.csv"))

        for csv_file in csv_files:
            db_folder = csv_file.parent

            # Extract database name from folder name (remove UUID)
            folder_name = db_folder.name
            match = self.UUID_PATTERN.search(folder_name)

            if match:
                uuid_hex = match.group(1)
                db_name = folder_name.replace(uuid_hex, '').strip()
            else:
                db_name = folder_name

            # Count .md entries in the database folder
            md_entries = list(db_folder.glob("*.md"))

            # Get relative path from export root
            try:
                rel_path = db_folder.relative_to(search_dir)
            except ValueError:
                rel_path = db_folder

            databases.append({
                'name': db_name,
                'path': str(rel_path),
                'entries': len(md_entries),
                'has_csv': csv_file.name,
                'csv_path': str(csv_file.relative_to(search_dir))
            })

        return databases

    def get_export_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about the export

        Returns:
            Dict with total_pages, total_databases, export_size_mb
        """
        pages = self.extract_page_ids()
        databases = self.detect_databases()

        # Calculate total export size
        total_size_bytes = sum(
            f.stat().st_size
            for f in self.export_dir.rglob("*")
            if f.is_file()
        )

        return {
            'total_pages': len(pages),
            'total_databases': len(databases),
            'export_size_mb': round(total_size_bytes / (1024 * 1024), 2),
            'export_dir': str(self.export_dir)
        }
