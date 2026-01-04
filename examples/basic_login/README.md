# Basic Login Example

This example demonstrates a complete Athesa process for a simple username/password login flow.

## Files

- `process.py` - Complete process definition with states, handlers, and screens
- `run.py` - Example runner script

## What it demonstrates

- **States**: LoginInitialState → UsernameEnteredState → PasswordEnteredState → Success/Failed
- **Screens**: Username input, password input, error message, success indicator
- **Handlers**: Username entry, password entry, error handling
- **Event System**: State changes, screen detection, action execution

## How to run

```bash
cd athesa

# Install package
pip install -e .

# Run example
python examples/basic_login/run.py
```

## Expected output

```
 Starting browser...
🌐 Navigating to login page...
▶️  Running login process...

🔄 State: LoginInitialState → UsernameEnteredState
👁️  Detected: USERNAME_SCREEN
⚡ Entering username: test@example.com
⚡ Clicking Next

🔄 State: UsernameEnteredState → PasswordEnteredState
👁️  Detected: PASSWORD_SCREEN
⚡ Entering password
⚡ Clicking Login

🔄 State: PasswordEnteredState → LoginSuccessState
👁️  Detected: SUCCESS_SCREEN

✅ Process completed: success
🎉 Login successful!
```

## Customization

Replace the URL in `run.py` with your actual login page:

```python
bridge.navigate("https://your-site.com/login")
```

Update selectors in `process.py` to match your site's HTML.

## Learning points

1. **Process structure**: States → Screens → Handlers → Actions
2. **Event observability**: Monitor process execution in real-time
3. **Context usage**: Pass credentials securely
4. **Protocol compliance**: No inheritance needed - just implement properties
