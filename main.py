#!/usr/bin/env python3
"""
Notion Usage Insights - Main Orchestrator
Generates comprehensive workspace analytics and usage reports
"""
import sys
from typing import Optional
from pathlib import Path

# Import configuration and modules
from config import Config
from src.api_client import NotionAPIClient
from src.extractors import ExportExtractor
from src.analytics import WorkspaceAnalytics  # Phase 5
# from src.report_builder import ReportBuilder  # Phase 6


def main() -> int:
    """
    Main orchestration flow for Notion Usage Insights

    Pipeline:
    1. Load configuration and validate
    2. Extract page IDs from export (if available)
    3. Fetch user data from API
    4. Search all pages via API
    5. Enrich pages with detailed metadata
    6. Run analytics calculations
    7. Generate Excel report
    8. Display summary

    Returns:
        Exit code (0 = success, 1 = error)
    """

    print("=" * 70)
    print("NOTION USAGE INSIGHTS - WORKSPACE ANALYTICS")
    print("=" * 70)
    print()

    try:
        # ========== PHASE 1: Configuration ==========
        print("📋 Step 1: Validating configuration...")
        Config.validate()
        Config.print_config()
        print()

        # ========== PHASE 2: API Client Setup ==========
        print("🔌 Step 2: Initializing Notion API client...")
        api_client = NotionAPIClient()
        print("✓ API client ready")
        print()

        # ========== PHASE 3: Data Collection (TODO: Phase 4-6) ==========
        print("📥 Step 3: Collecting workspace data...")
        print("   - Fetching users...")
        users = api_client.get_all_users(use_cache=True)
        print(f"   ✓ Loaded {len(users)} users")

        print("   - Searching pages...")
        pages = api_client.search_all_pages(use_cache=True)
        print(f"   ✓ Found {len(pages)} pages")
        print()

        # ========== PHASE 4: Export Extraction ==========
        print("📂 Step 4: Extracting page IDs from workspace export...")
        extractor = ExportExtractor()
        export_pages = extractor.extract_page_ids()
        export_summary = extractor.get_export_summary()
        print(f"   ✓ Extracted {len(export_pages)} pages from export")
        print(f"   ✓ Found {export_summary['total_databases']} databases")
        print(f"   ✓ Export size: {export_summary['export_size_mb']} MB")
        print()

        # ========== PHASE 5 - Analytics ==========
        print("📊 Step 5: Running analytics calculations...")
        analytics = WorkspaceAnalytics(pages=pages, users=users)
        results = analytics.run_all()

        print(f"   ✓ Summary: {results['summary']['total_pages']} pages, {results['summary']['active_contributors']} active contributors")
        print(f"   ✓ Growth: {len(results['growth']['annual_counts'])} years tracked")
        print(f"   ✓ Users: {results['users']['segments']['power_creators']} power creators")
        print(f"   ✓ Collaboration: {results['collaboration']['average_collaboration_score']:.1f}% avg score")
        print(f"   ✓ Health: {results['content_health']['stale_percentage']:.1f}% stale pages")
        print(f"   ✓ Costs: ${results['costs']['total_annual_cost']:,.0f} annual")
        print(f"   ✓ Risk: Gini {results['risk']['gini_coefficient']:.3f}, Bus factor {results['risk']['bus_factor']}")
        print("   ✓ Analytics complete")
        print()

        # ========== TODO: PHASE 6 - Report Generation ==========
        # print("📄 Step 6: Generating Excel report...")
        # report_builder = ReportBuilder()
        # output_path = report_builder.generate_report(
        #     growth_metrics=growth_metrics,
        #     user_engagement=user_engagement,
        #     content_health=content_health,
        #     collaboration=collaboration,
        #     cost_analysis=cost_analysis,
        #     knowledge_risk=knowledge_risk
        # )
        # print(f"   ✓ Report saved: {output_path}")
        # print()

        # ========== Summary ==========
        print("=" * 70)
        print("✅ PIPELINE COMPLETE")
        print("=" * 70)
        print(f"📊 Users: {len(users)}")
        print(f"📄 Pages (API): {len(pages)}")
        print(f"📄 Pages (Export): {len(export_pages)}")
        print(f"🗄️  Databases: {export_summary['total_databases']}")
        # print(f"💾 Report: {output_path}")
        print()
        print("⚠️  NOTE: Full pipeline not yet implemented")
        print("   ✅ Phase 4: Export Extractor (DONE)")
        print("   ✅ Phase 5: Analytics Engine (DONE)")
        print("   - Phase 6: Report Builder (pending)")
        print()

        return 0

    except ValueError as e:
        print(f"\n❌ Configuration Error:")
        print(str(e))
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected Error:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
