# Athesa Documentation

Welcome to Athesa - a state-driven web automation framework for complex workflows.

## Quick Links

- **[API Reference](API.md)** - Complete API documentation
- **[Examples](../examples/)** - Working examples
- **[GitHub](https://github.com/ixmb/athesa)** - Source code

## Getting Started

### Installation

```bash
pip install athesa
```

### Your First Process

```python
from athesa import ProcessRunner, ProcessContext
from athesa.adapters.selenium import SeleniumBridge
from selenium import webdriver

# Setup browser
driver = webdriver.Chrome()
bridge = SeleniumBridge(driver)

# Create process (see examples/)
from my_processes import LoginProcess
process = LoginProcess()

# Create context
context = ProcessContext(
    credentials={'username': 'user@example.com', 'password': 'secret'}
)

# Run!
runner = ProcessRunner(process, context, bridge)
outcome = runner.run()  # 'success', 'failure', or 'retry'

print(f"Login {outcome}!")
driver.quit()
```

## Core Concepts

### Process
A complete workflow from start to finish. Defines screens, handlers, states, and transitions.

### State
A step in your workflow. Each state knows what screens to expect.

### Screen
A detectable page state using selectors and verification criteria.

### Handler
Actions to perform when a screen is detected.

### Bridge
Abstraction layer for browser automation (Selenium, Playwright, custom).

## Architecture

```
┌─────────────────────────────────────────┐
│         Your Process Definition         │
│  (States, Screens, Handlers)           │
└──────────────┬──────────────────────────┘
               │
       ┌───────▼────────┐
       │ ProcessRunner  │
       └───────┬────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌──▼──┐  ┌───▼────┐
│State  │  │Page │  │Action  │
│Machine│  │Det. │  │Executor│
└───┬───┘  └──┬──┘  └───┬────┘
    │         │         │
    └─────────┼─────────┘
              │
        ┌─────▼─────┐
        │  Bridge   │
        │ (Selenium)│
        └─────┬─────┘
              │
        ┌─────▼─────┐
        │ WebDriver │
        └───────────┘
```

## Why Athesa?

**Problem**: Web automation is brittle. Pages change, flows have edge cases, errors are hard to debug.

**Solution**: Athesa uses explicit state machines and screen detection:
- ✅ Clear state transitions make debugging easy
- ✅ Multiple detection strategies handle dynamic pages
- ✅ Process registry allows flow composition
- ✅ Event system provides observability
- ✅ Protocol-based (no forced inheritance)

## Examples

See `examples/` directory:
- `basic_login/` - Simple username/password login flow

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## License

MIT License - see LICENSE file
