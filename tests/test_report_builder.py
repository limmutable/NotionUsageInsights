"""
Unit tests for Markdown Report Builder
"""
import pytest
from pathlib import Path
from datetime import datetime
from src.report_builder import MarkdownReportBuilder


@pytest.fixture
def sample_results():
    """Sample analytics results for testing"""
    return {
        'summary': {
            'total_pages': 2812,
            'total_users': 18,
            'active_contributors': 27,
            'current_creators': 12,
            'deleted_creators': 15,
            'inactive_users': 6,
            'stale_pages': 1500,
            'stale_percentage': 53.3,
            'annual_cost': 2592,
            'cost_per_active_user': 216.0
        },
        'growth': {
            'annual_counts': {2019: 100, 2020: 300, 2021: 500, 2022: 800, 2023: 900, 2024: 212},
            'yoy_growth': {2020: 200.0, 2021: 66.7, 2022: 60.0, 2023: 12.5, 2024: -76.4},
            'quarterly_latest_year': {'2024Q1': 50, '2024Q2': 75, '2024Q3': 62, '2024Q4': 25},
            'monthly_last_12': {'2024-01': 15, '2024-02': 20, '2024-03': 15, '2024-04': 25,
                               '2024-05': 30, '2024-06': 20, '2024-07': 22, '2024-08': 18,
                               '2024-09': 22, '2024-10': 8},
            'avg_monthly_pages': 19.5
        },
        'users': {
            'segments': {
                'power_creators': 2,
                'active_creators': 4,
                'occasional_creators': 3,
                'minimal_creators': 3,
                'non_creators': 6
            },
            'pages_by_segment': {},
            'active_creator_percentage': 66.7
        },
        'top_creators': [
            {'name': 'Alice', 'page_count': 500, 'percentage': 17.8},
            {'name': 'Bob', 'page_count': 400, 'percentage': 14.2},
            {'name': 'Charlie', 'page_count': 300, 'percentage': 10.7}
        ],
        'content_health': {
            'staleness_distribution': {
                'Active (< 1 month)': 200,
                'Fresh (1-3 months)': 300,
                'Aging (3-6 months)': 400,
                'Stale (6-12 months)': 500,
                'Very Stale (12-24 months)': 700,
                'Dead (24+ months)': 712
            },
            'stale_pages': 1500,
            'stale_percentage': 53.3,
            'very_stale_pages': 1412,
            'very_stale_percentage': 50.2,
            'abandoned_pages': 500,
            'abandoned_percentage': 17.8,
            'archived_pages': 50
        },
        'collaboration': {
            'top_collaborators': [
                {'name': 'Alice', 'pages_created': 500, 'others_pages_edited': 200, 'collaboration_score': 40.0},
                {'name': 'Bob', 'pages_created': 400, 'others_pages_edited': 300, 'collaboration_score': 75.0}
            ],
            'average_collaboration_score': 57.5,
            'collaborated_pages': 1200,
            'single_owner_pages': 1612,
            'collaboration_percentage': 42.7
        },
        'costs': {
            'total_annual_cost': 2592,
            'cost_per_active_creator': 216.0,
            'wasted_spend_annual': 864,
            'wasted_spend_percentage': 33.3,
            'total_creation_value': 135000,
            'roi_percentage': 5108.3,
            'monthly_cost_per_user': 12,
            'blended_hourly_rate': 48
        },
        'risk': {
            'concentration': {
                'top_1_percent': {'users': 1, 'pages': 500, 'percentage': 17.8},
                'top_5_percent': {'users': 1, 'pages': 900, 'percentage': 32.0},
                'top_10_percent': {'users': 2, 'pages': 1300, 'percentage': 46.2}
            },
            'gini_coefficient': 0.785,
            'bus_factor': 2
        },
        'structure': {
            'templates_count': 50,
            'databases_count': 0,
            'pages_count': 2762,
            'template_percentage': 1.8
        }
    }


class TestMarkdownReportBuilder:
    """Test MarkdownReportBuilder class"""

    def test_initialization(self, sample_results):
        """Test report builder initialization"""
        builder = MarkdownReportBuilder(sample_results)
        assert builder.results == sample_results
        assert builder.workspace_name == "Notion Workspace"
        assert isinstance(builder.timestamp, datetime)

    def test_initialization_custom_workspace_name(self, sample_results):
        """Test initialization with custom workspace name"""
        builder = MarkdownReportBuilder(sample_results, workspace_name="My Team Workspace")
        assert builder.workspace_name == "My Team Workspace"

    def test_format_table_basic(self, sample_results):
        """Test basic table formatting"""
        builder = MarkdownReportBuilder(sample_results)
        data = [
            {'Name': 'Alice', 'Count': 100},
            {'Name': 'Bob', 'Count': 200}
        ]
        table = builder._format_table(data, ['Name', 'Count'])

        assert '| Name | Count |' in table
        assert '| :--- | :--- |' in table
        assert '| Alice | 100 |' in table
        assert '| Bob | 200 |' in table

    def test_format_table_with_alignments(self, sample_results):
        """Test table formatting with custom alignments"""
        builder = MarkdownReportBuilder(sample_results)
        data = [{'Name': 'Alice', 'Count': 100}]
        table = builder._format_table(data, ['Name', 'Count'], ['left', 'right'])

        assert '| :--- | ---: |' in table

    def test_format_table_empty_data(self, sample_results):
        """Test table formatting with empty data"""
        builder = MarkdownReportBuilder(sample_results)
        table = builder._format_table([], ['Name', 'Count'])
        assert table == "_No data available_"

    def test_format_percentage(self, sample_results):
        """Test percentage formatting"""
        builder = MarkdownReportBuilder(sample_results)

        assert builder._format_percentage(42.567) == "42.6%"
        assert builder._format_percentage(0.0) == "0.0%"
        assert builder._format_percentage(100.0) == "100.0%"

    def test_format_percentage_with_icon(self, sample_results):
        """Test percentage formatting with status icons"""
        builder = MarkdownReportBuilder(sample_results)

        assert "✅" in builder._format_percentage(15.0, include_icon=True)
        assert "⚠️" in builder._format_percentage(35.0, include_icon=True)
        assert "❌" in builder._format_percentage(75.0, include_icon=True)

    def test_format_currency(self, sample_results):
        """Test currency formatting"""
        builder = MarkdownReportBuilder(sample_results)

        assert builder._format_currency(1000) == "$1,000"
        assert builder._format_currency(1234567) == "$1,234,567"
        assert builder._format_currency(0) == "$0"

    def test_get_status_icon_stale_percentage(self, sample_results):
        """Test status icon for stale percentage"""
        builder = MarkdownReportBuilder(sample_results)

        assert builder._get_status_icon('stale_percentage', 25.0) == '✅'
        assert builder._get_status_icon('stale_percentage', 45.0) == '⚠️'
        assert builder._get_status_icon('stale_percentage', 75.0) == '❌'

    def test_get_status_icon_bus_factor(self, sample_results):
        """Test status icon for bus factor"""
        builder = MarkdownReportBuilder(sample_results)

        assert builder._get_status_icon('bus_factor', 3) == '❌'
        assert builder._get_status_icon('bus_factor', 7) == '⚠️'
        assert builder._get_status_icon('bus_factor', 15) == '✅'

    def test_get_status_icon_unknown_metric(self, sample_results):
        """Test status icon for unknown metric"""
        builder = MarkdownReportBuilder(sample_results)
        assert builder._get_status_icon('unknown_metric', 50.0) == ''

    def test_write_header(self, sample_results):
        """Test header generation"""
        builder = MarkdownReportBuilder(sample_results, workspace_name="Test Workspace")
        header = builder._write_header()

        assert "# Test Workspace Analytics Report" in header
        assert "**Generated:**" in header
        assert "## Table of Contents" in header
        assert "[Executive Summary]" in header

    def test_write_executive_summary(self, sample_results):
        """Test executive summary generation"""
        builder = MarkdownReportBuilder(sample_results)
        summary = builder._write_executive_summary()

        assert "## Executive Summary" in summary
        assert "2,812" in summary  # total pages
        assert "18" in summary  # total users
        assert "53.3%" in summary  # stale percentage

    def test_write_growth(self, sample_results):
        """Test growth section generation"""
        builder = MarkdownReportBuilder(sample_results)
        growth = builder._write_growth()

        assert "## Growth & Velocity" in growth
        assert "2019" in growth
        assert "2024" in growth
        assert "19.5" in growth  # avg monthly pages

    def test_write_users(self, sample_results):
        """Test user analytics section generation"""
        builder = MarkdownReportBuilder(sample_results)
        users = builder._write_users()

        assert "## User Analytics" in users
        assert "Power Creators" in users
        assert "Non-Creators" in users
        assert "Alice" in users  # top creator
        assert "66.7%" in users  # active creator percentage

    def test_write_content_health(self, sample_results):
        """Test content health section generation"""
        builder = MarkdownReportBuilder(sample_results)
        health = builder._write_content_health()

        assert "## Content Health" in health
        assert "Staleness Distribution" in health
        assert "Active (< 1 month)" in health
        assert "53.3%" in health  # stale percentage

    def test_write_collaboration(self, sample_results):
        """Test collaboration section generation"""
        builder = MarkdownReportBuilder(sample_results)
        collab = builder._write_collaboration()

        assert "## Collaboration Patterns" in collab
        assert "Top 10 Collaborators" in collab
        assert "57.5%" in collab  # avg collaboration score
        assert "Collaboration Score" in collab

    def test_write_costs(self, sample_results):
        """Test cost analysis section generation"""
        builder = MarkdownReportBuilder(sample_results)
        costs = builder._write_costs()

        assert "## Cost Analysis" in costs
        assert "$2,592" in costs  # annual cost
        assert "$216" in costs  # cost per active
        assert "33.3%" in costs  # wasted percentage

    def test_write_risk(self, sample_results):
        """Test risk assessment section generation"""
        builder = MarkdownReportBuilder(sample_results)
        risk = builder._write_risk()

        assert "## Risk Assessment" in risk
        assert "0.785" in risk  # Gini coefficient
        assert "2 people" in risk  # bus factor
        assert "Ownership Concentration" in risk

    def test_write_detailed_tables(self, sample_results):
        """Test detailed tables section generation"""
        builder = MarkdownReportBuilder(sample_results)
        tables = builder._write_detailed_tables()

        assert "## Detailed Tables" in tables
        assert "User Segments Breakdown" in tables
        assert "Staleness Definitions" in tables
        assert "Power Creators" in tables

    def test_generate_report_creates_file(self, sample_results, tmp_path):
        """Test report generation creates markdown file"""
        builder = MarkdownReportBuilder(sample_results)
        output_path = tmp_path / "test_report.md"

        result_path = builder.generate_report(output_path=output_path)

        assert result_path == output_path
        assert output_path.exists()
        assert output_path.suffix == '.md'

    def test_generate_report_content(self, sample_results, tmp_path):
        """Test generated report has all sections"""
        builder = MarkdownReportBuilder(sample_results)
        output_path = tmp_path / "test_report.md"

        builder.generate_report(output_path=output_path)

        content = output_path.read_text(encoding='utf-8')

        # Check all major sections are present
        assert "# Notion Workspace Analytics Report" in content
        assert "## Executive Summary" in content
        assert "## Growth & Velocity" in content
        assert "## User Analytics" in content
        assert "## Content Health" in content
        assert "## Collaboration Patterns" in content
        assert "## Cost Analysis" in content
        assert "## Risk Assessment" in content
        assert "## Detailed Tables" in content

    def test_generate_report_separators(self, sample_results, tmp_path):
        """Test report sections are separated correctly"""
        builder = MarkdownReportBuilder(sample_results)
        output_path = tmp_path / "test_report.md"

        builder.generate_report(output_path=output_path)

        content = output_path.read_text(encoding='utf-8')

        # Check separators between sections
        assert '\n\n---\n\n' in content

    def test_generate_report_valid_markdown(self, sample_results, tmp_path):
        """Test generated report is valid markdown"""
        builder = MarkdownReportBuilder(sample_results)
        output_path = tmp_path / "test_report.md"

        builder.generate_report(output_path=output_path)

        content = output_path.read_text(encoding='utf-8')

        # Check markdown elements
        assert content.count('##') >= 8  # At least 8 section headers
        assert '|' in content  # Tables present
        assert '**' in content  # Bold text present
        assert '-' in content  # List items or separators


class TestMarkdownTableFormatting:
    """Test markdown table formatting edge cases"""

    def test_table_with_missing_keys(self, sample_results):
        """Test table handles missing dictionary keys"""
        builder = MarkdownReportBuilder(sample_results)
        data = [
            {'Name': 'Alice', 'Count': 100},
            {'Name': 'Bob'}  # Missing 'Count'
        ]
        table = builder._format_table(data, ['Name', 'Count'])

        assert '| Alice | 100 |' in table
        assert '| Bob |  |' in table  # Empty cell for missing key

    def test_table_with_special_characters(self, sample_results):
        """Test table handles special characters"""
        builder = MarkdownReportBuilder(sample_results)
        data = [
            {'Name': 'User | Special', 'Count': 100}
        ]
        table = builder._format_table(data, ['Name', 'Count'])

        # Should handle pipe characters in data
        assert 'User | Special' in table


class TestReportBuilderWithEmptyData:
    """Test report builder handles empty/missing data gracefully"""

    def test_empty_top_creators(self, sample_results):
        """Test report handles empty top creators list"""
        sample_results['top_creators'] = []
        builder = MarkdownReportBuilder(sample_results)
        users_section = builder._write_users()

        assert "## User Analytics" in users_section
        # Should not crash

    def test_empty_collaboration_data(self, sample_results):
        """Test report handles empty collaboration data"""
        sample_results['collaboration']['top_collaborators'] = []
        builder = MarkdownReportBuilder(sample_results)
        collab_section = builder._write_collaboration()

        assert "## Collaboration Patterns" in collab_section
        assert "_No collaboration data_" in collab_section
