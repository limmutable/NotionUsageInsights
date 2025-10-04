"""
Workspace analytics engine for Notion data
Calculates growth metrics, user engagement, content health, and more
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from config import Config


class WorkspaceAnalytics:
    """Analytics engine for Notion workspace data"""

    def __init__(self, pages: List[Dict[str, Any]], users: Dict[str, Dict[str, Any]]):
        """
        Initialize analytics engine with workspace data

        Args:
            pages: List of page dicts with metadata (from API + export)
            users: Dict of user data {user_id: {name, email, type}}
        """
        self.users = users
        self.df = pd.DataFrame(pages)

        # Prepare dataframe with derived columns
        if not self.df.empty:
            self._prepare_dataframe()

    def _prepare_dataframe(self) -> None:
        """
        Add derived columns to dataframe for analysis

        Adds:
        - Datetime conversions
        - User names
        - Time-based groupings (year, quarter, month)
        - Staleness categories
        - Flags (abandoned, single-owner, template)
        """
        # Convert timestamps to datetime
        self.df['created_time'] = pd.to_datetime(self.df['created_time'])
        self.df['last_edited_time'] = pd.to_datetime(self.df['last_edited_time'])

        # Add user names
        self.df['creator_name'] = self.df['created_by'].map(
            lambda uid: self.users.get(uid, {}).get('name', 'Unknown')
        )
        self.df['editor_name'] = self.df['last_edited_by'].map(
            lambda uid: self.users.get(uid, {}).get('name', 'Unknown')
        )

        # Time-based groupings
        self.df['created_year'] = self.df['created_time'].dt.year
        self.df['created_quarter'] = self.df['created_time'].dt.to_period('Q').astype(str)
        self.df['created_month'] = self.df['created_time'].dt.to_period('M').astype(str)

        # Calculate days since last edit
        now = pd.Timestamp.now()
        self.df['days_since_edit'] = (now - self.df['last_edited_time']).dt.days

        # Staleness categories
        def categorize_staleness(days: int) -> str:
            if days < 30:
                return 'Active (< 1 month)'
            elif days < 90:
                return 'Fresh (1-3 months)'
            elif days < 180:
                return 'Aging (3-6 months)'
            elif days < 365:
                return 'Stale (6-12 months)'
            elif days < 730:
                return 'Very Stale (12-24 months)'
            else:
                return 'Dead (24+ months)'

        self.df['staleness'] = self.df['days_since_edit'].apply(categorize_staleness)

        # Flags
        self.df['is_abandoned'] = (
            self.df['created_time'] == self.df['last_edited_time']
        )
        self.df['is_single_owner'] = (
            self.df['created_by'] == self.df['last_edited_by']
        )

        # Detect templates (pages with "template" in title, case-insensitive)
        if 'title' in self.df.columns:
            self.df['is_template'] = self.df['title'].str.lower().str.contains(
                'template', na=False
            )
        else:
            self.df['is_template'] = False

    def _analyze_summary(self) -> Dict[str, Any]:
        """
        Calculate summary metrics

        Returns:
            Dict with total_pages, total_users, active_contributors, etc.
        """
        total_pages = len(self.df)
        total_users = len(self.users)

        # Active contributors (users who created at least 1 page)
        active_contributors = self.df['created_by'].nunique() if not self.df.empty else 0

        # Stale percentage (pages not edited in 12+ months)
        stale_pages = len(self.df[self.df['days_since_edit'] >= 365]) if not self.df.empty else 0
        stale_percentage = (stale_pages / total_pages * 100) if total_pages > 0 else 0

        # Cost per active user
        annual_cost = total_users * Config.MONTHLY_COST_PER_USER * 12
        cost_per_active = (annual_cost / active_contributors) if active_contributors > 0 else 0

        return {
            'total_pages': total_pages,
            'total_users': total_users,
            'active_contributors': active_contributors,
            'inactive_users': total_users - active_contributors,
            'stale_pages': stale_pages,
            'stale_percentage': round(stale_percentage, 1),
            'annual_cost': annual_cost,
            'cost_per_active_user': round(cost_per_active, 2)
        }

    def _analyze_growth(self) -> Dict[str, Any]:
        """
        Analyze page creation growth over time

        Returns:
            Dict with annual, quarterly, and monthly breakdowns
        """
        if self.df.empty:
            return {
                'annual_counts': {},
                'yoy_growth': {},
                'quarterly_latest_year': {},
                'monthly_last_12': {},
                'avg_monthly_pages': 0.0
            }

        # Annual page counts
        annual_counts = self.df.groupby('created_year').size().to_dict()

        # Calculate year-over-year growth rates
        years = sorted(annual_counts.keys())
        yoy_growth = {}
        for i in range(1, len(years)):
            prev_year = years[i-1]
            curr_year = years[i]
            growth = ((annual_counts[curr_year] - annual_counts[prev_year])
                     / annual_counts[prev_year] * 100)
            yoy_growth[curr_year] = round(growth, 1)

        # Quarterly breakdown (latest year)
        latest_year = max(years) if years else datetime.now().year
        quarterly_data = self.df[self.df['created_year'] == latest_year].groupby(
            'created_quarter'
        ).size().to_dict()

        # Monthly breakdown (last 12 months)
        twelve_months_ago = pd.Timestamp.now() - pd.DateOffset(months=12)
        recent_pages = self.df[self.df['created_time'] >= twelve_months_ago]
        monthly_data = recent_pages.groupby('created_month').size().to_dict()

        # Average monthly pages (last 12 months)
        avg_monthly = recent_pages.groupby('created_month').size().mean()

        return {
            'annual_counts': annual_counts,
            'yoy_growth': yoy_growth,
            'quarterly_latest_year': quarterly_data,
            'monthly_last_12': monthly_data,
            'avg_monthly_pages': round(avg_monthly, 1)
        }

    def _analyze_users(self) -> Dict[str, Any]:
        """
        Analyze user segmentation and activity

        Returns:
            Dict with user segments and their page counts
        """
        if self.df.empty:
            return {
                'power_creators': 0,
                'active_creators': 0,
                'occasional_creators': 0,
                'minimal_creators': 0,
                'non_creators': len(self.users)
            }

        # Count pages per user
        pages_per_user = self.df.groupby('created_by').size()

        # Calculate pages per year for each user
        user_creation_dates = self.df.groupby('created_by')['created_time'].agg(['min', 'max'])

        def calculate_annual_rate(user_id: str) -> float:
            if user_id not in pages_per_user:
                return 0

            pages = pages_per_user[user_id]
            if user_id not in user_creation_dates.index:
                return 0

            first_page = user_creation_dates.loc[user_id, 'min']
            last_page = user_creation_dates.loc[user_id, 'max']

            # Calculate years active (minimum 1 year)
            years_active = max((last_page - first_page).days / 365.25, 1.0)

            return pages / years_active

        # Segment users
        segments = {
            'power_creators': 0,      # 100+ pages/year
            'active_creators': 0,     # 20-99 pages/year
            'occasional_creators': 0, # 5-19 pages/year
            'minimal_creators': 0,    # 1-4 pages/year
            'non_creators': 0         # 0 pages
        }

        pages_by_segment = {seg: 0 for seg in segments.keys()}

        for user_id in self.users.keys():
            annual_rate = calculate_annual_rate(user_id)

            if annual_rate >= Config.POWER_USER_THRESHOLD:
                segments['power_creators'] += 1
                pages_by_segment['power_creators'] += pages_per_user.get(user_id, 0)
            elif annual_rate >= Config.ACTIVE_USER_THRESHOLD:
                segments['active_creators'] += 1
                pages_by_segment['active_creators'] += pages_per_user.get(user_id, 0)
            elif annual_rate >= Config.OCCASIONAL_USER_THRESHOLD:
                segments['occasional_creators'] += 1
                pages_by_segment['occasional_creators'] += pages_per_user.get(user_id, 0)
            elif annual_rate > 0:
                segments['minimal_creators'] += 1
                pages_by_segment['minimal_creators'] += pages_per_user.get(user_id, 0)
            else:
                segments['non_creators'] += 1

        # Calculate active creator percentage
        total_users = len(self.users)
        active_creators = total_users - segments['non_creators']
        active_percentage = (active_creators / total_users * 100) if total_users > 0 else 0

        return {
            'segments': segments,
            'pages_by_segment': pages_by_segment,
            'active_creator_percentage': round(active_percentage, 1)
        }

    def _analyze_top_creators(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top creators by page count

        Args:
            limit: Number of top creators to return

        Returns:
            List of dicts with user info and page counts
        """
        if self.df.empty:
            return []

        # Count pages per user
        pages_per_user = self.df.groupby('created_by').size().reset_index(
            name='page_count'
        )

        # Sort and get top N
        top_creators = pages_per_user.nlargest(limit, 'page_count')

        # Add user names and percentage
        total_pages = len(self.df)
        results = []

        for _, row in top_creators.iterrows():
            user_id = row['created_by']
            page_count = row['page_count']
            percentage = (page_count / total_pages * 100) if total_pages > 0 else 0

            results.append({
                'user_id': user_id,
                'name': self.users.get(user_id, {}).get('name', 'Unknown'),
                'page_count': int(page_count),
                'percentage': round(percentage, 1)
            })

        return results

    def _analyze_collaboration(self) -> Dict[str, Any]:
        """
        Analyze collaboration patterns

        Collaboration score = (others_pages_edited / pages_created) × 100
        where others_pages = pages last_edited_by user but created_by someone else

        Returns:
            Dict with collaboration metrics
        """
        if self.df.empty:
            return {
                'user_scores': [],
                'avg_collaboration_score': 0.0,
                'high_collaborators': 0,
                'siloed_creators': len(self.users)
            }

        results = []

        for user_id, user_info in self.users.items():
            # Pages created by this user
            created_pages = len(self.df[self.df['created_by'] == user_id])

            # Pages edited by this user but created by someone else
            others_pages = len(self.df[
                (self.df['last_edited_by'] == user_id) &
                (self.df['created_by'] != user_id)
            ])

            # Calculate collaboration score
            if created_pages > 0:
                score = (others_pages / created_pages) * 100
            else:
                score = 0.0

            results.append({
                'user_id': user_id,
                'name': user_info.get('name', 'Unknown'),
                'pages_created': created_pages,
                'others_pages_edited': others_pages,
                'collaboration_score': round(score, 1)
            })

        # Sort by collaboration score
        results.sort(key=lambda x: x['collaboration_score'], reverse=True)

        # Top 10 collaborators
        top_collaborators = results[:10]

        # Calculate averages (only for users who created pages)
        active_users = [r for r in results if r['pages_created'] > 0]
        avg_score = sum(r['collaboration_score'] for r in active_users) / len(active_users) if active_users else 0

        # Count collaborated pages (pages where creator ≠ last editor)
        collaborated_pages = len(self.df[self.df['created_by'] != self.df['last_edited_by']])
        single_owner_pages = len(self.df[self.df['created_by'] == self.df['last_edited_by']])

        return {
            'top_collaborators': top_collaborators,
            'average_collaboration_score': round(avg_score, 1),
            'collaborated_pages': collaborated_pages,
            'single_owner_pages': single_owner_pages,
            'collaboration_percentage': round(
                (collaborated_pages / len(self.df) * 100) if len(self.df) > 0 else 0, 1
            )
        }

    def _analyze_content_health(self) -> Dict[str, Any]:
        """
        Analyze content health and staleness

        Returns:
            Dict with staleness distribution and health metrics
        """
        if self.df.empty:
            return {
                'staleness_distribution': {},
                'stale_pages': 0,
                'very_stale_pages': 0,
                'abandoned_pages': 0,
                'single_owner_pages': 0,
                'stale_percentage': 0.0,
                'abandoned_percentage': 0.0
            }

        # Staleness distribution
        staleness_dist = self.df['staleness'].value_counts().to_dict()

        # Stale (12mo+) and very stale (24mo+) counts
        stale_pages = len(self.df[self.df['days_since_edit'] >= 365])
        very_stale_pages = len(self.df[self.df['days_since_edit'] >= 730])

        # Abandoned pages (never edited after creation)
        abandoned_pages = len(self.df[self.df['is_abandoned']])

        # Abandoned pages by top creators
        top_creator_ids = self.df.groupby('created_by').size().nlargest(10).index.tolist()
        abandoned_by_top = self.df[
            (self.df['is_abandoned']) &
            (self.df['created_by'].isin(top_creator_ids))
        ]
        abandoned_by_top_count = len(abandoned_by_top)

        # Archived pages count
        archived_pages = len(self.df[self.df.get('archived', False)])

        # Calculate percentages
        total_pages = len(self.df)
        stale_pct = (stale_pages / total_pages * 100) if total_pages > 0 else 0
        very_stale_pct = (very_stale_pages / total_pages * 100) if total_pages > 0 else 0
        abandoned_pct = (abandoned_pages / total_pages * 100) if total_pages > 0 else 0

        return {
            'staleness_distribution': staleness_dist,
            'stale_pages': stale_pages,
            'stale_percentage': round(stale_pct, 1),
            'very_stale_pages': very_stale_pages,
            'very_stale_percentage': round(very_stale_pct, 1),
            'abandoned_pages': abandoned_pages,
            'abandoned_percentage': round(abandoned_pct, 1),
            'abandoned_by_top_creators': abandoned_by_top_count,
            'archived_pages': archived_pages
        }

    def _analyze_costs(self) -> Dict[str, Any]:
        """
        Analyze cost metrics and ROI

        Returns:
            Dict with cost analysis by segment and waste calculations
        """
        if self.df.empty:
            total_users = len(self.users)
            annual_cost = total_users * Config.MONTHLY_COST_PER_USER * 12
            return {
                'annual_cost': annual_cost,
                'cost_per_active_user': 0.0,
                'cost_by_segment': {},
                'wasted_licenses': total_users,
                'wasted_cost': annual_cost,
                'roi_estimate': 0.0
            }

        # Get user segments
        user_analysis = self._analyze_users()
        segments = user_analysis['segments']

        # Calculate cost by segment
        monthly_cost_per_user = Config.MONTHLY_COST_PER_USER
        cost_by_segment = {}

        for segment, count in segments.items():
            monthly_cost = count * monthly_cost_per_user
            annual_cost = monthly_cost * 12
            cost_by_segment[segment] = {
                'users': count,
                'monthly_cost': monthly_cost,
                'annual_cost': annual_cost
            }

        # Total annual cost
        total_users = len(self.users)
        total_annual_cost = total_users * monthly_cost_per_user * 12

        # Active creators (users who created at least 1 page)
        active_contributors = self.df['created_by'].nunique()

        # Cost per active creator
        cost_per_active = (total_annual_cost / active_contributors) if active_contributors > 0 else 0

        # Wasted spend (cost of non-creators)
        non_creators = segments.get('non_creators', 0)
        wasted_annual = non_creators * monthly_cost_per_user * 12
        waste_percentage = (wasted_annual / total_annual_cost * 100) if total_annual_cost > 0 else 0

        # ROI calculation (creation value vs. cost)
        # Assume each page created has value = blended hourly rate
        page_value = Config.BLENDED_HOURLY_RATE
        total_pages = len(self.df)
        total_creation_value = total_pages * page_value

        roi = ((total_creation_value - total_annual_cost) / total_annual_cost * 100) if total_annual_cost > 0 else 0

        return {
            'cost_by_segment': cost_by_segment,
            'total_annual_cost': total_annual_cost,
            'cost_per_active_creator': round(cost_per_active, 2),
            'wasted_spend_annual': wasted_annual,
            'wasted_spend_percentage': round(waste_percentage, 1),
            'total_creation_value': total_creation_value,
            'roi_percentage': round(roi, 1),
            'monthly_cost_per_user': monthly_cost_per_user,
            'blended_hourly_rate': Config.BLENDED_HOURLY_RATE
        }

    def _analyze_structure(self) -> Dict[str, Any]:
        """
        Analyze structural patterns in content

        Returns:
            Dict with template and content type metrics
        """
        if self.df.empty:
            return {
                'templates_count': 0,
                'databases_count': 0,
                'pages_count': 0,
                'template_percentage': 0.0
            }
        total_pages = len(self.df)

        # Template detection
        template_pages = len(self.df[self.df['is_template']])
        template_percentage = (template_pages / total_pages * 100) if total_pages > 0 else 0

        # Non-template pages
        non_template_pages = total_pages - template_pages

        return {
            'template_count': template_pages,
            'template_percentage': round(template_percentage, 1),
            'non_template_count': non_template_pages
        }

    def _analyze_risk(self) -> Dict[str, Any]:
        """
        Analyze knowledge risk and concentration

        Returns:
            Dict with concentration metrics, Gini coefficient, and bus factor
        """
        if self.df.empty:
            return {
                'concentration': {
                    'top_1_percent': {'users': 0, 'pages': 0, 'percentage': 0.0},
                    'top_5_percent': {'users': 0, 'pages': 0, 'percentage': 0.0},
                    'top_10_percent': {'users': 0, 'pages': 0, 'percentage': 0.0}
                },
                'gini_coefficient': 0.0,
                'bus_factor': 0
            }

        # Count pages per user
        pages_per_user = self.df.groupby('created_by').size().sort_values(ascending=False)

        total_pages = len(self.df)
        total_users = len(self.users)

        # Concentration metrics (top 1%, 5%, 10%)
        top_1_pct_count = max(1, int(total_users * 0.01))
        top_5_pct_count = max(1, int(total_users * 0.05))
        top_10_pct_count = max(1, int(total_users * 0.10))

        top_1_pct_pages = pages_per_user.head(top_1_pct_count).sum()
        top_5_pct_pages = pages_per_user.head(top_5_pct_count).sum()
        top_10_pct_pages = pages_per_user.head(top_10_pct_count).sum()

        concentration = {
            'top_1_percent': {
                'users': top_1_pct_count,
                'pages': int(top_1_pct_pages),
                'percentage': round((top_1_pct_pages / total_pages * 100) if total_pages > 0 else 0, 1)
            },
            'top_5_percent': {
                'users': top_5_pct_count,
                'pages': int(top_5_pct_pages),
                'percentage': round((top_5_pct_pages / total_pages * 100) if total_pages > 0 else 0, 1)
            },
            'top_10_percent': {
                'users': top_10_pct_count,
                'pages': int(top_10_pct_pages),
                'percentage': round((top_10_pct_pages / total_pages * 100) if total_pages > 0 else 0, 1)
            }
        }

        # Gini coefficient calculation
        # Measures inequality in page distribution (0 = perfect equality, 1 = perfect inequality)
        if len(pages_per_user) > 0:
            # Add zeros for non-creators
            all_pages = list(pages_per_user.values)
            all_pages.extend([0] * (total_users - len(pages_per_user)))
            all_pages = sorted(all_pages)

            n = len(all_pages)
            cumsum = np.cumsum(all_pages)
            gini = (2 * sum((i + 1) * pages for i, pages in enumerate(all_pages))) / (n * sum(all_pages)) - (n + 1) / n if sum(all_pages) > 0 else 0
        else:
            gini = 0

        # Bus factor: minimum number of people who need to leave for 50% knowledge loss
        # Calculate cumulative percentage of pages
        cumulative_pct = 0
        bus_factor = 0
        for pages in pages_per_user.values:
            cumulative_pct += (pages / total_pages * 100) if total_pages > 0 else 0
            bus_factor += 1
            if cumulative_pct >= 50:
                break

        # Single-owner pages by top 10 creators
        top_10_creator_ids = pages_per_user.head(10).index.tolist()
        single_owner_by_top_10 = self.df[
            (self.df['is_single_owner']) &
            (self.df['created_by'].isin(top_10_creator_ids))
        ]
        single_owner_top_10_count = len(single_owner_by_top_10)

        return {
            'concentration': concentration,
            'gini_coefficient': round(gini, 3),
            'bus_factor': bus_factor,
            'single_owner_pages_top_10': single_owner_top_10_count
        }

    def run_all(self) -> Dict[str, Any]:
        """
        Run all analytics methods and return combined results

        Returns:
            Dict with all analytics results organized by category
        """
        return {
            'summary': self._analyze_summary(),
            'growth': self._analyze_growth(),
            'users': self._analyze_users(),
            'top_creators': self._analyze_top_creators(),
            'collaboration': self._analyze_collaboration(),
            'content_health': self._analyze_content_health(),
            'costs': self._analyze_costs(),
            'structure': self._analyze_structure(),
            'risk': self._analyze_risk()
        }
