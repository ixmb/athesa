"""Unit tests for detection strategies

Tests Strategy Pattern implementation for PageDetector.
Each test verifies that strategy correctly delegates to bridge methods.
"""

import pytest
from unittest.mock import Mock
from athesa.core.screen import DetectionStrategy
from athesa.engine.strategies import (
    VisibleAndEnabledStrategy,
    PresenceOnlyStrategy,
    CustomStrategy,
    create_detection_strategy_registry,
)


class TestDetectionStrategies:
    """Test individual detection strategies"""
    
    def test_visible_and_enabled_strategy(self):
        """VisibleAndEnabledStrategy calls bridge.is_visible"""
        bridge = Mock()
        bridge.is_visible.return_value = True
        strategy = VisibleAndEnabledStrategy()
        
        selector = ('css', '#login-button')
        result = strategy.is_present(bridge, selector)
        
        bridge.is_visible.assert_called_once_with(selector)
        assert result is True
    
    def test_visible_and_enabled_strategy_returns_false(self):
        """VisibleAndEnabledStrategy returns False when element not visible"""
        bridge = Mock()
        bridge.is_visible.return_value = False
        strategy = VisibleAndEnabledStrategy()
        
        result = strategy.is_present(bridge, ('css', '#hidden'))
        
        assert result is False
    
    def test_presence_only_strategy(self):
        """PresenceOnlyStrategy calls bridge.is_existing"""
        bridge = Mock()
        bridge.is_existing.return_value = True
        strategy = PresenceOnlyStrategy()
        
        selector = ('xpath', '//div[@id="content"]')
        result = strategy.is_present(bridge, selector)
        
        bridge.is_existing.assert_called_once_with(selector)
        assert result is True
    
    def test_presence_only_strategy_returns_false(self):
        """PresenceOnlyStrategy returns False when element doesn't exist"""
        bridge = Mock()
        bridge.is_existing.return_value = False
        strategy = PresenceOnlyStrategy()
        
        result = strategy.is_present(bridge, ('css', '#nonexistent'))
        
        assert result is False
    
    def test_custom_strategy_always_returns_true(self):
        """CustomStrategy always returns True (relies on verification criteria)"""
        bridge = Mock()
        strategy = CustomStrategy()
        
        # Should return True regardless of bridge state
        result = strategy.is_present(bridge, ('css', 'any-selector'))
        
        assert result is True
        # Bridge methods should NOT be called
        bridge.is_visible.assert_not_called()
        bridge.is_existing.assert_not_called()
    
    def test_custom_strategy_ignores_selector(self):
        """CustomStrategy doesn't use selector or bridge"""
        bridge = Mock()
        strategy = CustomStrategy()
        
        # Different selectors, same result
        assert strategy.is_present(bridge, ('css', '#foo')) is True
        assert strategy.is_present(bridge, ('xpath', '//bar')) is True
        assert strategy.is_present(bridge, ('id', 'baz')) is True


class TestDetectionStrategyRegistry:
    """Test detection strategy registry factory"""
    
    def test_create_registry_contains_all_strategies(self):
        """Registry contains all DetectionStrategy enum values"""
        registry = create_detection_strategy_registry()
        
        expected_strategies = [
            DetectionStrategy.VISIBLE_AND_ENABLED,
            DetectionStrategy.PRESENCE_ONLY,
            DetectionStrategy.CUSTOM,
        ]
        
        for strategy_type in expected_strategies:
            assert strategy_type in registry, f"{strategy_type} not in registry"
            assert registry[strategy_type] is not None
    
    def test_registry_strategies_are_instances(self):
        """Registry contains strategy instances, not classes"""
        registry = create_detection_strategy_registry()
        
        for strategy_type, strategy in registry.items():
            assert hasattr(strategy, 'is_present'), \
                f"Strategy for {strategy_type} has no is_present method"
    
    def test_registry_strategies_work_with_bridge(self):
        """Registry strategies can execute with mock bridge"""
        bridge = Mock()
        bridge.is_visible.return_value = True
        bridge.is_existing.return_value = True
        
        registry = create_detection_strategy_registry()
        
        # Test each strategy
        selector = ('css', '#test')
        
        result = registry[DetectionStrategy.VISIBLE_AND_ENABLED].is_present(bridge, selector)
        assert result is True
        bridge.is_visible.assert_called_with(selector)
        
        result = registry[DetectionStrategy.PRESENCE_ONLY].is_present(bridge, selector)
        assert result is True
        bridge.is_existing.assert_called_with(selector)
        
        result = registry[DetectionStrategy.CUSTOM].is_present(bridge, selector)
        assert result is True
    
    def test_registry_uses_correct_strategy_for_each_type(self):
        """Each DetectionStrategy maps to correct strategy implementation"""
        registry = create_detection_strategy_registry()
        
        assert isinstance(
            registry[DetectionStrategy.VISIBLE_AND_ENABLED],
            VisibleAndEnabledStrategy
        )
        assert isinstance(
            registry[DetectionStrategy.PRESENCE_ONLY],
            PresenceOnlyStrategy
        )
        assert isinstance(
            registry[DetectionStrategy.CUSTOM],
            CustomStrategy
        )


class TestStrategyBehaviorDifferences:
    """Test that different strategies behave differently"""
    
    def test_strategies_call_different_bridge_methods(self):
        """Each strategy uses its own bridge method"""
        bridge = Mock()
        bridge.is_visible.return_value = True
        bridge.is_existing.return_value = True
        
        selector = ('css', '#element')
        
        # VisibleAndEnabled uses is_visible
        VisibleAndEnabledStrategy().is_present(bridge, selector)
        assert bridge.is_visible.call_count == 1
        assert bridge.is_existing.call_count == 0
        
        bridge.reset_mock()
        
        # PresenceOnly uses is_existing
        PresenceOnlyStrategy().is_present(bridge, selector)
        assert bridge.is_visible.call_count == 0
        assert bridge.is_existing.call_count == 1
        
        bridge.reset_mock()
        
        # Custom uses neither
        CustomStrategy().is_present(bridge, selector)
        assert bridge.is_visible.call_count == 0
        assert bridge.is_existing.call_count == 0
