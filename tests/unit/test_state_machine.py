"""
Real-world unit tests for StateMachine

Tests state transition scenarios in actual automation flows.
"""

import pytest
from athesa.engine.state_machine import StateMachine
from athesa.events import EventEmitter


class TestStateMachineRealWorld:
    """Real-world state machine scenarios"""
    
    def test_login_flow_with_error_recovery(self):
        """
        Scenario: Login fails, user retries, eventually succeeds
        
        Real use case: Temporary network issues, wrong password retry
        """
        # Define states
        class LoginStart: pass
        class EnteringUsername: pass
        class EnteringPassword: pass
        class LoginError: pass
        class LoginSuccess: pass
        
        # Track transitions
        transitions = []
        
        emitter = EventEmitter()
        emitter.add_listener('state_changed', lambda old, new: transitions.append(new.__class__.__name__))
        
        sm = StateMachine(LoginStart, "login_flow", emitter)
        
        # First attempt - error
        sm.transition_to(EnteringUsername())
        sm.transition_to(EnteringPassword())
        sm.transition_to(LoginError())  # Failed
        
        # Retry
        sm.transition_to(EnteringUsername())
        sm.transition_to(EnteringPassword())
        sm.transition_to(LoginSuccess())  # Success
        
        assert transitions == [
            'EnteringUsername',
            'EnteringPassword',
            'LoginError',
            'EnteringUsername',
            'EnteringPassword',
            'LoginSuccess'
        ]
    
    def test_multi_step_upload_workflow(self):
        """
        Scenario: Complex upload flow with metadata, preview, confirmation
        
        Real use case: YouTube upload - select file, enter details, review, publish
        """
        class UploadInit: pass
        class FileSelected: pass
        class EnteringTitle: pass
        class EnteringDescription: pass
        class SelectingThumbnail: pass
        class ReviewScreen: pass
        class Publishing: pass
        class Published: pass
        
        state_sequence = []
        
        emitter = EventEmitter()
        emitter.add_listener('state_changed', lambda old, new: state_sequence.append(new.__class__.__name__))
        
        sm = StateMachine(UploadInit, "youtube_upload", emitter)
        
        # Complete upload flow
        sm.transition_to(FileSelected())
        sm.transition_to(EnteringTitle())
        sm.transition_to(EnteringDescription())
        sm.transition_to(SelectingThumbnail())
        sm.transition_to(ReviewScreen())
        sm.transition_to(Publishing())
        sm.transition_to(Published())
        
        # Verify complete sequence
        assert len(state_sequence) == 7
        assert state_sequence[-1] == 'Published'
    
    def test_conditional_branching_flow(self):
        """
        Scenario: Flow branches based on account status
        
        Real use case: New user setup vs returning user, premium vs free tier
        """
        class CheckingAccount: pass
        class NewUserSetup: pass
        class ReturningUserDashboard: pass
        class PremiumFeatures: pass
        class FreeFeatures: pass
        
        # Simulate different user types
        for user_type in ['new', 'returning_free', 'returning_premium']:
            path = []
            
            emitter = EventEmitter()
            emitter.add_listener('state_changed', lambda old, new: path.append(new.__class__.__name__))
            
            sm = StateMachine(CheckingAccount, f"flow_{user_type}", emitter)
            
            if user_type == 'new':
                sm.transition_to(NewUserSetup())
            elif user_type == 'returning_free':
                sm.transition_to(ReturningUserDashboard())
                sm.transition_to(FreeFeatures())
            else:  # returning_premium
                sm.transition_to(ReturningUserDashboard())
                sm.transition_to(PremiumFeatures())
            
            # Verify different paths
            if user_type == 'new':
                assert path == ['NewUserSetup']
            elif user_type == 'returning_free':
                assert path == ['ReturningUserDashboard', 'FreeFeatures']
            else:
                assert path == ['ReturningUserDashboard', 'PremiumFeatures']
    
    def test_timeout_and_retry_states(self):
        """
        Scenario: Process times out waiting for user action, retries
        
        Real use case: Phone verification, 2FA wait, manual CAPTCHA solving
        """
        class WaitingFor2FA: pass
        class Timeout: pass
        class RetryPrompt: pass
        class Verified: pass
        
        attempts = []
        
        emitter = EventEmitter()
        emitter.add_listener('state_changed', lambda old, new: attempts.append(new.__class__.__name__))
        
        sm = StateMachine(WaitingFor2FA, "2fa_flow", emitter)
        
        # First attempt - timeout
        sm.transition_to(Timeout())
        sm.transition_to(RetryPrompt())
        sm.transition_to(WaitingFor2FA())
        
        # Second attempt - timeout again
        sm.transition_to(Timeout())
        sm.transition_to(RetryPrompt())
        sm.transition_to(WaitingFor2FA())
        
        # Third attempt - success
        sm.transition_to(Verified())
        
        assert attempts.count('Timeout') == 2
        assert attempts.count('RetryPrompt') == 2
        assert attempts[-1] == 'Verified'
    
    def test_state_machine_reset_for_batch_processing(self):
        """
        Scenario: Reset state machine between batch items
        
        Real use case: Process 100 videos, reset state for each
        """
        class ProcessInit: pass
        class Processing: pass
        class Complete: pass
        
        items_processed = 0
        
        emitter = EventEmitter()
        sm = StateMachine(ProcessInit, "batch_processor", emitter)
        
        # Process 3 items
        for i in range(3):
            sm.reset(ProcessInit)
            assert isinstance(sm.current_state, ProcessInit)  # After reset
            sm.transition_to(Processing())
            sm.transition_to(Complete())
            items_processed += 1
        
        assert items_processed == 3
        # After completing 3 items, current state is Complete (last transition)
        assert isinstance(sm.current_state, Complete)
