"""
Core classes for representing and managing Codex runs and sessions.
"""

import os
import subprocess
import tempfile
import shlex
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
import logging
import time
import json

from .models import CodexRunResult, CodexSessionResult, ChangeType, ToolType
from .parsers import CodexLogParser, CodexOutputParser
from .utils import TemplateProcessor, FileManager
from .health import (
    AgentHealthMonitor, AgentHealthInfo, AgentStatus, HealthStatus, 
    AgentMetrics, get_health_monitor
)

# Supported providers and their default configurations
SUPPORTED_PROVIDERS = {
    'openai': {
        'name': 'OpenAI',
        'env_key': 'OPENAI_API_KEY',
        'base_url': 'https://api.openai.com/v1'
    },
    'azure': {
        'name': 'Azure OpenAI',
        'env_key': 'AZURE_OPENAI_API_KEY',
        'base_url': None  # Configured per deployment
    },
    'openrouter': {
        'name': 'OpenRouter',
        'env_key': 'OPENROUTER_API_KEY',
        'base_url': 'https://openrouter.ai/api/v1'
    },
    'gemini': {
        'name': 'Gemini',
        'env_key': 'GEMINI_API_KEY',
        'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai'
    },
    'ollama': {
        'name': 'Ollama',
        'env_key': 'OLLAMA_API_KEY',
        'base_url': 'http://localhost:11434/v1'
    },
    'mistral': {
        'name': 'Mistral',
        'env_key': 'MISTRAL_API_KEY',
        'base_url': 'https://api.mistral.ai/v1'
    },
    'deepseek': {
        'name': 'DeepSeek',
        'env_key': 'DEEPSEEK_API_KEY',
        'base_url': 'https://api.deepseek.com/v1'
    },
    'xai': {
        'name': 'xAI',
        'env_key': 'XAI_API_KEY',
        'base_url': 'https://api.x.ai/v1'
    },
    'groq': {
        'name': 'Groq',
        'env_key': 'GROQ_API_KEY',
        'base_url': 'https://api.groq.com/openai/v1'
    },
    'arceeai': {
        'name': 'Arcee AI',
        'env_key': 'ARCEEAI_API_KEY',
        'base_url': 'https://api.arcee.ai/v1'
    }
}


def validate_provider_config(provider: str) -> None:
    """
    Validate provider configuration and check for required environment variables.
    
    Args:
        provider: The provider name to validate
        
    Raises:
        ValueError: If provider is not supported or configuration is invalid
        RuntimeError: If required environment variable is missing
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers: {list(SUPPORTED_PROVIDERS.keys())}")
    
    provider_config = SUPPORTED_PROVIDERS[provider]
    env_key = provider_config['env_key']
    
    if not os.getenv(env_key):
        raise RuntimeError(f"Missing environment variable {env_key} required for {provider_config['name']} provider")


def get_provider_env_key(provider: str) -> str:
    """
    Get the environment variable key for a provider.
    
    Args:
        provider: The provider name
        
    Returns:
        The environment variable key
    """
    if provider not in SUPPORTED_PROVIDERS:
        return f"{provider.upper()}_API_KEY"
    
    return SUPPORTED_PROVIDERS[provider]['env_key']


class CodexRun:
    """
    Represents a single run of Codex with parsing capabilities for outputs.
    Each instance represents one execution with its complete lifecycle.
    """
    
    def __init__(self, 
                 prompt: str,
                 model: str = "gpt-4.1-nano",
                 provider: str = "openai",
                 writable_root: Optional[str] = None,
                 timeout: int = 300,
                 run_id: Optional[str] = None,
                 approval_mode: str = "full-auto",
                 debug: bool = False,
                 validate_env: bool = True,
                 enable_health_monitoring: bool = True,
                 dangerously_auto_approve_everything: bool = False,
                 on_json_line: Optional[Callable[[Dict], None]] = None):
        """
        Initialize a Codex run.
        
        Args:
            prompt: The prompt to send to Codex
            model: The model to use for the run
            provider: The AI provider to use (openai, azure, gemini, etc.)
            writable_root: Root directory for file operations
            timeout: Timeout in seconds for the run
            run_id: Unique identifier for this run
            approval_mode: Approval mode for the agent
            debug: Enable debug logging
            validate_env: Whether to validate environment variables for the provider
            enable_health_monitoring: Whether to enable health monitoring for this run
            dangerously_auto_approve_everything: Skip all confirmation prompts (for testing)
            on_json_line: Callback function to handle valid JSON lines from stdout
        """
        self.run_id = run_id or str(uuid.uuid4())
        self.prompt = prompt
        self.model = model
        self.provider = provider
        self.writable_root = os.path.expanduser(writable_root) if writable_root else os.getcwd()
        self.timeout = timeout
        self.approval_mode = approval_mode
        self.debug = debug
        self.enable_health_monitoring = enable_health_monitoring
        self.dangerously_auto_approve_everything = dangerously_auto_approve_everything
        self.on_json_line = on_json_line
        
        # Validate provider configuration if requested
        if validate_env:
            validate_provider_config(self.provider)
        
        # Health monitoring setup
        self.health_monitor: Optional[AgentHealthMonitor] = None
        self.health_info: Optional[AgentHealthInfo] = None
        self.process: Optional[subprocess.Popen] = None
        
        if self.enable_health_monitoring:
            self.health_monitor = get_health_monitor()
        
        # State tracking
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.success = False
        self.log_file: Optional[str] = None
        self.output: Optional[str] = None
        self.error: Optional[str] = None
        
        # Parsed results
        self.result: Optional[CodexRunResult] = None
        
        # Setup logging
        self.logger = logging.getLogger(f"codex_run_{self.run_id}")
        if debug:
            self.logger.setLevel(logging.DEBUG)
    
    def execute(self, log_dir: str = ".") -> CodexRunResult:
        """
        Execute the Codex run and parse results.
        
        Args:
            log_dir: Directory to store log files
            
        Returns:
            CodexRunResult with parsed output
        """
        self.start_time = datetime.now()
        self.logger.info(f"Starting Codex run {self.run_id}")
        
        # Register with health monitor
        if self.health_monitor:
            self.health_info = self.health_monitor.register_agent(
                agent_id=self.run_id,
                metadata={
                    'prompt': self.prompt[:100] + '...' if len(self.prompt) > 100 else self.prompt,
                    'model': self.model,
                    'provider': self.provider,
                    'approval_mode': self.approval_mode
                }
            )
        
        try:
            # Generate log file path
            timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
            self.log_file = os.path.join(log_dir, f"codex_run_{timestamp}_{self.run_id[:8]}.log")
            
            # Update health info with log file
            if self.health_monitor and self.health_info:
                self.health_info.log_file = self.log_file
                self.health_monitor.update_agent_status(self.run_id, AgentStatus.RUNNING)
            
            # Execute Codex command
            self._execute_codex()
            
            # Parse the results
            self.result = self._parse_results()
            
            self.success = True
            self.logger.info(f"Codex run {self.run_id} completed successfully")
            
            # Update status to completed
            if self.health_monitor:
                self.health_monitor.update_agent_status(self.run_id, AgentStatus.COMPLETED)
            
        except Exception as e:
            self.error = str(e)
            self.success = False
            self.logger.error(f"Codex run {self.run_id} failed: {e}")
            
            # Update status to failed
            if self.health_monitor:
                self.health_monitor.update_agent_status(self.run_id, AgentStatus.FAILED, str(e))
            
            # Create minimal result even on failure
            self.result = CodexRunResult(
                run_id=self.run_id,
                start_time=self.start_time,
                success=False,
                log_file=self.log_file,
                metadata={
                    'error': str(e),
                    'model': self.model,
                    'provider': self.provider,
                    'writable_root': self.writable_root,
                    'timeout': self.timeout,
                    'prompt': self.prompt
                }
            )
        
        finally:
            self.end_time = datetime.now()
            if self.result:
                self.result.end_time = self.end_time
            
            # Send final heartbeat and unregister
            if self.health_monitor:
                final_metrics = AgentMetrics(
                    runtime_seconds=(self.end_time - self.start_time).total_seconds(),
                    error_count=1 if not self.success else 0,
                    last_activity=self.end_time
                )
                self.health_monitor.heartbeat(self.run_id, final_metrics)
                # Keep agent registered for post-mortem analysis
        
        return self.result
    
    def _execute_codex(self):
        """Execute the Codex command."""
        # Set environment variable to disable sandbox
        env = os.environ.copy()
        env['CODEX_UNSAFE_ALLOW_NO_SANDBOX'] = '1'
        
        # Build command - use codex executable directly
        cmd_parts = [
            "codex",
            f"--model={self.model}",
            f"--provider={self.provider}",
            f"--writable-root={self.writable_root}",
            "--full-auto",
            "--dangerously-auto-approve-everything",
            "--quiet",
            self.prompt
        ]
        
        if self.debug:
            # Remove --debug as it's not a valid option, use verbose logging instead
            pass
        
        # Note: --dangerously-auto-approve-everything is already added above
        # if self.dangerously_auto_approve_everything:
        #     cmd_parts.append("--dangerously-auto-approve-everything")
        
        try:
            self.logger.debug(f"Executing command: {shlex.join(cmd_parts)}")
            print(f"DEBUG: Executing command: {shlex.join(cmd_parts)}")
            print(f"DEBUG: Environment CODEX_UNSAFE_ALLOW_NO_SANDBOX = {env.get('CODEX_UNSAFE_ALLOW_NO_SANDBOX')}")
            
            self.process = subprocess.Popen(
                cmd_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.writable_root,
                env=env
            )
            
            # Update health monitor with process ID
            if self.health_monitor and self.health_info:
                self.health_info.process_id = self.process.pid
                self.health_monitor.heartbeat(self.run_id)

            with open(self.log_file, 'w') as log_f:
                for line in iter(self.process.stdout.readline, ''):
                    log_f.write(line)
                    log_f.flush()

                    if self.on_json_line:
                        try:
                            json_line = json.loads(line)
                            self.on_json_line(json_line)
                        except json.JSONDecodeError:
                            pass # Ignore non-json lines
            
            self.process.wait(timeout=self.timeout)

            # Read the output
            with open(self.log_file, 'r') as log_f:
                self.output = log_f.read()
            
            if self.process.returncode != 0:
                raise RuntimeError(f"Codex command failed with return code {self.process.returncode}")
        
        except subprocess.TimeoutExpired:
            if self.health_monitor:
                self.health_monitor.update_agent_status(self.run_id, AgentStatus.TIMEOUT, "Process timed out")
            raise RuntimeError(f"Codex command timed out after {self.timeout} seconds")
        except Exception as e:
            if self.health_monitor:
                self.health_monitor.update_agent_status(self.run_id, AgentStatus.FAILED, str(e))
            raise RuntimeError(f"Failed to execute Codex command: {e}")
        finally:
            if hasattr(self, 'process') and self.process and self.process.poll() is None:
                self.process.terminate()
    
    def _parse_results(self) -> CodexRunResult:
        """Parse the log file to extract results."""
        if not self.log_file or not os.path.exists(self.log_file):
            raise RuntimeError("No log file available for parsing")
        
        parser = CodexLogParser(os.path.dirname(self.log_file))
        result = parser.parse_run(self.log_file, self.run_id)
        
        # Add our execution metadata
        result.metadata.update({
            'model': self.model,
            'provider': self.provider,
            'writable_root': self.writable_root,
            'timeout': self.timeout,
            'prompt': self.prompt
        })
        
        return result
    
    def get_changes_by_file(self, file_path: str) -> List[Any]:
        """Get all changes for a specific file."""
        if not self.result:
            return []
        
        changes = []
        
        # Check regular changes
        for change in self.result.changes:
            if change.file_path == file_path:
                changes.append(change)
        
        # Check patches
        for patch in self.result.patches:
            if patch.file_path == file_path:
                changes.append(patch)
        
        return changes
    
    def get_tools_used(self) -> List[str]:
        """Get list of unique tools used in this run."""
        if not self.result:
            return []
        
        tools = set()
        for tool_usage in self.result.tool_usage:
            tools.add(tool_usage.tool_name)
        
        return sorted(list(tools))
    
    def get_health_status(self) -> Optional[AgentHealthInfo]:
        """
        Get current health status of this agent.
        
        Returns:
            AgentHealthInfo if health monitoring is enabled, None otherwise
        """
        if not self.health_monitor:
            return None
        
        return self.health_monitor.get_agent_health(self.run_id)
    
    def is_running(self) -> bool:
        """Check if this agent is currently running."""
        if not self.health_monitor:
            return False
        
        health_info = self.health_monitor.get_agent_health(self.run_id)
        return health_info.is_running if health_info else False
    
    def is_healthy(self) -> bool:
        """Check if this agent is currently healthy."""
        if not self.health_monitor:
            return True  # Assume healthy if no monitoring
        
        health_info = self.health_monitor.get_agent_health(self.run_id)
        return health_info.health == HealthStatus.HEALTHY if health_info else False
    
    def terminate(self, force: bool = False) -> bool:
        """
        Terminate this agent.
        
        Args:
            force: Whether to force termination
            
        Returns:
            True if termination was attempted, False if not running or no monitoring
        """
        if not self.health_monitor:
            return False
        
        return self.health_monitor.terminate_agent(self.run_id, force)
    
    def get_runtime_seconds(self) -> float:
        """Get runtime in seconds."""
        if self.start_time:
            end_time = self.end_time or datetime.now()
            return (end_time - self.start_time).total_seconds()
        return 0.0


class CodexSession:
    """
    Manages multiple Codex runs as part of a session.
    Provides batch processing and aggregate analysis capabilities.
    """
    
    def __init__(self, 
                 session_id: Optional[str] = None,
                 default_model: str = "gpt-4.1-nano",
                 default_provider: str = "openai",
                 default_timeout: int = 300,
                 log_dir: str = ".",
                 debug: bool = False,
                 validate_env: bool = True,
                 enable_health_monitoring: bool = True):
        """
        Initialize a Codex session.
        
        Args:
            session_id: Unique identifier for this session
            default_model: Default model for runs
            default_provider: Default provider for runs
            default_timeout: Default timeout for runs
            log_dir: Directory for log files
            debug: Enable debug logging
            validate_env: Whether to validate environment variables for the default provider
            enable_health_monitoring: Whether to enable health monitoring for runs
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.default_model = default_model
        self.default_provider = default_provider
        self.default_timeout = default_timeout
        self.log_dir = log_dir
        self.debug = debug
        self.enable_health_monitoring = enable_health_monitoring
        
        # Validate provider configuration if requested
        if validate_env:
            validate_provider_config(self.default_provider)
        
        # Health monitoring
        self.health_monitor: Optional[AgentHealthMonitor] = None
        if self.enable_health_monitoring:
            self.health_monitor = get_health_monitor()
        
        # State
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.runs: List[CodexRun] = []
        
        # Results
        self.result: Optional[CodexSessionResult] = None
        
        # Setup logging
        self.logger = logging.getLogger(f"codex_session_{self.session_id}")
        if debug:
            self.logger.setLevel(logging.DEBUG)
    
    def add_run(self, 
                prompt: str,
                model: Optional[str] = None,
                provider: Optional[str] = None,
                writable_root: Optional[str] = None,
                timeout: Optional[int] = None,
                approval_mode: str = "full-auto",
                dangerously_auto_approve_everything: bool = False) -> CodexRun:
        """
        Create and add a new run to the session.
        
        Args:
            prompt: The prompt for the run
            model: The model for the run
            provider: The provider for the run
            writable_root: The root directory for the run
            timeout: The timeout for the run
            approval_mode: The approval mode for the run
            dangerously_auto_approve_everything: Skip all confirmation prompts (for testing)
            
        Returns:
            The created CodexRun instance
        """
        run = CodexRun(
            prompt=prompt,
            model=model or self.default_model,
            provider=provider or self.default_provider,
            writable_root=writable_root,
            timeout=timeout or self.default_timeout,
            approval_mode=approval_mode,
            debug=self.debug,
            validate_env=False,  # Already validated in session init
            enable_health_monitoring=self.enable_health_monitoring,
            dangerously_auto_approve_everything=dangerously_auto_approve_everything
        )
        self.runs.append(run)
        return run
    
    def execute_all(self) -> CodexSessionResult:
        """
        Execute all runs in the session.
        
        Returns:
            CodexSessionResult with aggregate results
        """
        self.start_time = datetime.now()
        self.logger.info(f"Starting session {self.session_id} with {len(self.runs)} runs")
        
        # Print session start banner
        print(f"\n  [{self.start_time.strftime('%H:%M:%S')}] Starting Codex Session:")
        print(f"     Session ID: {self.session_id}")
        print(f"   🔢 Total Runs: {len(self.runs)}")
        print(f"     Model: {self.default_model} ({self.default_provider})")
        print(f"   ⏱️  Timeout: {self.default_timeout}s per run")
        print()
        
        run_results = []
        
        for i, run in enumerate(self.runs, 1):
            # Print run start info
            print(f"📍 [{datetime.now().strftime('%H:%M:%S')}] Starting Run {i}/{len(self.runs)}:")
            print(f"   🆔 Run ID: {run.run_id}")
            print(f"     Prompt: {run.prompt[:80]}{'...' if len(run.prompt) > 80 else ''}")
            print(f"     Working Dir: {run.writable_root}")
            print()
            
            self.logger.info(f"Executing run {i}/{len(self.runs)}: {run.run_id}")
            
            run_start_time = datetime.now()
            try:
                result = run.execute(self.log_dir)
                run_results.append(result)
                
                # Print run completion info
                run_duration = (datetime.now() - run_start_time).total_seconds()
                print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Run {i}/{len(self.runs)} Completed:")
                print(f"   ⏱️  Duration: {run_duration:.1f}s")
                print(f"   ✅ Success: {result.success if result else False}")
                if result and result.changes:
                    print(f"     Changes: {len(result.changes)}")
                if result and hasattr(result, 'files_modified'):
                    print(f"     Files: {len(result.files_modified)}")
                print()
                
            except Exception as e:
                run_duration = (datetime.now() - run_start_time).total_seconds()
                print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Run {i}/{len(self.runs)} Failed:")
                print(f"   ⏱️  Duration: {run_duration:.1f}s")
                print(f"   ❌ Error: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}")
                print()
                
                self.logger.error(f"Run {run.run_id} failed: {e}")
                # Still add failed result
                run_results.append(run.result)
            
            # Print session progress summary
            successful_so_far = sum(1 for r in run_results if r and r.success)
            session_runtime = (datetime.now() - self.start_time).total_seconds()
            print(f"  Session Progress: {i}/{len(self.runs)} runs completed ({successful_so_far} successful) in {session_runtime:.1f}s")
            print("-" * 60)
            print()
        
        self.end_time = datetime.now()
        
        # Create session result
        self.result = CodexSessionResult(
            session_id=self.session_id,
            runs=run_results,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        # Print final session summary
        total_duration = (self.end_time - self.start_time).total_seconds()
        successful_runs = len(self.result.successful_runs)
        print(f"🏁 [{self.end_time.strftime('%H:%M:%S')}] Session Completed:")
        print(f"     Session ID: {self.session_id}")
        print(f"   ⏱️  Total Duration: {total_duration:.1f}s")
        print(f"   ✅ Successful Runs: {successful_runs}/{len(run_results)}")
        print(f"     Success Rate: {(successful_runs/len(run_results)*100):.1f}%" if run_results else "0%")
        if self.result.total_files_modified:
            print(f"     Files Modified: {len(self.result.total_files_modified)}")
        print(f"     Total Changes: {self.result.total_changes}")
        print()
        
        self.logger.info(f"Session {self.session_id} completed with {successful_runs}/{len(run_results)} successful runs")
        
        return self.result
    
    def process_csv_data(self, 
                        csv_data: List[Dict[str, str]], 
                        prompt_template: str,
                        template_processor: Optional[TemplateProcessor] = None) -> CodexSessionResult:
        """
        Process CSV data using a prompt template.
        
        Args:
            csv_data: List of CSV row dictionaries
            prompt_template: Jinja2 template for the prompt
            template_processor: Optional custom template processor
            
        Returns:
            CodexSessionResult with results for each row
        """
        if template_processor is None:
            template_processor = TemplateProcessor()
        
        self.logger.info(f"Processing {len(csv_data)} CSV rows")
        
        # Create runs for each CSV row
        for i, row_data in enumerate(csv_data):
            try:
                # Render prompt template with row data
                prompt = template_processor.render_template(prompt_template, row_data)
                
                # Add run
                run = self.add_run(
                    prompt=prompt,
                    # Add row metadata to be able to track which run corresponds to which row
                )
                
                # Add row data to run metadata for later reference
                run.csv_row_index = i
                run.csv_row_data = row_data
                
            except Exception as e:
                self.logger.error(f"Failed to create run for CSV row {i}: {e}")
        
        # Execute all runs
        return self.execute_all()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the session."""
        if not self.result:
            return {}
        
        return {
            'session_id': self.session_id,
            'total_runs': len(self.result.runs),
            'successful_runs': len(self.result.successful_runs),
            'total_files_modified': len(self.result.total_files_modified),
            'total_changes': self.result.total_changes,
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else None
        }
    
    def analyze_by_tool_usage(self) -> Dict[str, int]:
        """Analyze tool usage across all runs."""
        if not self.result:
            return {}
        
        tool_counts = {}
        for run in self.result.runs:
            for tool_usage in run.tool_usage:
                tool_name = tool_usage.tool_name
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        
        return tool_counts
    
    def get_runs_by_success(self, success: bool = True) -> List[CodexRunResult]:
        """Get runs filtered by success status."""
        if not self.result:
            return []
        
        return [run for run in self.result.runs if run.success == success] 
    
    def get_session_health_summary(self) -> Dict[str, Any]:
        """
        Get health summary for all runs in this session.
        
        Returns:
            Dictionary with health statistics
        """
        if not self.health_monitor:
            return {"monitoring_enabled": False}
        
        session_agents = []
        for run in self.runs:
            health_info = self.health_monitor.get_agent_health(run.run_id)
            if health_info:
                session_agents.append(health_info)
        
        if not session_agents:
            return {"monitoring_enabled": True, "agents": 0}
        
        # Calculate statistics
        total_agents = len(session_agents)
        running_count = sum(1 for agent in session_agents if agent.is_running)
        healthy_count = sum(1 for agent in session_agents if agent.health == HealthStatus.HEALTHY)
        failed_count = sum(1 for agent in session_agents if agent.status == AgentStatus.FAILED)
        completed_count = sum(1 for agent in session_agents if agent.status == AgentStatus.COMPLETED)
        
        total_runtime = sum(agent.runtime_seconds for agent in session_agents)
        total_errors = sum(agent.metrics.error_count for agent in session_agents)
        
        return {
            "monitoring_enabled": True,
            "session_id": self.session_id,
            "total_agents": total_agents,
            "running": running_count,
            "healthy": healthy_count,
            "failed": failed_count,
            "completed": completed_count,
            "health_percentage": (healthy_count / total_agents * 100) if total_agents > 0 else 0,
            "completion_percentage": (completed_count / total_agents * 100) if total_agents > 0 else 0,
            "total_runtime_seconds": total_runtime,
            "average_runtime_seconds": total_runtime / total_agents if total_agents > 0 else 0,
            "total_errors": total_errors
        }
    
    def get_running_runs(self) -> List[CodexRun]:
        """Get all currently running runs in this session."""
        return [run for run in self.runs if run.is_running()]
    
    def get_healthy_runs(self) -> List[CodexRun]:
        """Get all healthy runs in this session."""
        return [run for run in self.runs if run.is_healthy()]
    
    def get_runs_by_status(self, status: AgentStatus) -> List[CodexRun]:
        """Get runs filtered by agent status."""
        if not self.health_monitor:
            return []
        
        filtered_runs = []
        for run in self.runs:
            health_info = self.health_monitor.get_agent_health(run.run_id)
            if health_info and health_info.status == status:
                filtered_runs.append(run)
        
        return filtered_runs
    
    def terminate_all_running(self, force: bool = False) -> int:
        """
        Terminate all running agents in this session.
        
        Args:
            force: Whether to force termination
            
        Returns:
            Number of agents terminated
        """
        if not self.health_monitor:
            return 0
        
        running_runs = self.get_running_runs()
        terminated_count = 0
        
        for run in running_runs:
            if run.terminate(force):
                terminated_count += 1
        
        return terminated_count 