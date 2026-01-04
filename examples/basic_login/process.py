"""
Basic Login Process Example

Demonstrates a simple login flow with username/password screens.
This is a complete, working example of an Athesa process.
"""

from enum import Enum, auto
from selenium.webdriver.common.by import By

from athesa import (
    ProcessProtocol,
    StateProtocol,
    HandlerProtocol,
    ScreenDefinition,
    DetectionStrategy,
    Action,
    ActionSequence,
    ActionCommand,
    ProcessContext,
)


# ========== Screen Types ==========

class LoginScreens(Enum):
    """All possible screens in the login process"""
    USERNAME_SCREEN = auto()
    PASSWORD_SCREEN = auto()
    ERROR_SCREEN = auto()
    SUCCESS_SCREEN = auto()


# ========== States ==========

class LoginInitialState:
    """Initial state - navigates to login page"""
    
    def handle(self, context: ProcessContext) -> None:
        # Default handling - let ProcessRunner detect screen
        pass
    
    def get_expected_screens(self):
        return [LoginScreens.USERNAME_SCREEN, LoginScreens.ERROR_SCREEN]
    
    def on_detection_failed(self, context: ProcessContext) -> None:
        context.transition_to(LoginFailedState())


class UsernameEnteredState:
    """After username is entered"""
    
    def handle(self, context: ProcessContext) -> None:
        pass
    
    def get_expected_screens(self):
        return [LoginScreens.PASSWORD_SCREEN, LoginScreens.ERROR_SCREEN]
    
    def on_detection_failed(self, context: ProcessContext) -> None:
        context.transition_to(LoginFailedState())


class PasswordEnteredState:
    """After password is entered"""
    
    def handle(self, context: ProcessContext) -> None:
        pass
    
    def get_expected_screens(self):
        return [LoginScreens.SUCCESS_SCREEN, LoginScreens.ERROR_SCREEN]
    
    def on_detection_failed(self, context: ProcessContext) -> None:
        context.transition_to(LoginFailedState())


class LoginSuccessState:
    """Login succeeded - terminal state"""
    pass


class LoginFailedState:
    """Login failed - terminal state"""
    pass


# ========== Handlers ==========

class UsernameScreenHandler:
    """Handles username input screen"""
    
    def create_action_sequence(self, context: ProcessContext) -> ActionSequence:
        username = context.credentials.get('username', '')
        
        return ActionSequence(
            actions=[
                Action(
                    command=ActionCommand.TYPE,
                    params={
                        'selector': (By.CSS_SELECTOR, 'input[type="email"]'),
                        'text': username
                    },
                    message=f"Entering username: {username}"
                ),
                Action(
                    command=ActionCommand.CLICK,
                    params={
                        'selector': (By.ID, 'next-button')
                    },
                    message="Clicking Next"
                ),
            ],
            next_state=UsernameEnteredState
        )


class PasswordScreenHandler:
    """Handles password input screen"""
    
    def create_action_sequence(self, context: ProcessContext) -> ActionSequence:
        password = context.credentials.get('password', '')
        
        return ActionSequence(
            actions=[
                Action(
                    command=ActionCommand.TYPE,
                    params={
                        'selector': (By.CSS_SELECTOR, 'input[type="password"]'),
                        'text': password
                    },
                    message="Entering password"
                ),
                Action(
                    command=ActionCommand.CLICK,
                    params={
                        'selector': (By.ID, 'login-button')
                    },
                    message="Clicking Login"
                ),
            ],
            next_state=PasswordEnteredState
        )


class ErrorScreenHandler:
    """Handles error screens"""
    
    def create_action_sequence(self, context: ProcessContext) -> ActionSequence:
        return ActionSequence(
            actions=[],
            next_state=LoginFailedState
        )


class SuccessScreenHandler:
    """Handles successful login"""
    
    def create_action_sequence(self, context: ProcessContext) -> ActionSequence:
        return ActionSequence(
            actions=[],
            next_state=LoginSuccessState
        )


# ========== Process Definition ==========

class BasicLoginProcess:
    """
    Basic login process with username/password flow.
    
    Example usage:
        from selenium import webdriver
        from athesa import ProcessRunner, ProcessContext
        from athesa.adapters.selenium import SeleniumBridge
        
        driver = webdriver.Chrome()
        bridge = SeleniumBridge(driver)
        
        process = BasicLoginProcess()
        context = ProcessContext(
            credentials={'username': 'user@example.com', 'password': 'secret'}
        )
        
        runner = ProcessRunner(process, context, bridge)
        outcome = runner.run()
        
        print(f"Login {outcome}")
        driver.quit()
    """
    
    @property
    def name(self) -> str:
        return "basic_login"
    
    @property
    def initial_state(self):
        return LoginInitialState
    
    @property
    def registry(self):
        return {
            LoginScreens.USERNAME_SCREEN: UsernameScreenHandler(),
            LoginScreens.PASSWORD_SCREEN: PasswordScreenHandler(),
            LoginScreens.ERROR_SCREEN: ErrorScreenHandler(),
            LoginScreens.SUCCESS_SCREEN: SuccessScreenHandler(),
        }
    
    @property
    def screens(self):
        return [
            ScreenDefinition(
                type=LoginScreens.USERNAME_SCREEN,
                selector=(By.CSS_SELECTOR, 'input[type="email"]'),
                selector_name="Email Input",
                detection_strategy=DetectionStrategy.VISIBLE_AND_ENABLED
            ),
            ScreenDefinition(
                type=LoginScreens.PASSWORD_SCREEN,
                selector=(By.CSS_SELECTOR, 'input[type="password"]'),
                selector_name="Password Input",
                detection_strategy=DetectionStrategy.VISIBLE_AND_ENABLED
            ),
            ScreenDefinition(
                type=LoginScreens.ERROR_SCREEN,
                selector=(By.CSS_SELECTOR, '.error-message'),
                selector_name="Error Message",
                detection_strategy=DetectionStrategy.VISIBLE_AND_ENABLED
            ),
            ScreenDefinition(
                type=LoginScreens.SUCCESS_SCREEN,
                selector=(By.ID, 'user-profile'),
                selector_name="User Profile",
                detection_strategy=DetectionStrategy.VISIBLE_AND_ENABLED
            ),
        ]
    
    @property
    def final_states(self):
        return (LoginSuccessState, LoginFailedState)
    
    @property
    def global_interrupts(self):
        return []
    
    def get_workflow(self):
        # Optional: Initial navigation action
        return None
