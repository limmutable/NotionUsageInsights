"""
Unit tests for export extractor module
"""
import pytest
from pathlib import Path
from src.extractors import ExportExtractor
from config import Config


class TestExportExtractor:
    """Test export extraction functionality"""

    @pytest.fixture
    def extractor(self):
        """Create extractor instance"""
        return ExportExtractor()

    def test_extractor_initialization(self, extractor):
        """Test that extractor initializes correctly"""
        assert extractor is not None
        assert extractor.export_dir == Path(Config.EXPORT_DIR)

    def test_extractor_custom_dir(self):
        """Test extractor with custom export directory"""
        custom_dir = "/custom/path"
        extractor = ExportExtractor(export_dir=custom_dir)
        assert extractor.export_dir == Path(custom_dir)

    def test_format_uuid(self):
        """Test UUID formatting from hex to hyphenated format"""
        uuid_hex = "abc123def4567890abcd1234ef567890"
        expected = "abc123de-f456-7890-abcd-1234ef567890"
        result = ExportExtractor.format_uuid(uuid_hex)
        assert result == expected

    def test_format_uuid_invalid_length(self):
        """Test that format_uuid raises error for invalid length"""
        with pytest.raises(ValueError, match="UUID must be 32 characters"):
            ExportExtractor.format_uuid("tooshort")

    def test_extract_page_ids_returns_list(self, extractor):
        """Test that extract_page_ids returns a list"""
        pages = extractor.extract_page_ids()
        assert isinstance(pages, list)

    def test_extract_page_ids_has_pages(self, extractor):
        """Test that extract_page_ids finds pages in export"""
        pages = extractor.extract_page_ids()
        assert len(pages) > 0, "Should find pages in export directory"

    def test_page_has_required_fields(self, extractor):
        """Test that extracted pages have all required fields"""
        pages = extractor.extract_page_ids()
        assert len(pages) > 0

        page = pages[0]
        required_fields = ['id', 'title', 'path', 'file_size_kb']
        for field in required_fields:
            assert field in page, f"Page missing required field: {field}"

    def test_page_id_format(self, extractor):
        """Test that page IDs are properly formatted UUIDs"""
        pages = extractor.extract_page_ids()
        assert len(pages) > 0

        page_id = pages[0]['id']
        # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        assert len(page_id) == 36, "UUID should be 36 chars with hyphens"
        assert page_id.count('-') == 4, "UUID should have 4 hyphens"

    def test_detect_databases_returns_list(self, extractor):
        """Test that detect_databases returns a list"""
        databases = extractor.detect_databases()
        assert isinstance(databases, list)

    def test_databases_have_required_fields(self, extractor):
        """Test that databases have all required fields"""
        databases = extractor.detect_databases()
        if len(databases) > 0:
            db = databases[0]
            required_fields = ['name', 'path', 'entries', 'has_csv']
            for field in required_fields:
                assert field in db, f"Database missing required field: {field}"

    def test_get_export_summary(self, extractor):
        """Test get_export_summary returns correct structure"""
        summary = extractor.get_export_summary()

        required_fields = ['total_pages', 'total_databases', 'export_size_mb', 'export_dir']
        for field in required_fields:
            assert field in summary, f"Summary missing field: {field}"

        assert summary['total_pages'] > 0
        assert summary['export_size_mb'] > 0

    def test_extract_page_ids_invalid_directory(self):
        """Test that extract_page_ids raises error for invalid directory"""
        extractor = ExportExtractor(export_dir="/invalid/nonexistent/path")

        with pytest.raises(ValueError, match="Export directory not found"):
            extractor.extract_page_ids()

    def test_detect_databases_invalid_directory(self):
        """Test that detect_databases raises error for invalid directory"""
        extractor = ExportExtractor(export_dir="/invalid/nonexistent/path")

        with pytest.raises(ValueError, match="Export directory not found"):
            extractor.detect_databases()


class TestMockedExportExtractor:
    """Unit tests with mocked file system"""

    def test_format_uuid_various_inputs(self):
        """Test UUID formatting with various valid inputs"""
        test_cases = [
            ("00000000000000000000000000000000", "00000000-0000-0000-0000-000000000000"),
            ("ffffffffffffffffffffffffffffffff", "ffffffff-ffff-ffff-ffff-ffffffffffff"),
            ("1b3122211c9a4bb2b1e905a3fdefcc81", "1b312221-1c9a-4bb2-b1e9-05a3fdefcc81"),
        ]

        for input_hex, expected_uuid in test_cases:
            result = ExportExtractor.format_uuid(input_hex)
            assert result == expected_uuid
