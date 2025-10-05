#!/usr/bin/env python3
"""
Notion Usage Insights - Main Orchestrator
Generates comprehensive workspace analytics and usage reports
"""
import sys
import traceback
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Import configuration and modules
from config import Config
from src.api_client import NotionAPIClient
from src.extractors import ExportExtractor
from src.analytics import WorkspaceAnalytics
from src.report_builder import MarkdownReportBuilder


def print_header() -> None:
    """Print application header"""
    print("=" * 70)
    print("NOTION USAGE INSIGHTS - WORKSPACE ANALYTICS")
    print("=" * 70)
    print()


def setup_and_validate() -> None:
    """
    Validate configuration and print settings

    Raises:
        ValueError: If configuration is invalid
    """
    print("📋 Step 1: Validating configuration...")
    Config.validate()
    Config.print_config()
    print()


def collect_workspace_data(api_client: NotionAPIClient) -> Tuple[Dict[str, Dict], List[Dict]]:
    """
    Collect users and pages from Notion API

    Args:
        api_client: Initialized Notion API client

    Returns:
        Tuple of (users dict, pages list)
    """
    print("📥 Step 3: Collecting workspace data...")

    print("   - Fetching users...")
    users = api_client.get_all_users(use_cache=True)
    print(f"   ✓ Loaded {len(users)} users")

    print("   - Searching pages...")
    pages = api_client.search_all_pages(use_cache=True)
    print(f"   ✓ Found {len(pages)} pages")
    print()

    return users, pages


def extract_export_data(extractor: ExportExtractor) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Extract page IDs and database info from workspace export

    Args:
        extractor: Initialized export extractor

    Returns:
        Tuple of (export pages list, export summary dict)
    """
    print("📂 Step 4: Extracting page IDs from workspace export...")

    export_pages = extractor.extract_page_ids()
    export_summary = extractor.get_export_summary()

    print(f"   ✓ Extracted {len(export_pages)} pages from export")
    print(f"   ✓ Found {export_summary['total_databases']} databases")
    print(f"   ✓ Export size: {export_summary['export_size_mb']} MB")
    print()

    return export_pages, export_summary


def run_analytics_pipeline(pages: List[Dict], users: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Run all analytics calculations

    Args:
        pages: List of page objects from API
        users: Dict of user objects

    Returns:
        Dict containing all analytics results
    """
    print("📊 Step 5: Running analytics calculations...")

    analytics = WorkspaceAnalytics(pages=pages, users=users)
    results = analytics.run_all()

    # Print progress for each analysis
    print(f"   ✓ Summary: {results['summary']['total_pages']} pages, "
          f"{results['summary']['active_contributors']} active contributors")
    print(f"   ✓ Growth: {len(results['growth']['annual_counts'])} years tracked")
    print(f"   ✓ Users: {results['users']['segments']['power_creators']} power creators")
    print(f"   ✓ Collaboration: {results['collaboration']['average_collaboration_score']:.1f}% avg score")
    print(f"   ✓ Health: {results['content_health']['stale_percentage']:.1f}% stale pages")
    print(f"   ✓ Costs: ${results['costs']['total_annual_cost']:,.0f} annual")
    print(f"   ✓ Risk: Gini {results['risk']['gini_coefficient']:.3f}, "
          f"Bus factor {results['risk']['bus_factor']}")
    print("   ✓ Analytics complete")
    print()

    return results


def generate_and_save_report(results: Dict[str, Any]) -> Path:
    """
    Generate Markdown report from analytics results

    Args:
        results: Analytics results dict

    Returns:
        Path to generated report file
    """
    print("📄 Step 6: Generating Markdown report...")

    report_builder = MarkdownReportBuilder(results)
    output_path = report_builder.generate_report()

    print(f"   ✓ Report saved: {output_path}")
    print()

    return output_path


def print_summary(users: Dict, pages: List, export_pages: List,
                 export_summary: Dict, output_path: Path) -> None:
    """
    Print pipeline completion summary

    Args:
        users: Users dict
        pages: Pages list from API
        export_pages: Pages list from export
        export_summary: Export summary dict
        output_path: Path to generated report
    """
    print("=" * 70)
    print("✅ PIPELINE COMPLETE")
    print("=" * 70)
    print(f"📊 Users: {len(users)}")
    print(f"📄 Pages (API): {len(pages)}")
    print(f"📄 Pages (Export): {len(export_pages)}")
    print(f"🗄️  Databases: {export_summary['total_databases']}")
    print(f"💾 Report: {output_path}")
    print()
    print("✅ All phases complete!")
    print("   ✅ Phase 4: Export Extractor")
    print("   ✅ Phase 5: Analytics Engine")
    print("   ✅ Phase 6: Report Builder")
    print()


def main() -> int:
    """
    Main orchestration flow for Notion Usage Insights

    Pipeline:
    1. Setup and validate configuration
    2. Initialize API client
    3. Collect workspace data (users, pages)
    4. Extract export data
    5. Run analytics calculations
    6. Generate report
    7. Display summary

    Returns:
        Exit code (0 = success, 1 = error)
    """
    print_header()

    try:
        # Phase 1: Configuration
        setup_and_validate()

        # Phase 2: API Client Setup
        print("🔌 Step 2: Initializing Notion API client...")
        api_client = NotionAPIClient()
        print("✓ API client ready")
        print()

        # Phase 3: Data Collection
        users, pages = collect_workspace_data(api_client)

        # Phase 4: Export Extraction
        extractor = ExportExtractor()
        export_pages, export_summary = extract_export_data(extractor)

        # Phase 5: Analytics
        results = run_analytics_pipeline(pages, users)

        # Phase 6: Report Generation
        output_path = generate_and_save_report(results)

        # Summary
        print_summary(users, pages, export_pages, export_summary, output_path)

        return 0

    except ValueError as e:
        print(f"\n❌ Configuration Error:")
        print(str(e))
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected Error:")
        print(f"   {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
