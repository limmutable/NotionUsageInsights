"""
Markdown Report Builder for Notion Workspace Analytics

Generates comprehensive analytics reports in Markdown format.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from config import Config


class MarkdownReportBuilder:
    """
    Generates comprehensive Markdown reports from analytics results

    Output format is optimized for:
    - Direct import into Notion
    - Conversion to HTML/PDF with pandoc
    - Easy reading in any Markdown viewer
    """

    def __init__(self, results: Dict[str, Any], workspace_name: str = "Notion Workspace"):
        """
        Initialize report builder with analytics results

        Args:
            results: Dict containing all analytics results from WorkspaceAnalytics.run_all()
            workspace_name: Name of workspace for report title
        """
        self.results = results
        self.workspace_name = workspace_name
        self.timestamp = datetime.now()

    def generate_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Generate complete Markdown report

        Args:
            output_path: Optional custom output path. If None, uses data/output/workspace_analytics_TIMESTAMP.md

        Returns:
            Path to generated report file
        """
        if output_path is None:
            timestamp_str = self.timestamp.strftime('%Y%m%d_%H%M%S')
            output_dir = Path(Config.OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f'workspace_analytics_{timestamp_str}.md'

        # Build report sections
        sections = [
            self._write_header(),
            self._write_executive_summary(),
            self._write_growth(),
            self._write_users(),
            self._write_content_health(),
            self._write_collaboration(),
            self._write_costs(),
            self._write_risk(),
            self._write_detailed_tables()
        ]

        # Combine sections with separators
        report_content = '\n\n---\n\n'.join(sections)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return output_path

    # ==================== Helper Methods ====================

    def _format_table(self, data: List[Dict[str, Any]], headers: List[str],
                      alignments: Optional[List[str]] = None) -> str:
        """
        Convert data to Markdown table

        Args:
            data: List of dicts with data
            headers: List of column headers
            alignments: List of 'left', 'right', 'center' for each column (default: left)

        Returns:
            Markdown table string
        """
        if not data:
            return "_No data available_"

        if alignments is None:
            alignments = ['left'] * len(headers)

        # Build header row
        header_row = '| ' + ' | '.join(headers) + ' |'

        # Build separator row
        separator_parts = []
        for align in alignments:
            if align == 'right':
                separator_parts.append('---:')
            elif align == 'center':
                separator_parts.append(':---:')
            else:  # left
                separator_parts.append(':---')
        separator_row = '| ' + ' | '.join(separator_parts) + ' |'

        # Build data rows
        data_rows = []
        for row in data:
            cells = [str(row.get(h, '')) for h in headers]
            data_rows.append('| ' + ' | '.join(cells) + ' |')

        return '\n'.join([header_row, separator_row] + data_rows)

    def _format_percentage(self, value: float, include_icon: bool = False) -> str:
        """Format percentage with optional status icon"""
        formatted = f"{value:.1f}%"
        if include_icon:
            if value < 20:
                return f"✅ {formatted}"
            elif value < 50:
                return f"⚠️ {formatted}"
            else:
                return f"❌ {formatted}"
        return formatted

    def _format_currency(self, value: float) -> str:
        """Format currency with $ symbol"""
        return f"${value:,.0f}"

    def _get_status_icon(self, metric: str, value: float) -> str:
        """
        Get status icon based on metric and value using Config thresholds

        Args:
            metric: Name of metric (e.g., 'stale_percentage', 'bus_factor')
            value: Metric value

        Returns:
            Status icon: ✅ (good), ⚠️ (warning), ❌ (critical)
        """
        from config import Config

        # Build thresholds from Config (allows user customization)
        thresholds = {
            'stale_percentage': [
                (Config.STALE_GOOD_THRESHOLD, '✅'),
                (Config.STALE_WARNING_THRESHOLD, '⚠️'),
                (100, '❌')
            ],
            'bus_factor': [
                (Config.BUS_FACTOR_CRITICAL, '❌'),
                (Config.BUS_FACTOR_WARNING, '⚠️'),
                (float('inf'), '✅')
            ],
            'gini_coefficient': [
                (Config.GINI_GOOD_THRESHOLD, '✅'),
                (Config.GINI_WARNING_THRESHOLD, '⚠️'),
                (1.0, '❌')
            ],
            'wasted_percentage': [
                (Config.WASTE_GOOD_THRESHOLD, '✅'),
                (Config.WASTE_WARNING_THRESHOLD, '⚠️'),
                (100, '❌')
            ],
            'collaboration_score': [
                (Config.COLLAB_CRITICAL, '❌'),
                (Config.COLLAB_WARNING, '⚠️'),
                (float('inf'), '✅')
            ]
        }

        if metric not in thresholds:
            return ''

        for threshold, icon in thresholds[metric]:
            if value <= threshold:
                return icon

        return ''

    # ==================== Section Writers ====================

    def _write_header(self) -> str:
        """Generate report header with title and TOC"""
        date_str = self.timestamp.strftime('%B %d, %Y at %I:%M %p')

        return f"""# {self.workspace_name} Analytics Report

**Generated:** {date_str}

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Growth & Velocity](#growth--velocity)
3. [User Analytics](#user-analytics)
4. [Content Health](#content-health)
5. [Collaboration Patterns](#collaboration-patterns)
6. [Cost Analysis](#cost-analysis)
7. [Risk Assessment](#risk-assessment)
8. [Detailed Tables](#detailed-tables)
"""

    def _write_executive_summary(self) -> str:
        """Generate executive summary with key metrics"""
        summary = self.results['summary']
        health = self.results['content_health']
        costs = self.results['costs']
        risk = self.results['risk']

        stale_icon = self._get_status_icon('stale_percentage', health['stale_percentage'])
        bus_icon = self._get_status_icon('bus_factor', risk['bus_factor'])
        gini_icon = self._get_status_icon('gini_coefficient', risk['gini_coefficient'])

        current_creators = summary.get('current_creators', 0)
        deleted_creators = summary.get('deleted_creators', 0)
        inactive_users = summary['inactive_users']

        current_pct = current_creators/summary['total_users']*100 if summary['total_users'] > 0 else 0
        inactive_pct = inactive_users/summary['total_users']*100 if summary['total_users'] > 0 else 0

        return f"""## Executive Summary

> **About this data:**
> - **Total Pages:** All pages currently in your workspace (across all time periods)
> - **Total Users:** Current active users in your workspace
> - **Active Contributors:** {summary['active_contributors']} total ({current_creators} current users + {deleted_creators} deleted users)
> - **Inactive Users:** Current users who have never created any pages

### Quick Stats

| Metric | Value | Status |
|:---|---:|:---:|
| **Total Pages** | {summary['total_pages']:,} | - |
| **Total Users (Current)** | {summary['total_users']:,} | - |
| **Current Active Creators** | {current_creators:,} ({current_pct:.1f}%) | - |
| **Deleted User Pages** | From {deleted_creators} deleted users | - |
| **Inactive Users** | {inactive_users:,} ({inactive_pct:.1f}%) | - |
| **Stale Pages (12mo+)** | {health['stale_percentage']:.1f}% | {stale_icon} |
| **Annual Cost** | {self._format_currency(summary['annual_cost'])} | - |
| **Cost per Active User** | {self._format_currency(summary['cost_per_active_user'])} | - |
| **Bus Factor** | {risk['bus_factor']} people | {bus_icon} |
| **Gini Coefficient** | {risk['gini_coefficient']:.3f} | {gini_icon} |

### Key Insights

- 📊 **Workspace has {summary['total_pages']:,} total pages** created over time
- 👥 **{current_creators} of {summary['total_users']} current users** have created pages ({current_pct:.1f}%)
- 👻 **{deleted_creators} deleted users** created pages that still remain in the workspace
- 🚫 **{inactive_users} current users ({inactive_pct:.1f}%)** have never created a page
- 📉 **{health['stale_percentage']:.1f}% of content** hasn't been updated in over a year
- 💰 **Annual workspace cost:** {self._format_currency(costs['total_annual_cost'])} ({self._format_currency(costs['cost_per_active_creator'])} per active creator)
- ⚠️ **Knowledge risk:** Bus factor of {risk['bus_factor']} (if {risk['bus_factor']} key people leave, 50% of knowledge is at risk)
"""

    def _write_growth(self) -> str:
        """Generate growth and velocity section"""
        growth = self.results['growth']

        # Annual growth table
        annual_data = []
        years = sorted(growth['annual_counts'].keys())
        for year in years:
            count = growth['annual_counts'][year]
            yoy = growth['yoy_growth'].get(year, '')
            yoy_str = f"+{yoy}%" if yoy and yoy > 0 else f"{yoy}%" if yoy else '-'
            annual_data.append({
                'Year': year,
                'Pages Created': f"{count:,}",
                'YoY Growth': yoy_str
            })

        annual_table = self._format_table(
            annual_data,
            ['Year', 'Pages Created', 'YoY Growth'],
            ['left', 'right', 'right']
        )

        # Monthly trend (last 12 months)
        monthly_data = []
        for month, count in sorted(growth['monthly_last_12'].items()):
            monthly_data.append({
                'Month': month,
                'Pages Created': count
            })

        monthly_table = self._format_table(
            monthly_data[-12:],  # Last 12 months
            ['Month', 'Pages Created'],
            ['left', 'right']
        ) if monthly_data else "_No recent data_"

        return f"""## Growth & Velocity

### Annual Growth

{annual_table}

**Average monthly pages (last 12 months):** {growth['avg_monthly_pages']:.1f}

### Monthly Trend (Last 12 Months)

{monthly_table}
"""

    def _write_users(self) -> str:
        """Generate user analytics section"""
        users = self.results['users']
        top_creators = self.results['top_creators']

        # User segmentation
        segments = users['segments']
        total_users = sum(segments.values())

        segment_data = [
            {
                'Segment': '🔥 Power Creators (100+/year)',
                'Count': segments['power_creators'],
                'Percentage': f"{segments['power_creators']/total_users*100:.1f}%" if total_users > 0 else "0.0%"
            },
            {
                'Segment': '✨ Active Creators (20-99/year)',
                'Count': segments['active_creators'],
                'Percentage': f"{segments['active_creators']/total_users*100:.1f}%" if total_users > 0 else "0.0%"
            },
            {
                'Segment': '📝 Occasional Creators (5-19/year)',
                'Count': segments['occasional_creators'],
                'Percentage': f"{segments['occasional_creators']/total_users*100:.1f}%" if total_users > 0 else "0.0%"
            },
            {
                'Segment': '🌱 Minimal Creators (1-4/year)',
                'Count': segments['minimal_creators'],
                'Percentage': f"{segments['minimal_creators']/total_users*100:.1f}%" if total_users > 0 else "0.0%"
            },
            {
                'Segment': '👻 Non-Creators (0/year)',
                'Count': segments['non_creators'],
                'Percentage': f"{segments['non_creators']/total_users*100:.1f}%" if total_users > 0 else "0.0%"
            }
        ]

        segment_table = self._format_table(
            segment_data,
            ['Segment', 'Count', 'Percentage'],
            ['left', 'right', 'right']
        )

        # Top creators
        creator_data = []
        for i, creator in enumerate(top_creators[:10], 1):
            creator_data.append({
                'Rank': f"#{i}",
                'Name': creator['name'],
                'Pages Created': f"{creator['page_count']:,}",
                '% of Total': f"{creator['percentage']:.1f}%"
            })

        creator_table = self._format_table(
            creator_data,
            ['Rank', 'Name', 'Pages Created', '% of Total'],
            ['center', 'left', 'right', 'right']
        )

        active_count = sum([segments['power_creators'], segments['active_creators'], segments['occasional_creators'], segments['minimal_creators']])

        return f"""## User Analytics

### User Segmentation

{segment_table}

**Active creator rate:** {users['active_creator_percentage']:.1f}% ({active_count} of {total_users} users)

### Top 10 Creators

{creator_table}
"""

    def _write_content_health(self) -> str:
        """Generate content health section"""
        health = self.results['content_health']

        # Staleness distribution
        staleness_data = []
        staleness_order = [
            'Active (< 1 month)',
            'Fresh (1-3 months)',
            'Aging (3-6 months)',
            'Stale (6-12 months)',
            'Very Stale (12-24 months)',
            'Dead (24+ months)'
        ]

        total_pages = sum(health['staleness_distribution'].values())
        for category in staleness_order:
            count = health['staleness_distribution'].get(category, 0)
            percentage = (count / total_pages * 100) if total_pages > 0 else 0

            # Add visual indicator
            if 'Active' in category or 'Fresh' in category:
                icon = '✅'
            elif 'Aging' in category or 'Stale' in category:
                icon = '⚠️'
            else:
                icon = '❌'

            staleness_data.append({
                'Status': f"{icon} {category}",
                'Count': f"{count:,}",
                'Percentage': f"{percentage:.1f}%"
            })

        staleness_table = self._format_table(
            staleness_data,
            ['Status', 'Count', 'Percentage'],
            ['left', 'right', 'right']
        )

        stale_icon = self._get_status_icon('stale_percentage', health['stale_percentage'])

        return f"""## Content Health

### Staleness Distribution

{staleness_table}

### Key Health Metrics

| Metric | Value | Status |
|:---|---:|:---:|
| **Stale Pages (12mo+)** | {health['stale_pages']:,} ({health['stale_percentage']:.1f}%) | {stale_icon} |
| **Very Stale Pages (24mo+)** | {health['very_stale_pages']:,} ({health.get('very_stale_percentage', 0):.1f}%) | - |
| **Abandoned Pages** | {health['abandoned_pages']:,} ({health['abandoned_percentage']:.1f}%) | - |
| **Archived Pages** | {health.get('archived_pages', 0):,} | - |

### Insights

- {health['stale_percentage']:.1f}% of pages haven't been updated in over a year
- {health['abandoned_percentage']:.1f}% of pages were never edited after creation
- Consider archiving or deleting very stale pages to improve searchability
"""

    def _write_collaboration(self) -> str:
        """Generate collaboration patterns section"""
        collab = self.results['collaboration']

        # Top collaborators
        collab_data = []
        for i, user in enumerate(collab['top_collaborators'][:10], 1):
            collab_data.append({
                'Rank': f"#{i}",
                'Name': user['name'],
                'Pages Created': user['pages_created'],
                'Others Pages Edited': user['others_pages_edited'],
                'Collaboration Score': f"{user['collaboration_score']:.1f}%"
            })

        collab_table = self._format_table(
            collab_data,
            ['Rank', 'Name', 'Pages Created', 'Others Pages Edited', 'Collaboration Score'],
            ['center', 'left', 'right', 'right', 'right']
        ) if collab_data else "_No collaboration data_"

        avg_score = collab['average_collaboration_score']
        if avg_score > 100:
            collaboration_level = "strong cross-functional collaboration"
        elif avg_score > 50:
            collaboration_level = "moderate collaboration"
        else:
            collaboration_level = "limited collaboration"

        return f"""## Collaboration Patterns

### Top 10 Collaborators

{collab_table}

**Collaboration Score** = (Pages edited by others / Pages created) × 100

### Summary Metrics

| Metric | Value |
|:---|---:|
| **Average Collaboration Score** | {collab['average_collaboration_score']:.1f}% |
| **Collaborated Pages** | {collab['collaborated_pages']:,} ({collab['collaboration_percentage']:.1f}%) |
| **Single-Owner Pages** | {collab['single_owner_pages']:,} |

### Insights

- {collab['collaboration_percentage']:.1f}% of pages have been edited by someone other than the creator
- Average collaboration score of {collab['average_collaboration_score']:.1f}% indicates {collaboration_level}
"""

    def _write_costs(self) -> str:
        """Generate cost analysis section"""
        costs = self.results['costs']
        users = self.results['users']

        # Cost by segment
        cost_data = []
        segments = users['segments']
        segment_names = {
            'power_creators': '🔥 Power Creators',
            'active_creators': '✨ Active Creators',
            'occasional_creators': '📝 Occasional Creators',
            'minimal_creators': '🌱 Minimal Creators',
            'non_creators': '👻 Non-Creators'
        }

        for segment_key, segment_name in segment_names.items():
            count = segments[segment_key]
            monthly_cost = count * Config.MONTHLY_COST_PER_USER
            annual_cost = monthly_cost * 12

            cost_data.append({
                'Segment': segment_name,
                'Users': count,
                'Monthly Cost': self._format_currency(monthly_cost),
                'Annual Cost': self._format_currency(annual_cost)
            })

        cost_table = self._format_table(
            cost_data,
            ['Segment', 'Users', 'Monthly Cost', 'Annual Cost'],
            ['left', 'right', 'right', 'right']
        )

        waste_icon = self._get_status_icon('wasted_percentage', costs.get('wasted_spend_percentage', 0))

        return f"""## Cost Analysis

### Cost by User Segment

{cost_table}

### Financial Summary

| Metric | Value | Status |
|:---|---:|:---:|
| **Total Annual Cost** | {self._format_currency(costs['total_annual_cost'])} | - |
| **Cost per Active Creator** | {self._format_currency(costs['cost_per_active_creator'])} | - |
| **Wasted Spend (Non-creators)** | {self._format_currency(costs['wasted_spend_annual'])} ({costs['wasted_spend_percentage']:.1f}%) | {waste_icon} |
| **Content Creation Value** | {self._format_currency(costs['total_creation_value'])} | - |
| **ROI** | {costs['roi_percentage']:.1f}% | - |

### Assumptions

- **Monthly cost per user:** {self._format_currency(costs['monthly_cost_per_user'])}
- **Blended hourly rate:** {self._format_currency(costs['blended_hourly_rate'])}
- **Avg time per page:** 1 hour

### Insights

- {costs['wasted_spend_percentage']:.1f}% of annual spend ({self._format_currency(costs['wasted_spend_annual'])}) is on non-creators
- ROI of {costs['roi_percentage']:.1f}% based on estimated content creation value
- Consider rightsizing licenses for inactive users
"""

    def _write_risk(self) -> str:
        """Generate risk assessment section"""
        risk = self.results['risk']

        # Concentration metrics
        conc = risk['concentration']
        conc_data = [
            {
                'Metric': 'Top 1% of Creators',
                'Users': conc['top_1_percent']['users'],
                'Pages Created': f"{conc['top_1_percent']['pages']:,}",
                '% of Total': f"{conc['top_1_percent']['percentage']:.1f}%"
            },
            {
                'Metric': 'Top 5% of Creators',
                'Users': conc['top_5_percent']['users'],
                'Pages Created': f"{conc['top_5_percent']['pages']:,}",
                '% of Total': f"{conc['top_5_percent']['percentage']:.1f}%"
            },
            {
                'Metric': 'Top 10% of Creators',
                'Users': conc['top_10_percent']['users'],
                'Pages Created': f"{conc['top_10_percent']['pages']:,}",
                '% of Total': f"{conc['top_10_percent']['percentage']:.1f}%"
            }
        ]

        conc_table = self._format_table(
            conc_data,
            ['Metric', 'Users', 'Pages Created', '% of Total'],
            ['left', 'right', 'right', 'right']
        )

        bus_icon = self._get_status_icon('bus_factor', risk['bus_factor'])
        gini_icon = self._get_status_icon('gini_coefficient', risk['gini_coefficient'])

        # Gini interpretation
        if risk['gini_coefficient'] < 0.5:
            gini_interp = "relatively equal distribution"
        elif risk['gini_coefficient'] < 0.7:
            gini_interp = "moderate concentration"
        else:
            gini_interp = "high concentration"

        # Risk level
        if risk['bus_factor'] < 5:
            risk_level = "⚠️ HIGH RISK: Consider knowledge transfer and documentation"
            knowledge_dist = "highly concentrated"
        elif risk['bus_factor'] < 10:
            risk_level = "✅ MODERATE RISK: Monitor key contributors"
            knowledge_dist = "moderately concentrated"
        else:
            risk_level = "✅ LOW RISK: Knowledge is well distributed"
            knowledge_dist = "well distributed"

        return f"""## Risk Assessment

### Ownership Concentration

{conc_table}

### Risk Metrics

| Metric | Value | Status |
|:---|---:|:---:|
| **Gini Coefficient** | {risk['gini_coefficient']:.3f} | {gini_icon} |
| **Bus Factor** | {risk['bus_factor']} people | {bus_icon} |

### Understanding the Metrics

**Gini Coefficient** measures inequality in page ownership:
- 0.0 = Perfect equality (everyone creates equal pages)
- 1.0 = Perfect inequality (one person creates all pages)
- **Current: {risk['gini_coefficient']:.3f}** indicates {gini_interp}

**Bus Factor** is the minimum number of people who need to leave before 50% of knowledge is at risk:
- **Current: {risk['bus_factor']}** people hold critical knowledge

### Insights

- Top 10% of creators are responsible for {conc['top_10_percent']['percentage']:.1f}% of all content
- Knowledge is {knowledge_dist}
- {risk_level}
"""

    def _write_detailed_tables(self) -> str:
        """Generate detailed data tables section"""
        users = self.results['users']

        return f"""## Detailed Tables

### User Segments Breakdown

| Segment | Threshold | Count | Pages/Year Range |
|:---|:---|---:|:---|
| Power Creators | 100+/year | {users['segments']['power_creators']} | 100+ |
| Active Creators | 20-99/year | {users['segments']['active_creators']} | 20-99 |
| Occasional Creators | 5-19/year | {users['segments']['occasional_creators']} | 5-19 |
| Minimal Creators | 1-4/year | {users['segments']['minimal_creators']} | 1-4 |
| Non-Creators | 0/year | {users['segments']['non_creators']} | 0 |

### Staleness Definitions

| Category | Last Edited | Risk Level |
|:---|:---|:---:|
| Active | < 1 month | ✅ Low |
| Fresh | 1-3 months | ✅ Low |
| Aging | 3-6 months | ⚠️ Medium |
| Stale | 6-12 months | ⚠️ Medium |
| Very Stale | 12-24 months | ❌ High |
| Dead | 24+ months | ❌ High |

---

**Report generated with [Notion Usage Insights](https://github.com/your-repo/NotionUsageInsights)**
"""
