"""
Real-world unit tests for ProcessRegistry

Tests realistic factory and discovery scenarios.
"""

import pytest
from athesa.factory import ProcessRegistry
from athesa.core.process import ProcessProtocol


class TestProcessRegistryRealWorld:
    """Real-world registry usage scenarios"""
    
    def test_multi_tenant_process_management(self):
        """
        Scenario: SaaS platform managing different customer automation processes
        
        Real use case: Each customer has different login processes, workflows
        """
        registry = ProcessRegistry()
        
        # Customer A processes
        class CustomerALogin:
            @property
            def name(self): return "customer_a_login"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        # Customer B processes
        class CustomerBLogin:
            @property
            def name(self): return "customer_b_login"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        # Register customer-specific processes
        registry.register('tenant_a_login', CustomerALogin)
        registry.register('tenant_b_login', CustomerBLogin)
        
        # Verify isolation
        assert 'tenant_a_login' in registry.list()
        assert 'tenant_b_login' in registry.list()
        
        # Create customer-specific instances
        process_a = registry.create('tenant_a_login')
        process_b = registry.create('tenant_b_login')
        
        assert process_a.name == "customer_a_login"
        assert process_b.name == "customer_b_login"
    
    def test_process_versioning(self):
        """
        Scenario: Maintain multiple versions of same process
        
        Real use case: A/B testing, gradual rollout, fallback to old version
        """
        registry = ProcessRegistry()
        
        class LoginV1:
            version = "1.0"
            @property
            def name(self): return "login_v1"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        class LoginV2:
            version = "2.0"
            @property
            def name(self): return "login_v2"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        # Register versions
        registry.register('login_v1', LoginV1)
        registry.register('login_v2', LoginV2)
        
        # Use specific version based on feature flag
        use_new_version = True
        process_key = 'login_v2' if use_new_version else 'login_v1'
        
        process = registry.create(process_key)
        expected_version = "2.0" if use_new_version else "1.0"
        assert process.version == expected_version
    
    def test_dynamic_process_loading(self):
        """
        Scenario: Load processes from configuration at runtime
        
        Real use case: Plugin system, dynamic configuration
        """
        registry = ProcessRegistry()
        
        # Simulate config-driven process loading
        config = {
            'enabled_processes': ['google_login', 'youtube_upload', 'facebook_post'],
            'disabled_processes': ['twitter_post']
        }
        
        # Mock process classes
        class GoogleLogin:
            @property
            def name(self): return "google_login"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        class YouTubeUpload:
            @property
            def name(self): return "youtube_upload"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        # Register only enabled processes
        for process_name in config['enabled_processes']:
            if process_name == 'google_login':
                registry.register(process_name, GoogleLogin)
            elif process_name == 'youtube_upload':
                registry.register(process_name, YouTubeUpload)
            # ... more processes
       
        # Verify only enabled processes are available
        assert 'google_login' in registry.list()
        assert 'youtube_upload' in registry.list()
        assert 'twitter_post' not in registry.list()  # Disabled
    
    def test_process_discovery_api(self):
        """
        Scenario: REST API for discovering available automation processes
        
        Real use case: Frontend UI shows available automations to user
        """
        registry = ProcessRegistry()
        
        # Register processes with metadata
        class ProcessWithMetadata:
            @property
            def name(self): return "example_process"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
            
            # Extra metadata for API response
            description = "Example automation process"
            category = "social_media"
            estimated_duration_seconds = 30
        
        registry.register('example', ProcessWithMetadata)
        
        # Simulate API endpoint: GET /api/processes
        def get_available_processes():
            processes = []
            for name in registry.list():
                process_class = registry.get(name)
                processes.append({
                    'id': name,
                    'name': process_class().name,
                    'description': getattr(process_class, 'description', 'N/A'),
                    'category': getattr(process_class, 'category', 'general'),
                    'duration': getattr(process_class, 'estimated_duration_seconds', None)
                })
            return processes
        
        api_response = get_available_processes()
        
        assert len(api_response) == 1
        assert api_response[0]['id'] == 'example'
        assert api_response[0]['category'] == 'social_media'
        assert api_response[0]['duration'] == 30
    
    def test_process_dependency_management(self):
        """
        Scenario: Some processes require others to run first
        
        Real use case: Login must succeed before upload, setup before execution
        """
        registry = ProcessRegistry()
        
        class LoginProcess:
            required_before = []
            @property
            def name(self): return "login"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        class UploadProcess:
            required_before = ['login']  # Requires login first
            @property
            def name(self): return "upload"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        registry.register('login', LoginProcess)
        registry.register('upload', UploadProcess)
        
        # Check dependencies before running
        upload_class = registry.get('upload')
        dependencies = getattr(upload_class, 'required_before', [])
        
        assert 'login' in dependencies
        
        # Verify all dependencies are available
        for dep in dependencies:
            assert dep in registry.list(), f"Missing dependency: {dep}"
    
    def test_hot_reload_processes(self):
        """
        Scenario: Update process definition without restarting application
        
        Real use case: Development workflow, quick iteration, A/B testing swaps
        """
        registry = ProcessRegistry()
        
        class LoginV1:
            version = 1
            @property
            def name(self): return "login"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        class LoginV2:
            version = 2
            @property
            def name(self): return "login"
            @property
            def initial_state(self): return None
            @property
            def registry(self): return {}
            @property
            def screens(self): return []
            @property
            def final_states(self): return ()
        
        # Register initial version
        registry.register('login', LoginV1)
        process = registry.create('login')
        assert process.version == 1
        
        # Hot reload: replace with new version
        registry.register('login', LoginV2, force=True)
        process = registry.create('login')
        assert process.version == 2
