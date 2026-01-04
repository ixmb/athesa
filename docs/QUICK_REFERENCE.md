# Athesa Quick Reference

Quick lookup for common operations.

---

## Basic Setup

```python
from athesa import ProcessRunner, ProcessContext
from athesa.adapters.selenium import SeleniumBridge
from selenium import webdriver

driver = webdriver.Chrome()
bridge = SeleniumBridge(driver)
context = ProcessContext(credentials={'username': 'user', 'password': 'pass'})

runner = ProcessRunner(process, context, bridge)
outcome = runner.run()
```

---

## Define a Process

```python
class MyProcess:
    @property
    def name(self) -> str: return "my_process"
    
    @property
    def initial_state(self): return InitialState
    
    @property
    def registry(self): return {ScreenType.LOGIN: LoginHandler()}
    
    @property
    def screens(self):
        return [ScreenDefinition(type=ScreenType.LOGIN, selector=(By.ID, 'login'))]
    
    @property
    def final_states(self): return (SuccessState, FailureState)
```

---

## Define a State

```python
class MyState:
    def handle(self, context): pass
    def get_expected_screens(self): return [ScreenType.LOGIN]
    def on_detection_failed(self, context): context.transition_to(FailureState())
```

---

## Define a Handler

```python
class MyHandler:
    def create_action_sequence(self, context):
        return ActionSequence(
            actions=[Action(ActionCommand.CLICK, {'selector': (By.ID, 'btn')})],
            next_state=NextState
        )
```

---

## Common Actions

```python
# Click
Action(ActionCommand.CLICK, {'selector': (By.ID, 'button')})

# Type text
Action(ActionCommand.TYPE, {'selector': (By.CSS, 'input'), 'text': 'hello'})

# Navigate
Action(ActionCommand.NAVIGATE, {'url': 'https://example.com'})

# Wait
Action(ActionCommand.WAIT, {'duration': 2})

# Execute JavaScript
Action(ActionCommand.EXECUTE_SCRIPT, {'script': 'window.scrollTo(0, 100)'})

# Upload file
Action(ActionCommand.UPLOAD_FILE, {'selector': (By.ID, 'file'), 'file_path': '/path/to/file'})
```

---

## Event Listening

```python
from athesa.events import EventEmitter

emitter = EventEmitter()

emitter.add_listener('state_changed', lambda old, new: print(f"{old} → {new}"))
emitter.add_listener('screen_detected', lambda screen: print(f"Detected: {screen.name}"))
emitter.add_listener('action_executed', lambda action: print(f"Executed: {action.command.name}"))

runner = ProcessRunner(process, context, bridge, event_emitter=emitter)
```

---

## Process Registry

```python
from athesa.factory import registry

# Register
registry.register('login', LoginProcess)

# Create
process = registry.create('login')

# List all
for name in registry.list():
    print(name)
```

---

## Context Usage

```python
# Create
context = ProcessContext(
    credentials={'username': 'test', 'password': 'pass'},
    data={'video': 'path/to/video.mp4'}
)

# Access
username = context.credentials['username']
video_path = context.data['video']

# Temporary storage
context.temp['session_id'] = '12345'

# Manual transition
context.transition_to(NextState())
```

---

## Screen Detection Strategies

```python
from athesa.core.screen import DetectionStrategy

# Visible and enabled (default)
ScreenDefinition(
    type=ScreenType.LOGIN,
    selector=(By.ID, 'login'),
    detection_strategy=DetectionStrategy.VISIBLE_AND_ENABLED
)

# Presence only (exists in DOM)
ScreenDefinition(
    type=ScreenType.HIDDEN,
    selector=(By.ID, 'hidden-element'),
    detection_strategy=DetectionStrategy.PRESENCE_ONLY
)

# Custom verification
ScreenDefinition(
    type=ScreenType.LOADED,
    selector=(By.ID, 'content'),
    detection_strategy=DetectionStrategy.CUSTOM,
    verification_criteria=[
        lambda driver: driver.find_element(By.ID, 'content').get_attribute('data-loaded') == 'true'
    ]
)
```

---

## Run Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_events.py

# Run with coverage
pytest --cov=athesa tests/
```

---

## Debugging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Events for debugging
emitter.add_listener('state_changed', lambda old, new: logging.info(f"State: {old} → {new}"))
emitter.add_listener('detection_timeout', lambda screens: logging.warning(f"Timeout: {screens}"))
emitter.add_listener('action_failed', lambda action, error: logging.error(f"Failed: {error}"))
```

---

## Common Patterns

### Login then upload

```python
class LoginThenUploadProcess:
    @property
    def initial_state(self): return LoginInitialState
    
    @property
    def registry(self):
        return {
            # Login screens
            Screens.LOGIN: LoginHandler(),
            # Upload screens after login
            Screens.UPLOAD_PAGE: UploadHandler(),
            Screens.SUCCESS: SuccessHandler(),
        }
    
    @property
    def final_states(self): return (UploadSuccessState, FailureState)
```

### Retry on error

```python
class RetryState:
    def __init__(self, max_retries=3):
        self.retries = 0
        self.max_retries = max_retries
    
    def on_detection_failed(self, context):
        self.retries += 1
        if self.retries < self.max_retries:
            context.transition_to(RetryState(self.max_retries))
        else:
            context.transition_to(FailureState())
```

### Conditional branching

```python
class ConditionalHandler:
    def create_action_sequence(self, context):
        if context.get('use_premium_flow'):
            next_state = PremiumState
        else:
            next_state = FreeState
        
        return ActionSequence(actions=[...], next_state=next_state)
```

---

For complete API reference, see [API.md](API.md).
