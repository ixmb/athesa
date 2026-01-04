"""
Example runner script for Basic Login Process

Run this script to see the login process in action.
"""

from selenium import webdriver
from athesa import ProcessRunner, ProcessContext
from athesa.adapters.selenium import SeleniumBridge
from athesa.events import EventEmitter

from process import BasicLoginProcess


def main():
    """Run the basic login process"""
    
    # Setup event listener for observability
    emitter = EventEmitter()
    
    def on_state_changed(old_state, new_state):
        print(f"🔄 State: {old_state.__class__.__name__} → {new_state.__class__.__name__}")
    
    def on_screen_detected(screen):
        print(f"👁️  Detected: {screen.name}")
    
    def on_action_executed(action):
        if action.message:
            print(f"⚡ {action.message}")
    
    emitter.add_listener('state_changed', on_state_changed)
    emitter.add_listener('screen_detected', on_screen_detected)
    emitter.add_listener('action_executed', on_action_executed)
    
    # Setup browser
    print("🚀 Starting browser...")
    driver = webdriver.Chrome()
    bridge = SeleniumBridge(driver)
    
    try:
        # Create process and context
        process = BasicLoginProcess()
        context = ProcessContext(
            credentials={
                'username': 'test@example.com',
                'password': 'test123'
            }
        )
        
        # Navigate to login page first
        print("🌐 Navigating to login page...")
        bridge.navigate("https://example.com/login")  # Replace with actual URL
        
        # Run process
        print("▶️  Running login process...\n")
        runner = ProcessRunner(process, context, bridge, event_emitter=emitter)
        outcome = runner.run()
        
        print(f"\n✅ Process completed: {outcome}")
        
        if outcome == 'success':
            print("🎉 Login successful!")
        else:
            print("❌ Login failed!")
    
    finally:
        print("\n🔒 Closing browser...")
        driver.quit()


if __name__ == '__main__':
    main()
