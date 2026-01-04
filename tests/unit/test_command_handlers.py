"""Unit tests for command handlers

Tests Command Pattern implementation for ActionExecutor.
Each test verifies that command handlers correctly delegate to bridge methods.
"""

import pytest
from unittest.mock import Mock, MagicMock
from athesa.core.action import ActionCommand
from athesa.engine.commands import (
    NavigateCommandHandler,
    ClickCommandHandler,
    TypeCommandHandler,
    ClearCommandHandler,
    UploadFileCommandHandler,
    WaitCommandHandler,
    ExecuteScriptCommandHandler,
    RefreshCommandHandler,
    SwitchWindowCommandHandler,
    CloseWindowCommandHandler,
    OpenNewTabCommandHandler,
    SwitchToFrameCommandHandler,
    SwitchToDefaultCommandHandler,
    CustomCommandHandler,
    create_command_registry,
)


class TestCommandHandlers:
    """Test individual command handlers"""
    
    def test_navigate_command_handler(self):
        """NavigateCommandHandler calls bridge.navigate"""
        bridge = Mock()
        handler = NavigateCommandHandler()
        
        handler.execute(bridge, {'url': 'https://example.com'})
        
        bridge.navigate.assert_called_once_with('https://example.com')
    
    def test_click_command_handler(self):
        """ClickCommandHandler calls bridge.click"""
        bridge = Mock()
        handler = ClickCommandHandler()
        
        selector = ('css', '#button')
        handler.execute(bridge, {'selector': selector})
        
        bridge.click.assert_called_once_with(selector)
    
    def test_type_command_handler(self):
        """TypeCommandHandler calls bridge.type_text"""
        bridge = Mock()
        handler = TypeCommandHandler()
        
        selector = ('css', 'input')
        handler.execute(bridge, {'selector': selector, 'text': 'test@example.com'})
        
        bridge.type_text.assert_called_once_with(selector, 'test@example.com')
    
    def test_clear_command_handler(self):
        """ClearCommandHandler types empty string"""
        bridge = Mock()
        handler = ClearCommandHandler()
        
        selector = ('css', 'input')
        handler.execute(bridge, {'selector': selector})
        
        bridge.type_text.assert_called_once_with(selector, '')
    
    def test_upload_file_command_handler(self):
        """UploadFileCommandHandler calls bridge.upload_file"""
        bridge = Mock()
        handler = UploadFileCommandHandler()
        
        selector = ('css', 'input[type="file"]')
        handler.execute(bridge, {'selector': selector, 'file_path': '/tmp/file.txt'})
        
        bridge.upload_file.assert_called_once_with(selector, '/tmp/file.txt')
    
    def test_wait_command_handler(self):
        """WaitCommandHandler sleeps for duration"""
        bridge = Mock()
        handler = WaitCommandHandler()
        
        import time
        original_sleep = time.sleep
        time.sleep = Mock()
        
        try:
            handler.execute(bridge, {'duration': 2})
            time.sleep.assert_called_once_with(2)
        finally:
            time.sleep = original_sleep
    
    def test_execute_script_command_handler(self):
        """ExecuteScriptCommandHandler calls bridge.execute_script"""
        bridge = Mock()
        handler = ExecuteScriptCommandHandler()
        
        handler.execute(bridge, {'script': 'return 1+1;', 'args': (1, 2)})
        
        bridge.execute_script.assert_called_once_with('return 1+1;', 1, 2)
    
    def test_execute_script_without_args(self):
        """ExecuteScriptCommandHandler works without args"""
        bridge = Mock()
        handler = ExecuteScriptCommandHandler()
        
        handler.execute(bridge, {'script': 'console.log("test");'})
        
        bridge.execute_script.assert_called_once_with('console.log("test");')
    
    def test_refresh_command_handler(self):
        """RefreshCommandHandler calls bridge.refresh_page"""
        bridge = Mock()
        handler = RefreshCommandHandler()
        
        handler.execute(bridge, {})
        
        bridge.refresh_page.assert_called_once()
    
    def test_switch_window_command_handler(self):
        """SwitchWindowCommandHandler calls bridge.switch_to_window"""
        bridge = Mock()
        handler = SwitchWindowCommandHandler()
        
        handler.execute(bridge, {'handle': 'window-123'})
        
        bridge.switch_to_window.assert_called_once_with('window-123')
    
    def test_close_window_command_handler(self):
        """CloseWindowCommandHandler calls bridge.close_current_window"""
        bridge = Mock()
        handler = CloseWindowCommandHandler()
        
        handler.execute(bridge, {})
        
        bridge.close_current_window.assert_called_once()
    
    def test_open_new_tab_command_handler(self):
        """OpenNewTabCommandHandler executes JS to open new tab"""
        bridge = Mock()
        handler = OpenNewTabCommandHandler()
        
        handler.execute(bridge, {})
        
        bridge.execute_script.assert_called_once_with("window.open('', '_blank');")
    
    def test_switch_to_frame_command_handler(self):
        """SwitchToFrameCommandHandler calls bridge.switch_to_frame"""
        bridge = Mock()
        handler = SwitchToFrameCommandHandler()
        
        handler.execute(bridge, {'frame': 'iframe-id'})
        
        bridge.switch_to_frame.assert_called_once_with('iframe-id')
    
    def test_switch_to_default_command_handler(self):
        """SwitchToDefaultCommandHandler calls bridge.switch_to_default_content"""
        bridge = Mock()
        handler = SwitchToDefaultCommandHandler()
        
        handler.execute(bridge, {})
        
        bridge.switch_to_default_content.assert_called_once()
    
    def test_custom_command_handler(self):
        """CustomCommandHandler calls custom callable"""
        bridge = Mock()
        handler = CustomCommandHandler()
        custom_fn = Mock()
        
        handler.execute(bridge, {'callable': custom_fn})
        
        custom_fn.assert_called_once_with(bridge)
    
    def test_custom_command_handler_raises_without_callable(self):
        """CustomCommandHandler raises ValueError without callable"""
        bridge = Mock()
        handler = CustomCommandHandler()
        
        with pytest.raises(ValueError, match="CUSTOM action requires 'callable'"):
            handler.execute(bridge, {})


class TestCommandRegistry:
    """Test command registry factory"""
    
    def test_create_command_registry_contains_all_commands(self):
        """Registry contains all ActionCommand enum values"""
        registry = create_command_registry()
        
        # Check all implemented commands are registered
        expected_commands = [
            ActionCommand.NAVIGATE,
            ActionCommand.REFRESH,
            ActionCommand.CLICK,
            ActionCommand.TYPE,
            ActionCommand.CLEAR,
            ActionCommand.UPLOAD_FILE,
            ActionCommand.WAIT,
            ActionCommand.WAIT_FOR_CONDITION,
            ActionCommand.EXECUTE_SCRIPT,
            ActionCommand.SWITCH_WINDOW,
            ActionCommand.CLOSE_WINDOW,
            ActionCommand.OPEN_NEW_TAB,
            ActionCommand.SWITCH_TO_FRAME,
            ActionCommand.SWITCH_TO_DEFAULT,
            ActionCommand.CUSTOM,
        ]
        
        for command in expected_commands:
            assert command in registry, f"{command} not in registry"
            assert registry[command] is not None
    
    def test_registry_handlers_are_instances(self):
        """Registry contains handler instances, not classes"""
        registry = create_command_registry()
        
        # Check that handlers have execute method
        for command, handler in registry.items():
            assert hasattr(handler, 'execute'), f"Handler for {command} has no execute method"
    
    def test_registry_handlers_work_with_bridge(self):
        """Registry handlers can execute with mock bridge"""
        bridge = Mock()
        registry = create_command_registry()
        
        # Test a few handlers
        registry[ActionCommand.NAVIGATE].execute(bridge, {'url': 'https://test.com'})
        bridge.navigate.assert_called_with('https://test.com')
        
        registry[ActionCommand.CLICK].execute(bridge, {'selector': ('id', 'btn')})
        bridge.click.assert_called_with(('id', 'btn'))
