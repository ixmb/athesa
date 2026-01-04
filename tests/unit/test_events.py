"""
Real-world unit tests for EventEmitter

Tests realistic scenarios that you'd encounter in actual process automation.
"""

import pytest
from athesa.events import EventEmitter


class TestEventEmitterRealWorld:
    """Real-world event emitter usage scenarios"""
    
    def test_process_lifecycle_tracking(self):
        """
        Scenario: Track complete process lifecycle for logging/analytics
        
        Real use case: Monitor automation runs, log to database, send notifications
        """
        emitter = EventEmitter()
        
        # Tracking state
        lifecycle = []
        
        # Register lifecycle handlers
        emitter.add_listener('process:started', lambda name: lifecycle.append(('started', name)))
        emitter.add_listener('state_changed', lambda old, new: lifecycle.append(('state', new.__class__.__name__)))
        emitter.add_listener('screen_detected', lambda screen: lifecycle.append(('screen', screen)))
        emitter.add_listener('process:completed', lambda outcome: lifecycle.append(('completed', outcome)))
        
        # Simulate process execution
        emitter.emit('process:started', 'google_login')
        
        class InitialState: pass
        class UsernameState: pass
        class SuccessState: pass
        
        emitter.emit('state_changed', InitialState(), UsernameState())
        emitter.emit('screen_detected', 'USERNAME_SCREEN')
        emitter.emit('state_changed', UsernameState(), SuccessState())
        emitter.emit('process:completed', 'success')
        
        # Verify complete lifecycle was tracked
        assert len(lifecycle) == 5
        assert lifecycle[0] == ('started', 'google_login')
        assert lifecycle[1] == ('state', 'UsernameState')
        assert lifecycle[2] == ('screen', 'USERNAME_SCREEN')
        assert lifecycle[3] == ('state', 'SuccessState')
        assert lifecycle[4] == ('completed', 'success')
    
    def test_error_notification_system(self):
        """
        Scenario: Send alerts when automation fails
        
        Real use case: Slack/email notifications, error logging, retry logic
        """
        emitter = EventEmitter()
        
        alerts = []
        
        def send_alert(action, error):
            """Simulates sending Slack/email alert"""
            alerts.append({
                'action': action.command.name if hasattr(action, 'command') else str(action),
                'error': str(error),
                'severity': 'high'
            })
        
        emitter.add_listener('action_failed', send_alert)
        
        # Simulate action failure
        from athesa.core.action import Action, ActionCommand
        failed_action = Action(ActionCommand.CLICK, {'selector': ('id', 'missing-button')})
        error = Exception("Element not found: missing-button")
        
        emitter.emit('action_failed', failed_action, error)
        
        assert len(alerts) == 1
        assert alerts[0]['action'] == 'CLICK'
        assert 'missing-button' in alerts[0]['error']
        assert alerts[0]['severity'] == 'high'
    
    def test_multiple_observers_pattern(self):
        """
        Scenario: Multiple systems listen to same events
        
        Real use case: Logging + metrics + notifications all triggered by same event
        """
        emitter = EventEmitter()
        
        # Three different systems observing
        log_entries = []
        metrics = {'actions_executed': 0}
        notifications = []
        
        # Logger
        emitter.add_listener('action_executed', lambda action: log_entries.append(f"Executed: {action.message}"))
        
        # Metrics collector
        emitter.add_listener('action_executed', lambda action: metrics.update({'actions_executed': metrics['actions_executed'] + 1}))
        
        # Notification system (only for important actions)
        def maybe_notify(action):
            if action.message and 'password' in action.message.lower():
                notifications.append(f"Sensitive action: {action.message}")
        
        emitter.add_listener('action_executed', maybe_notify)
        
        # Execute actions
        from athesa.core.action import Action, ActionCommand
        
        action1 = Action(ActionCommand.CLICK, {}, message="Clicking login button")
        action2 = Action(ActionCommand.TYPE, {}, message="Entering password")
        action3 = Action(ActionCommand.NAVIGATE, {}, message="Going to dashboard")
        
        emitter.emit('action_executed', action1)
        emitter.emit('action_executed', action2)
        emitter.emit('action_executed', action3)
        
        # Verify all systems received events
        assert len(log_entries) == 3
        assert metrics['actions_executed'] == 3
        assert len(notifications) == 1  # Only password action
        assert 'password' in notifications[0].lower()
    
    def test_performance_monitoring(self):
        """
        Scenario: Track performance metrics during automation
        
        Real use case: Monitor slow screens, timeout patterns, bottleneck detection
        """
        import time
        emitter = EventEmitter()
        
        timings = {}
        current_screen = None
        start_time = None
        
        def screen_detected_handler(screen):
            nonlocal current_screen, start_time
            current_screen = screen
            start_time = time.time()
        
        def action_executed_handler(action):
            if current_screen and start_time:
                elapsed = time.time() - start_time
                if current_screen not in timings:
                    timings[current_screen] = []
                timings[current_screen].append(elapsed)
        
        emitter.add_listener('screen_detected', screen_detected_handler)
        emitter.add_listener('action_executed', action_executed_handler)
        
        # Simulate detection and actions
        from athesa.core.action import Action, ActionCommand
        
        emitter.emit('screen_detected', 'USERNAME_SCREEN')
        time.sleep(0.1)  # Simulate action time
        emitter.emit('action_executed', Action(ActionCommand.TYPE, {}))
        
        emitter.emit('screen_detected', 'PASSWORD_SCREEN')
        time.sleep(0.2)  # Simulate slower action
        emitter.emit('action_executed', Action(ActionCommand.TYPE, {}))
        
        # Verify all events were captured
        assert 'USERNAME_SCREEN' in timings
        assert 'PASSWORD_SCREEN' in timings
        
        # Verify timing values exist and are reasonable
        assert len(timings['USERNAME_SCREEN']) == 1
        assert len(timings['PASSWORD_SCREEN']) == 1
        
        # All timestamps should be positive and within reasonable range
        for screen_name, event_timings in timings.items():
            for t in event_timings:
                assert t > 0, f"{screen_name} timing should be positive"
                assert t < 1.0, f"{screen_name} timing should be < 1s (was {t}s)"
    
    def test_cleanup_on_process_failure(self):
        """
        Scenario: Clean up resources when process fails
        
        Real use case: Close browsers, release locks, rollback transactions
        """
        emitter = EventEmitter()
        
        cleanup_called = {'browser_closed': False, 'lock_released': False}
        
        def cleanup_handler(error):
            cleanup_called['browser_closed'] = True
            cleanup_called['lock_released'] = True
            # In real scenario: driver.quit(), release_lock(), etc.
        
        emitter.add_listener('process:failed', cleanup_handler)
        
        # Simulate failure
        emitter.emit('process:failed', Exception("Timeout"))
        
        assert cleanup_called['browser_closed']
        assert cleanup_called['lock_released']
    
    def test_event_listener_removal(self):
        """
        Scenario: Temporary listeners for specific operations
        
        Real use case: One-time setup, conditional monitoring
        """
        emitter = EventEmitter()
        
        setup_count = 0
        
        def one_time_setup(name):
            nonlocal setup_count
            setup_count += 1
            # Do setup once
        
        emitter.add_listener_once('process:started', one_time_setup)
        
        # Fire event multiple times
        emitter.emit('process:started', 'process1')
        emitter.emit('process:started', 'process2')
        emitter.emit('process:started', 'process3')
        
        # Setup only called once
        assert setup_count == 1
