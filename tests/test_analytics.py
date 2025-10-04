"""
Unit tests for analytics module
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.analytics import WorkspaceAnalytics


class TestWorkspaceAnalytics:
    """Test analytics engine functionality"""

    @pytest.fixture
    def sample_users(self):
        """Create sample user data"""
        return {
            'user-1': {'name': 'Alice', 'email': 'alice@example.com', 'type': 'person'},
            'user-2': {'name': 'Bob', 'email': 'bob@example.com', 'type': 'person'},
            'user-3': {'name': 'Charlie', 'email': 'charlie@example.com', 'type': 'person'},
        }

    @pytest.fixture
    def sample_pages(self):
        """Create sample page data"""
        now = datetime.now()
        return [
            {
                'id': 'page-1',
                'title': 'Active Page',
                'created_time': (now - timedelta(days=15)).isoformat(),
                'created_by': 'user-1',
                'last_edited_time': (now - timedelta(days=1)).isoformat(),
                'last_edited_by': 'user-2',
                'archived': False
            },
            {
                'id': 'page-2',
                'title': 'Stale Page',
                'created_time': (now - timedelta(days=400)).isoformat(),
                'created_by': 'user-1',
                'last_edited_time': (now - timedelta(days=400)).isoformat(),
                'last_edited_by': 'user-1',
                'archived': False
            },
            {
                'id': 'page-3',
                'title': 'Template Page',
                'created_time': (now - timedelta(days=100)).isoformat(),
                'created_by': 'user-2',
                'last_edited_time': (now - timedelta(days=50)).isoformat(),
                'last_edited_by': 'user-2',
                'archived': False
            },
            {
                'id': 'page-4',
                'title': 'Power User Page',
                'created_time': (now - timedelta(days=200)).isoformat(),
                'created_by': 'user-1',
                'last_edited_time': (now - timedelta(days=10)).isoformat(),
                'last_edited_by': 'user-1',
                'archived': False
            },
        ]

    @pytest.fixture
    def analytics(self, sample_pages, sample_users):
        """Create analytics instance with sample data"""
        return WorkspaceAnalytics(sample_pages, sample_users)

    def test_analytics_initialization(self, analytics):
        """Test that analytics initializes correctly"""
        assert analytics is not None
        assert len(analytics.df) == 4
        assert len(analytics.users) == 3

    def test_dataframe_preparation(self, analytics):
        """Test that dataframe has all derived columns"""
        required_columns = [
            'created_time', 'last_edited_time',
            'creator_name', 'editor_name',
            'created_year', 'created_quarter', 'created_month',
            'days_since_edit', 'staleness',
            'is_abandoned', 'is_single_owner', 'is_template'
        ]

        for col in required_columns:
            assert col in analytics.df.columns, f"Missing column: {col}"

    def test_datetime_conversion(self, analytics):
        """Test that timestamps are converted to datetime"""
        assert pd.api.types.is_datetime64_any_dtype(analytics.df['created_time'])
        assert pd.api.types.is_datetime64_any_dtype(analytics.df['last_edited_time'])

    def test_user_name_mapping(self, analytics):
        """Test that user IDs are mapped to names"""
        assert 'Alice' in analytics.df['creator_name'].values
        assert 'Bob' in analytics.df['creator_name'].values

    def test_staleness_categories(self, analytics):
        """Test staleness categorization"""
        staleness_values = analytics.df['staleness'].unique()
        assert len(staleness_values) > 0
        # Should have at least Active and Very Stale based on sample data
        assert any('Active' in s for s in staleness_values)
        assert any('Stale' in s for s in staleness_values)

    def test_abandoned_flag(self, analytics):
        """Test abandoned page detection"""
        # Page-2 has same created and edited time
        abandoned = analytics.df[analytics.df['id'] == 'page-2']['is_abandoned'].iloc[0]
        assert abandoned == True

        # Page-1 has different created and edited time
        not_abandoned = analytics.df[analytics.df['id'] == 'page-1']['is_abandoned'].iloc[0]
        assert not_abandoned == False

    def test_single_owner_flag(self, analytics):
        """Test single owner detection"""
        # Page-1 has different creator and editor
        collab = analytics.df[analytics.df['id'] == 'page-1']['is_single_owner'].iloc[0]
        assert collab == False

        # Page-2 has same creator and editor
        single = analytics.df[analytics.df['id'] == 'page-2']['is_single_owner'].iloc[0]
        assert single == True

    def test_summary_metrics(self, analytics):
        """Test summary metrics calculation"""
        summary = analytics._analyze_summary()

        assert summary['total_pages'] == 4
        assert summary['total_users'] == 3
        assert summary['active_contributors'] > 0
        assert summary['stale_percentage'] >= 0
        assert 'annual_cost' in summary
        assert 'cost_per_active_user' in summary

    def test_growth_analysis(self, analytics):
        """Test growth analysis"""
        growth = analytics._analyze_growth()

        assert 'annual_counts' in growth
        assert 'yoy_growth' in growth
        assert 'monthly_last_12' in growth
        assert 'avg_monthly_pages' in growth
        assert isinstance(growth['annual_counts'], dict)

    def test_user_segmentation(self, analytics):
        """Test user segmentation"""
        user_analysis = analytics._analyze_users()

        assert 'segments' in user_analysis
        assert 'pages_by_segment' in user_analysis
        assert 'active_creator_percentage' in user_analysis

        segments = user_analysis['segments']
        assert 'power_creators' in segments
        assert 'active_creators' in segments
        assert 'non_creators' in segments

    def test_top_creators(self, analytics):
        """Test top creators analysis"""
        top_creators = analytics._analyze_top_creators(limit=5)

        assert isinstance(top_creators, list)
        assert len(top_creators) > 0
        assert len(top_creators) <= 5

        # Check structure
        first_creator = top_creators[0]
        assert 'user_id' in first_creator
        assert 'name' in first_creator
        assert 'page_count' in first_creator
        assert 'percentage' in first_creator

    def test_template_detection(self, analytics):
        """Test template page detection"""
        template_pages = analytics.df[analytics.df['is_template']]['title'].values
        assert 'Template Page' in template_pages

    def test_empty_dataframe_handling(self):
        """Test that analytics handles empty data gracefully"""
        analytics = WorkspaceAnalytics([], {})
        assert len(analytics.df) == 0

    def test_time_groupings(self, analytics):
        """Test year/quarter/month groupings"""
        assert pd.api.types.is_integer_dtype(analytics.df['created_year'])
        assert len(analytics.df['created_quarter'].unique()) > 0
        assert len(analytics.df['created_month'].unique()) > 0


class TestAdvancedAnalytics:
    """Test advanced analytics methods (Step 2)"""

    @pytest.fixture
    def sample_users(self):
        """Create sample user data"""
        return {
            'user-1': {'name': 'Alice', 'email': 'alice@example.com', 'type': 'person'},
            'user-2': {'name': 'Bob', 'email': 'bob@example.com', 'type': 'person'},
            'user-3': {'name': 'Charlie', 'email': 'charlie@example.com', 'type': 'person'},
        }

    @pytest.fixture
    def sample_pages(self):
        """Create sample page data with collaboration scenarios"""
        now = datetime.now()
        return [
            {
                'id': 'page-1',
                'title': 'Collaborative Page',
                'created_time': (now - timedelta(days=15)).isoformat(),
                'created_by': 'user-1',
                'last_edited_time': (now - timedelta(days=1)).isoformat(),
                'last_edited_by': 'user-2',  # Different from creator
                'archived': False
            },
            {
                'id': 'page-2',
                'title': 'Stale Abandoned Page',
                'created_time': (now - timedelta(days=400)).isoformat(),
                'created_by': 'user-1',
                'last_edited_time': (now - timedelta(days=400)).isoformat(),
                'last_edited_by': 'user-1',  # Same as creator
                'archived': False
            },
            {
                'id': 'page-3',
                'title': 'Single Owner Page',
                'created_time': (now - timedelta(days=100)).isoformat(),
                'created_by': 'user-2',
                'last_edited_time': (now - timedelta(days=50)).isoformat(),
                'last_edited_by': 'user-2',  # Same as creator
                'archived': False
            },
            {
                'id': 'page-4',
                'title': 'Very Stale Page',
                'created_time': (now - timedelta(days=800)).isoformat(),
                'created_by': 'user-1',
                'last_edited_time': (now - timedelta(days=800)).isoformat(),
                'last_edited_by': 'user-1',
                'archived': True  # Archived
            },
        ]

    @pytest.fixture
    def analytics(self, sample_pages, sample_users):
        """Create analytics instance with sample data"""
        return WorkspaceAnalytics(sample_pages, sample_users)

    def test_collaboration_analysis(self, analytics):
        """Test collaboration metrics calculation"""
        collab = analytics._analyze_collaboration()

        assert 'top_collaborators' in collab
        assert 'average_collaboration_score' in collab
        assert 'collaborated_pages' in collab
        assert 'single_owner_pages' in collab
        assert 'collaboration_percentage' in collab

        # Should have 1 collaborated page (page-1)
        assert collab['collaborated_pages'] == 1
        assert collab['single_owner_pages'] == 3

    def test_collaboration_score_calculation(self, analytics):
        """Test individual collaboration scores"""
        collab = analytics._analyze_collaboration()
        top_collaborators = collab['top_collaborators']

        # Find Bob's collaboration score
        bob = next((u for u in top_collaborators if u['name'] == 'Bob'), None)
        assert bob is not None
        # Bob edited 1 page created by Alice, and created 1 page himself
        # Score = (1 / 1) * 100 = 100%
        assert bob['collaboration_score'] == 100.0

    def test_content_health_analysis(self, analytics):
        """Test content health metrics"""
        health = analytics._analyze_content_health()

        assert 'staleness_distribution' in health
        assert 'stale_pages' in health
        assert 'very_stale_pages' in health
        assert 'abandoned_pages' in health
        assert 'abandoned_by_top_creators' in health
        assert 'archived_pages' in health

        # Should have 2 stale pages (>365 days)
        assert health['stale_pages'] >= 2
        # Should have 1 very stale page (>730 days)
        assert health['very_stale_pages'] >= 1
        # Should have 3 abandoned pages (never edited)
        # Page-1 is edited by someone else (not abandoned)
        # Page-2 and Page-4 have same created/edited time (abandoned)
        assert health['abandoned_pages'] == 2

    def test_archived_pages_detection(self, analytics):
        """Test archived pages are counted correctly"""
        health = analytics._analyze_content_health()
        # Page-4 is archived
        assert health['archived_pages'] == 1

    def test_staleness_distribution(self, analytics):
        """Test staleness distribution is calculated"""
        health = analytics._analyze_content_health()
        dist = health['staleness_distribution']

        assert isinstance(dist, dict)
        assert len(dist) > 0
        # Should have different staleness categories
        assert any('Stale' in key or 'Active' in key for key in dist.keys())

    def test_cost_analysis(self, analytics):
        """Test cost analysis metrics"""
        costs = analytics._analyze_costs()

        assert 'cost_by_segment' in costs
        assert 'total_annual_cost' in costs
        assert 'cost_per_active_creator' in costs
        assert 'wasted_spend_annual' in costs
        assert 'roi_percentage' in costs

        # Should have positive annual cost
        assert costs['total_annual_cost'] > 0

    def test_cost_by_segment(self, analytics):
        """Test cost breakdown by user segment"""
        costs = analytics._analyze_costs()
        cost_by_segment = costs['cost_by_segment']

        assert isinstance(cost_by_segment, dict)
        # Should have all segment types
        assert 'non_creators' in cost_by_segment
        assert 'minimal_creators' in cost_by_segment

        # Each segment should have users, monthly_cost, annual_cost
        for segment_data in cost_by_segment.values():
            assert 'users' in segment_data
            assert 'monthly_cost' in segment_data
            assert 'annual_cost' in segment_data

    def test_wasted_spend_calculation(self, analytics):
        """Test wasted spend on non-creators"""
        costs = analytics._analyze_costs()

        # Charlie is a non-creator
        assert costs['wasted_spend_annual'] > 0
        assert costs['wasted_spend_percentage'] > 0

    def test_roi_calculation(self, analytics):
        """Test ROI calculation"""
        costs = analytics._analyze_costs()

        # Should have ROI percentage
        assert 'roi_percentage' in costs
        # ROI should be a number
        assert isinstance(costs['roi_percentage'], (int, float))

    def test_collaboration_percentage(self, analytics):
        """Test collaboration percentage calculation"""
        collab = analytics._analyze_collaboration()

        # 1 out of 4 pages is collaborated (25%)
        assert collab['collaboration_percentage'] == 25.0


class TestRiskAndStructure:
    """Test risk assessment and structure analysis (Step 3)"""

    @pytest.fixture
    def sample_users(self):
        """Create sample user data"""
        return {
            'user-1': {'name': 'Alice', 'email': 'alice@example.com', 'type': 'person'},
            'user-2': {'name': 'Bob', 'email': 'bob@example.com', 'type': 'person'},
            'user-3': {'name': 'Charlie', 'email': 'charlie@example.com', 'type': 'person'},
            'user-4': {'name': 'Diana', 'email': 'diana@example.com', 'type': 'person'},
        }

    @pytest.fixture
    def sample_pages(self):
        """Create sample pages for risk analysis"""
        now = datetime.now()
        pages = []
        
        # Alice creates many pages (concentration risk)
        for i in range(10):
            pages.append({
                'id': f'page-alice-{i}',
                'title': f'Page {i}' if i < 9 else 'Template Page',
                'created_time': (now - timedelta(days=100)).isoformat(),
                'created_by': 'user-1',
                'last_edited_time': (now - timedelta(days=50)).isoformat(),
                'last_edited_by': 'user-1',
                'archived': False
            })
        
        # Bob creates fewer pages
        for i in range(3):
            pages.append({
                'id': f'page-bob-{i}',
                'title': f'Bob Page {i}',
                'created_time': (now - timedelta(days=80)).isoformat(),
                'created_by': 'user-2',
                'last_edited_time': (now - timedelta(days=40)).isoformat(),
                'last_edited_by': 'user-2',
                'archived': False
            })
        
        # Charlie and Diana create 1 page each
        pages.append({
            'id': 'page-charlie',
            'title': 'Charlie Page',
            'created_time': (now - timedelta(days=60)).isoformat(),
            'created_by': 'user-3',
            'last_edited_time': (now - timedelta(days=30)).isoformat(),
            'last_edited_by': 'user-3',
            'archived': False
        })
        
        return pages

    @pytest.fixture
    def analytics(self, sample_pages, sample_users):
        """Create analytics instance"""
        return WorkspaceAnalytics(sample_pages, sample_users)

    def test_structure_analysis(self, analytics):
        """Test structure analysis"""
        structure = analytics._analyze_structure()

        assert 'template_count' in structure
        assert 'template_percentage' in structure
        assert 'non_template_count' in structure

        # Should have 1 template page
        assert structure['template_count'] == 1

    def test_risk_analysis(self, analytics):
        """Test risk assessment metrics"""
        risk = analytics._analyze_risk()

        assert 'concentration' in risk
        assert 'gini_coefficient' in risk
        assert 'bus_factor' in risk
        assert 'single_owner_pages_top_10' in risk

    def test_concentration_metrics(self, analytics):
        """Test concentration analysis"""
        risk = analytics._analyze_risk()
        concentration = risk['concentration']

        assert 'top_1_percent' in concentration
        assert 'top_5_percent' in concentration
        assert 'top_10_percent' in concentration

        # Each should have users, pages, percentage
        for key in concentration:
            assert 'users' in concentration[key]
            assert 'pages' in concentration[key]
            assert 'percentage' in concentration[key]

    def test_gini_coefficient(self, analytics):
        """Test Gini coefficient calculation"""
        risk = analytics._analyze_risk()

        # Gini should be between 0 and 1
        assert 0 <= risk['gini_coefficient'] <= 1
        # With unequal distribution, should be > 0
        assert risk['gini_coefficient'] > 0

    def test_bus_factor(self, analytics):
        """Test bus factor calculation"""
        risk = analytics._analyze_risk()

        # Bus factor should be at least 1
        assert risk['bus_factor'] >= 1
        # Alice owns most pages, so bus factor should be low
        assert risk['bus_factor'] <= 2

    def test_run_all(self, analytics):
        """Test run_all() orchestration method"""
        results = analytics.run_all()

        # Should have all categories
        expected_keys = [
            'summary', 'growth', 'users', 'top_creators',
            'collaboration', 'content_health', 'costs',
            'structure', 'risk'
        ]

        for key in expected_keys:
            assert key in results, f"Missing key: {key}"

        # Verify each category has data
        assert results['summary']['total_pages'] > 0
        assert 'annual_counts' in results['growth']
        assert 'segments' in results['users']
        assert len(results['top_creators']) > 0

    def test_run_all_returns_dict(self, analytics):
        """Test that run_all returns a dictionary"""
        results = analytics.run_all()
        assert isinstance(results, dict)

    def test_empty_analytics_run_all(self):
        """Test run_all with empty data"""
        analytics = WorkspaceAnalytics([], {})
        results = analytics.run_all()

        # Should still return all categories, just with zeros
        assert 'summary' in results
        assert results['summary']['total_pages'] == 0
