# Athesa API Documentation

Complete API reference for the Athesa web automation framework.

---

## Table of Contents

- [Core Protocols](#core-protocols)
  - [ProcessProtocol](#processprotocol)
  - [StateProtocol](#stateprotocol)
  - [HandlerProtocol](#handlerprotocol)
  - [BridgeProtocol](#bridgeprotocol)
- [Core Types](#core-types)
  - [ScreenDefinition](#screendefinition)
  - [Action & ActionSequence](#action--actionsequence)
  - [ProcessContext](#processcontext)
- [Engine](#engine)
  - [ProcessRunner](#processrunner)
  - [StateMachine](#statemachine)
  - [PageDetector](#pagedetector)
  - [ActionExecutor](#actionexecutor)
- [Events](#events)
  - [EventEmitter](#eventemitter)
  - [ProcessCallbacks](#processcallbacks)
- [Factory](#factory)
  - [ProcessRegistry](#processregistry)
- [Adapters](#adapters)
  - [SeleniumBridge](#seleniumbridge)

---

## Core Protocols

### ProcessProtocol

Defines the structure of an automation process.

```python
from athesa.core.process import ProcessProtocol

class MyProcess:
    @property
    def name(self) -> str:
        """Unique process identifier"""
        return "my_process"
    
    @property
    def initial_state(self) -> Type[StateProtocol]:
        """Starting state class"""
        return InitialState
    
    @property
    def registry(self) -> Dict[type, HandlerProtocol]:
        """Screen type → Handler mapping"""
        return {
            MyScreens.LOGIN: LoginHandler(),
            MyScreens.ERROR: ErrorHandler(),
        }
    
    @property
    def screens(self) -> List[ScreenDefinition]:
        """All screen definitions"""
        return [
            ScreenDefinition(
                type=MyScreens.LOGIN,
                selector=(By.ID, "login-form")
            ),
            # ... more screens
        ]
    
    @property
    def final_states(self) -> Tuple[Type[StateProtocol], ...]:
        """Terminal states"""
        return (SuccessState, FailureState)
    
    @property
    def global_interrupts(self) -> List[type]:
        """Screens that can appear at any time (optional)"""
        return [MyScreens.COOKIE_CONSENT]
    
    def get_workflow(self):
        """Optional workflow generator (optional)"""
        return None
```

**Properties:**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | `str` | ✓ | Unique process identifier |
| `initial_state` | `Type[StateProtocol]` | ✓ | Starting state class |
| `registry` | `Dict[type, HandlerProtocol]` | ✓ | Screen → Handler mapping |
| `screens` | `List[ScreenDefinition]` | ✓ | All screen definitions |
| `final_states` | `Tuple[Type[StateProtocol], ...]` | ✓ | Terminal states |
| `global_interrupts` | `List[type]` | ✗ | Global interrupt screens |
| `get_workflow()` | `Generator[Action, None, None]` | ✗ | Initial workflow actions |

---

### StateProtocol

Defines a step in the workflow.

```python
from athesa.core.state import StateProtocol

class MyState:
    def handle(self, context: ProcessContext) -> None:
        """Execute state logic"""
        pass  # Default: let ProcessRunner handle
    
    def get_expected_screens(self) -> List[type]:
        """Screens this state expects"""
        return [MyScreens.SCREEN1, MyScreens.SCREEN2]
    
    def on_detection_failed(self, context: ProcessContext) -> None:
        """Called when screen detection times out"""
        context.transition_to(FailureState())
```

**Methods:**

- **`handle(context: ProcessContext) -> None`**
  - Called when entering this state
  - Usually left empty to let ProcessRunner handle detection
  - Can contain custom logic if needed

- **`get_expected_screens() -> List[type]`** (Required)
  - Returns list of screen types to wait for
  - Order matters: first match wins
  
- **`on_detection_failed(context: ProcessContext) -> None`** (Required)
  - Called when no expected screen is detected within timeout
  - Should transition to failure state or retry

---

### HandlerProtocol

Defines actions for a detected screen.

```python
from athesa.core.handler import HandlerProtocol

class MyHandler:
    def create_action_sequence(self, context: ProcessContext) -> ActionSequence:
        """Generate actions for this screen"""
        return ActionSequence(
            actions=[
                Action(ActionCommand.CLICK, {'selector': (By.ID, 'btn')}),
                Action(ActionCommand.TYPE, {'selector': (By.CSS, 'input'), 'text': 'hello'}),
            ],
            next_state=NextState
        )
```

**Methods:**

- **`create_action_sequence(context: ProcessContext) -> ActionSequence`** (Required)
  - Returns actions to execute and next state
  - Has access to `context.credentials`, `context.data`, etc.

---

### BridgeProtocol

Browser automation interface.

```python
from athesa.core.bridge import BridgeProtocol

# Implement all methods for custom adapter
class MyBridge:
    def click(self, selector: Tuple[str, str]) -> None: ...
    def type_text(self, selector: Tuple[str, str], text: str) -> None: ...
    def navigate(self, url: str) -> None: ...
    def is_visible(self, selector: Tuple[str, str]) -> bool: ...
    def is_existing(self, selector: Tuple[str, str]) -> bool: ...
    # ... 15+ more methods
```

**Key Methods:**

| Method | Description |
|--------|-------------|
| `click(selector)` | Click element |
| `type_text(selector, text)` | Type text into input |
| `navigate(url)` | Navigate to URL |
| `is_visible(selector)` | Check if element is visible |
| `is_existing(selector)` | Check if element exists in DOM |
| `execute_script(script, *args)` | Run JavaScript |
| `wait_for_condition(condition, timeout)` | Wait for custom condition |
| `upload_file(selector, path)` | Upload file |

See [SeleniumBridge](#seleniumbridge) for complete implementation example.

---

## Core Types

### ScreenDefinition

Defines how to identify a screen.

```python
from athesa.core.screen import ScreenDefinition, DetectionStrategy
from selenium.webdriver.common.by import By

screen = ScreenDefinition(
    type=MyScreens.LOGIN,                       # Enum value
    selector=(By.CSS_SELECTOR, '#login-form'),  # (by, value)
    selector_name="Login Form",                 # Human-readable name
    detection_strategy=DetectionStrategy.VISIBLE_AND_ENABLED,
    verification_criteria=[
        lambda driver: driver.find_element(By.ID, 'submit').is_enabled()
    ],
    metadata={'priority': 'high'}
)
```

**Attributes:**

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | `Any` (usually Enum) | ✓ | Unique screen identifier |
| `selector` | `Tuple[str, str]` | ✓ | (by, value) for detection |
| `selector_name` | `str` | ✗ | Human-readable name |
| `detection_strategy` | `DetectionStrategy` | ✗ | How to verify presence |
| `verification_criteria` | `List[Callable]` | ✗ | Additional lambda checks |
| `metadata` | `dict` | ✗ | Custom metadata |

**DetectionStrategy:**

```python
class DetectionStrategy(Enum):
    VISIBLE_AND_ENABLED = auto()  # Element visible and interactable
    PRESENCE_ONLY = auto()        # Element exists in DOM
    CUSTOM = auto()               # Use verification_criteria only
```

---

### Action & ActionSequence

Browser actions.

```python
from athesa.core.action import Action, ActionSequence, ActionCommand

# Single action
action = Action(
    command=ActionCommand.CLICK,
    params={'selector': (By.ID, 'submit')},
    message="Clicking submit button"  # Optional user-facing message
)

# Action sequence
sequence = ActionSequence(
    actions=[
        Action(ActionCommand.TYPE, {'selector': (...), 'text': 'hello'}),
        Action(ActionCommand.CLICK, {'selector': (...)}),
    ],
    next_state=NextState,                    # Optional
    on_success=lambda: print("Success!"),    # Optional
    on_failure=lambda e: print(f"Failed: {e}")  # Optional
)
```

**ActionCommand:**

```python
class ActionCommand(Enum):
    # Navigation
    NAVIGATE = auto()
    REFRESH = auto()
    
    # Interactions
    CLICK = auto()
    TYPE = auto()
    CLEAR = auto()
    SELECT = auto()
    UPLOAD_FILE = auto()
    
    # Waits
    WAIT = auto()
    WAIT_FOR_CONDITION = auto()
    
    # JavaScript
    EXECUTE_SCRIPT = auto()
    
    # Window/Tab
    SWITCH_WINDOW = auto()
    CLOSE_WINDOW = auto()
    OPEN_NEW_TAB = auto()
    
    # Frames
    SWITCH_TO_FRAME = auto()
    SWITCH_TO_DEFAULT = auto()
    
    # Custom
    CUSTOM = auto()
```

---

### ProcessContext

Execution context for a process.

```python
from athesa import ProcessContext

context = ProcessContext(
    credentials={'username': 'test@example.com', 'password': 'secret'},
    data={'video_path': '/path/to/video.mp4'},
    custom_key='custom_value'
)

# Access data
username = context.credentials['username']
video = context.data['video_path']
custom = context.get('custom_key')

# Temporary storage
context.temp['session_id'] = '12345'

# Manual state transition
context.transition_to(NextState())
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `credentials` | `dict` | Login credentials |
| `data` | `dict` | Input data for process |
| `temp` | `dict` | Temporary storage during execution |
| `metadata` | `dict` | Additional context data |

**Methods:**

- `get(key, default=None)`: Get value from data or metadata
- `set(key, value)`: Set value in temp storage
- `transition_to(new_state)`: Manually transition to new state

---

## Engine

### ProcessRunner

Executes a process from start to finish.

```python
from athesa import ProcessRunner, ProcessContext
from athesa.adapters.selenium import SeleniumBridge

runner = ProcessRunner(
    process=my_process,
    context=context,
    bridge=bridge,
    event_emitter=emitter  # Optional
)

outcome = runner.run()  # Returns 'success', 'failure', or 'retry'
```

**Methods:**

- **`run() -> str`**
  - Executes the process
  - Returns outcome: `'success'`, `'failure'`, or `'retry'`
  - Raises `AutomationStoppedException` if user stops

**Handles:**
- State transitions
- Screen detection
- Action execution
- Recovery on failures
- Event emission

---

### StateMachine

Manages state transitions.

```python
from athesa.engine import StateMachine

sm = StateMachine(
    initial_state=InitialState,
    process_name="my_process",
    event_emitter=emitter  # Optional
)

# Get current state
current = sm.current_state

# Transition
sm.transition_to(NextState())

# Reset
sm.reset(InitialState)
```

---

### PageDetector

Detects which screen is displayed.

```python
from athesa.engine import PageDetector

detector = PageDetector(
    bridge=bridge,
    process_screens=screen_definitions,
    global_interrupts=[],  # Optional
    event_emitter=emitter  # Optional
)

# Wait for screen
detected = detector.wait_for_screen(
    expected_types=[Screen1, Screen2],
    timeout=60
)

# Immediate check
detected = detector.detect_immediate([Screen1, Screen2])
```

---

### ActionExecutor

Executes actions via bridge.

```python
from athesa.engine import ActionExecutor

executor = ActionExecutor(
    bridge=bridge,
    event_emitter=emitter  # Optional
)

# Execute single action
executor.execute(action)

# Execute sequence
executor.execute_sequence([action1, action2, action3])
```

---

## Events

### EventEmitter

Pure Python event system.

```python
from athesa.events import EventEmitter

emitter = EventEmitter()

# Register listener
def on_state_change(old_state, new_state):
    print(f"{old_state} → {new_state}")

emitter.add_listener('state_changed', on_state_change)

# One-time listener
emitter.add_listener_once('process:started', lambda name: print(f"Started: {name}"))

# Emit event
emitter.emit('state_changed', OldState(), NewState())

# Remove listener
emitter.remove_listener('state_changed', on_state_change)

# Remove all listeners for event
emitter.remove_listener('state_changed')
```

**Methods:**

| Method | Description |
|--------|-------------|
| `on(event, callback)` | Register listener |
| `once(event, callback)` | One-time listener |
| `emit(event, *args, **kwargs)` | Emit event |
| `off(event, callback=None)` | Remove listener(s) |
| `listeners(event)` | Get listeners for event |
| `event_names()` | Get all event names |
| `listener_count(event)` | Count listeners |

**Standard Events:**

```python
from athesa.events.callbacks import ProcessEvents

ProcessEvents.STATE_CHANGED          # 'state_changed'
ProcessEvents.SCREEN_DETECTED        # 'screen_detected'
ProcessEvents.DETECTION_TIMEOUT      # 'detection_timeout'
ProcessEvents.ACTION_EXECUTING       # 'action_executing'
ProcessEvents.ACTION_EXECUTED        # 'action_executed'
ProcessEvents.ACTION_FAILED          # 'action_failed'
ProcessEvents.PROCESS_STARTED        # 'process:started'
ProcessEvents.PROCESS_COMPLETED      # 'process:completed'
ProcessEvents.PROCESS_FAILED         # 'process:failed'
```

---

### ProcessCallbacks

Standard callback protocol.

```python
from athesa.events.callbacks import ProcessCallbacks

class MyListener:
    def on_state_changed(self, old_state, new_state): ...
    def on_screen_detected(self, screen_type): ...
    def on_action_executed(self, action): ...
    def on_process_completed(self, outcome): ...
    def on_process_failed(self, error): ...
    # ... more callbacks

# Wire up
listener = MyListener()
emitter.add_listener('state_changed', listener.on_state_changed)
emitter.add_listener('screen_detected', listener.on_screen_detected)
# ... etc
```

---

## Factory

### ProcessRegistry

Central registry for process types.

```python
from athesa.factory import registry

# Register
registry.register('google_login', GoogleLoginProcess)

# Get class
ProcessClass = registry.get('google_login')

# Create instance
process = registry.create('google_login', config=my_config)

# List all
print(registry.list())  # ['google_login', ...]

# Check existence
if 'google_login' in registry:
    print("Available!")

# Unregister
registry.unregister('old_process')
```

**Methods:**

| Method | Description |
|--------|-------------|
| `register(name, process_class, force=False)` | Register process |
| `unregister(name)` | Remove process |
| `get(name)` | Get process class |
| `create(name, **kwargs)` | Create instance |
| `list()` | List all names |
| `exists(name)` | Check if registered |
| `clear()` | Remove all |

---

## Adapters

### SeleniumBridge

Selenium implementation of BridgeProtocol.

```python
from selenium import webdriver
from athesa.adapters.selenium import SeleniumBridge

driver = webdriver.Chrome()
bridge = SeleniumBridge(
    driver=driver,
    wait=None,  # Optional WebDriverWait
    default_timeout=10
)

# Use with ProcessRunner
runner = ProcessRunner(process, context, bridge)
```

**All BridgeProtocol methods implemented.**

---

## Complete Example

```python
from enum import Enum, auto
from selenium import webdriver
from selenium.webdriver.common.by import By

from athesa import (
    ProcessRunner,
    ProcessContext,
    ScreenDefinition,
    DetectionStrategy,
    Action,
    ActionSequence,
    ActionCommand,
)
from athesa.adapters.selenium import SeleniumBridge
from athesa.events import EventEmitter


# 1. Define screens
class LoginScreens(Enum):
    USERNAME = auto()
    PASSWORD = auto()
    SUCCESS = auto()


# 2. Define states
class InitialState:
    def handle(self, context): pass
    def get_expected_screens(self): return [LoginScreens.USERNAME]
    def on_detection_failed(self, context): context.transition_to(FailedState())

class UsernameEnteredState:
    def handle(self, context): pass
    def get_expected_screens(self): return [LoginScreens.PASSWORD]
    def on_detection_failed(self, context): context.transition_to(FailedState())

class SuccessState: pass
class FailedState: pass


# 3. Define handlers
class UsernameHandler:
    def create_action_sequence(self, context):
        return ActionSequence(
            actions=[
                Action(ActionCommand.TYPE, {
                    'selector': (By.ID, 'email'),
                    'text': context.credentials['username']
                }),
                Action(ActionCommand.CLICK, {'selector': (By.ID, 'next')}),
            ],
            next_state=UsernameEnteredState
        )

class PasswordHandler:
    def create_action_sequence(self, context):
        return ActionSequence(
            actions=[
                Action(ActionCommand.TYPE, {
                    'selector': (By.ID, 'password'),
                    'text': context.credentials['password']
                }),
                Action(ActionCommand.CLICK, {'selector': (By.ID, 'login')}),
            ],
            next_state=SuccessState
        )


# 4. Define process
class LoginProcess:
    @property
    def name(self): return "login"
    
    @property
    def initial_state(self): return InitialState
    
    @property
    def registry(self):
        return {
            LoginScreens.USERNAME: UsernameHandler(),
            LoginScreens.PASSWORD: PasswordHandler(),
        }
    
    @property
    def screens(self):
        return [
            ScreenDefinition(
                type=LoginScreens.USERNAME,
                selector=(By.ID, 'email'),
                detection_strategy=DetectionStrategy.VISIBLE_AND_ENABLED
            ),
            ScreenDefinition(
                type=LoginScreens.PASSWORD,
                selector=(By.ID, 'password'),
                detection_strategy=DetectionStrategy.VISIBLE_AND_ENABLED
            ),
        ]
    
    @property
    def final_states(self): return (SuccessState, FailedState)


# 5. Run!
driver = webdriver.Chrome()
bridge = SeleniumBridge(driver)
emitter = EventEmitter()

emitter.add_listener('state_changed', lambda old, new: print(f"{old} → {new}"))

context = ProcessContext(credentials={'username': 'test', 'password': 'pass'})
process = LoginProcess()

runner = ProcessRunner(process, context, bridge, emitter)
outcome = runner.run()

print(f"Result: {outcome}")
driver.quit()
```

---

## Error Handling

```python
from athesa.exceptions import (
    AthesaError,                    # Base exception
    ActionFailedException,          # Action execution failed
    ProcessInterruptedException,    # Global interrupt detected
    HandlerNotFoundError,           # No handler for screen
    AutomationStoppedException,     # User stopped
    DetectionTimeoutError,          # Screen not found
    BridgeError,                    # Bridge operation failed
)

try:
    runner.run()
except ActionFailedException as e:
    print(f"Action failed: {e}")
except AutomationStoppedException:
    print("User stopped process")
```

---

## Best Practices

1. **Keep states small**: One screen detection per state
2. **Use events for observability**: Monitor, log, alert
3. **Test with real scenarios**: Use realistic test data
4. **Handle errors gracefully**: Implement retry logic
5. **Document your screens**: Clear selector names
6. **Use protocol compliance**: No forced inheritance
7. **Leverage factory**: Register processes for reuse

---

For more examples, see `examples/` directory.
