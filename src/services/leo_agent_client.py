"""
Leo Agent Client - Direct integration with Leo API
Handles Leo-specific payload formatting and SSE response parsing
"""

import logging
import json
import time
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class LeoAgentClient:
    """
    Direct client for Leo streaming API.
    Handles format conversion and SSE response parsing.
    """
    
    def __init__(
        self,
        api_base_url: str,
        workflow_id: str,
        bearer_token: str,
        subscription_key: str,
        bpc: str = "20210511",
        environment: str = "DEV",
        version: str = "74d530a1-8dc8-443a-977b-1fc34434e806"
    ):
        """
        Initialize Leo client with credentials.
        
        Args:
            api_base_url: Leo API base URL
            workflow_id: Leo workflow ID
            bearer_token: OAuth bearer token for authentication
            subscription_key: Azure API subscription key
            bpc: Business process context
            environment: Environment (DEV/PROD)
            version: Workflow version
        """
        self.base_url = api_base_url
        self.workflow_id = workflow_id
        self.bearer_token = bearer_token
        self.subscription_key = subscription_key
        self.bpc = bpc
        self.environment = environment
        self.version = version
        
        logger.info(f"Leo client initialized for workflow: {workflow_id}")
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for Leo API request."""
        return {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {self.bearer_token}",
            "content-type": "application/json",
            "ocp-apim-subscription-key": self.subscription_key,
            "user-agent": "Automagik-Omni/1.0"
        }
    
    def _format_session_id(self, session_id: str) -> str:
        """
        Convert session ID to Leo's expected format.
        Leo expects: "session_<timestamp_ms>"
        
        Args:
            session_id: Original session ID from Omni
            
        Returns:
            Formatted session ID for Leo
        """
        if session_id.startswith("session_"):
            return session_id
        
        # Generate timestamp-based session ID
        leo_session_id = f"session_{int(time.time() * 1000)}"
        logger.debug(f"Converted session ID '{session_id}' -> '{leo_session_id}'")
        return leo_session_id
    
    def _build_payload(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Build Leo API payload.
        
        Args:
            message: User's message
            session_id: Session identifier
            
        Returns:
            Formatted payload for Leo API
        """
        leo_session_id = self._format_session_id(session_id)
        
        # Build runtime token - use the bearer token with Bearer prefix for runtimeToken
        runtime_token = f"Bearer {self.bearer_token}" if not self.bearer_token.startswith("Bearer ") else self.bearer_token
        
        return {
            "bpc": self.bpc,
            "environment": self.environment,
            "version": self.version,
            "interface": {
                "inputs": {
                    "message": message
                }
            },
            "options": {
                "sessionId": leo_session_id,
                "runtimeToken": runtime_token,
                "streamMode": "verbose"
            }
        }
    
    def _parse_sse_response(self, response: requests.Response) -> str:
        """
        Parse Server-Sent Events (SSE) streaming response from Leo.
        
        Args:
            response: Streaming HTTP response
            
        Returns:
            Complete response text assembled from SSE deltas
        """
        text_deltas = []
        state_snapshot = None
        
        logger.info("Parsing SSE streaming response from Leo API...")
        
        try:
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.strip():
                    continue
                
                # Parse SSE format: "data: {...}"
                if line.startswith("data:"):
                    json_str = line[5:].strip()
                    
                    try:
                        event = json.loads(json_str)
                        event_type = event.get("type", "")
                        
                        # Collect streaming text deltas
                        if event_type == "TEXT_MESSAGE_CONTENT":
                            delta = event.get("delta", "")
                            if delta:
                                text_deltas.append(delta)
                                logger.debug(f"Collected delta: {delta}")
                        
                        # Store state snapshot for fallback
                        elif event_type == "STATE_SNAPSHOT":
                            state_snapshot = event
                            logger.debug("Received STATE_SNAPSHOT")
                        
                        # RUN_FINISHED marks end of stream
                        elif event_type == "RUN_FINISHED":
                            logger.info("Stream completed (RUN_FINISHED)")
                    
                    except json.JSONDecodeError:
                        continue
            
            # Option 1: Use collected deltas (primary method)
            if text_deltas:
                final_text = "".join(text_deltas)
                logger.info(f"Assembled response from {len(text_deltas)} deltas: {final_text[:100]}...")
                return final_text
            
            # Option 2: Extract from STATE_SNAPSHOT (fallback)
            if state_snapshot:
                logger.info("Using STATE_SNAPSHOT fallback")
                snapshot_data = state_snapshot.get("snapshot", [])
                
                if len(snapshot_data) > 1 and isinstance(snapshot_data[1], dict):
                    # Try agent_0 path
                    if "agent_0" in snapshot_data[1]:
                        agent_vars = snapshot_data[1]["agent_0"].get("variables", {})
                        nodes = agent_vars.get("nodes", {})
                        if "agent_0" in nodes:
                            text = nodes["agent_0"].get("text", "")
                            if text:
                                logger.info(f"Extracted from STATE_SNAPSHOT: {text[:100]}...")
                                return text
                    
                    # Try final_response path
                    if "final_response" in snapshot_data[1]:
                        final_vars = snapshot_data[1]["final_response"].get("variables", {})
                        nodes = final_vars.get("nodes", {})
                        if "agent_0" in nodes:
                            text = nodes["agent_0"].get("text", "")
                            if text:
                                logger.info(f"Extracted from final_response: {text[:100]}...")
                                return text
            
            # No text found
            logger.warning("Could not extract text from Leo response")
            return "I processed your request, but couldn't extract a response."
            
        except Exception as e:
            logger.error(f"Error parsing SSE response: {e}", exc_info=True)
            raise RuntimeError(f"Failed to parse Leo response: {e}")
    
    def call_agent(
        self,
        message: str,
        session_id: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call Leo agent and return response.
        
        Args:
            message: User's message
            session_id: Session identifier
            user_id: User identifier (optional, for logging)
            context: Additional context (optional)
            
        Returns:
            AI response text
            
        Raises:
            RuntimeError: If API call fails
        """
        url = f"{self.base_url}/workflow-engine/{self.workflow_id}/stream"
        headers = self._build_headers()
        payload = self._build_payload(message, session_id)
        
        logger.info(f"Calling Leo API for user: {user_id}")
        logger.debug(f"URL: {url}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            # Make streaming request
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=120  # 2 minutes
            )
            
            logger.info(f"Leo API response status: {response.status_code}")
            
            # Check for errors
            if response.status_code != 200:
                error_text = response.text[:500]
                logger.error(f"Leo API error ({response.status_code}): {error_text}")
                
                # Handle specific auth errors with better messaging
                if response.status_code == 401:
                    raise RuntimeError(f"Leo API authentication failed (401): Session has expired or credentials are invalid. Please refresh your Leo API endpoint or check your configuration.")
                
                raise RuntimeError(f"Leo API returned {response.status_code}: {error_text}")
            
            # Parse streaming response
            result_text = self._parse_sse_response(response)
            
            logger.info(f"Successfully received response: {result_text[:100]}...")
            return result_text
            
        except requests.exceptions.Timeout:
            logger.error("Leo API request timed out")
            raise RuntimeError("Leo API request timed out after 120 seconds")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Leo API: {e}")
            raise RuntimeError(f"Could not connect to Leo API: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error calling Leo API: {e}", exc_info=True)
            raise RuntimeError(f"Leo API error: {e}")
    
    def stream_agent(
        self,
        message: str,
        session_id: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Call Leo agent and stream response chunks.
        
        Yields text deltas as they arrive from the SSE stream.
        This is useful for real-time updates to Discord messages.
        
        Args:
            message: User's message
            session_id: Session identifier
            user_id: User identifier (optional, for logging)
            context: Additional context (optional)
            
        Yields:
            Text chunks as they arrive from the API
            
        Raises:
            RuntimeError: If API call fails
        """
        url = f"{self.base_url}/workflow-engine/{self.workflow_id}/stream"
        headers = self._build_headers()
        payload = self._build_payload(message, session_id)
        
        logger.info(f"Calling Leo API (streaming) for user: {user_id}")
        logger.debug(f"URL: {url}")
        logger.debug(f"Payload: {json.dumps(payload)}")
        
        try:
            # Make streaming request
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=120  # 2 minutes
            )
            
            logger.info(f"Leo API response status: {response.status_code}")
            
            # Check for errors
            if response.status_code != 200:
                error_text = response.text[:500]
                logger.error(f"Leo API error ({response.status_code}): {error_text}")
                
                # Handle specific auth errors with better messaging
                if response.status_code == 401:
                    raise RuntimeError(f"Leo API authentication failed (401): Session has expired or credentials are invalid. Please refresh your Leo API endpoint or check your configuration.")
                
                raise RuntimeError(f"Leo API returned {response.status_code}: {error_text}")
            
            # Stream SSE events and yield text deltas
            text_deltas_count = 0
            state_snapshot = None
            all_events = []  # Debug: collect all events
            full_text_buffer = []  # Collect all text for fallback
            
            # Iterate over response lines with proper decoding
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.strip():
                    continue
                
                # Log raw line for debugging (first 300 chars)
                logger.debug(f"RAW SSE line: {line[:300]}")
                
                # Parse SSE format: "data: {...}" or "data:{...}"
                if line.startswith("data:"):
                    json_str = line[5:].strip()  # Remove "data:" prefix
                elif line.startswith("data :"):
                    json_str = line[6:].strip()  # Handle "data :" with space
                else:
                    # Not a data line, skip
                    continue
                
                if not json_str:
                    continue
                
                try:
                    event_data = json.loads(json_str)
                    event_type = event_data.get("type", "")
                    all_events.append(event_type)  # Track all event types
                    
                    logger.debug(f"Parsed event type: '{event_type}'")
                    
                    # Extract and yield text deltas - check ALL possible formats
                    if event_type == "TEXT_MESSAGE_CONTENT":
                        delta = event_data.get("delta", "")
                        if delta:
                            text_deltas_count += 1
                            full_text_buffer.append(delta)
                            logger.info(f"TEXT_MESSAGE_CONTENT #{text_deltas_count}: '{delta}'")
                            yield delta
                    
                    elif event_type == "TEXT_DELTA":
                        delta = event_data.get("delta", "") or event_data.get("content", "") or event_data.get("text", "")
                        if delta:
                            text_deltas_count += 1
                            full_text_buffer.append(delta)
                            logger.info(f"TEXT_DELTA #{text_deltas_count}: '{delta}'")
                            yield delta
                    
                    # Check for message content in different format
                    elif event_type == "MESSAGE":
                        content = event_data.get("content", "")
                        if content:
                            text_deltas_count += 1
                            full_text_buffer.append(content)
                            yield content
                    
                    # Store state snapshot for fallback
                    elif event_type == "STATE_SNAPSHOT":
                        state_snapshot = event_data
                        logger.debug(f"STATE_SNAPSHOT received with keys: {list(event_data.keys())}")
                    
                    # RUN_FINISHED marks end of stream
                    elif event_type == "RUN_FINISHED":
                        logger.info(f"Stream completed (RUN_FINISHED) after {text_deltas_count} deltas")
                        logger.info(f"All event types received: {sorted(set(all_events))}")
                        if full_text_buffer:
                            logger.info(f"Full text assembled: {''.join(full_text_buffer)[:100]}...")
                
                except json.JSONDecodeError as je:
                    logger.warning(f"JSON decode error: {je}, data: {json_str[:100]}")
                    continue
            
            # If no deltas were yielded, try fallback from state snapshot
            if text_deltas_count == 0 and state_snapshot:
                logger.info("No TEXT_DELTA events found, attempting fallback from STATE_SNAPSHOT")
                snapshot_data = state_snapshot.get("snapshot", [])
                
                if len(snapshot_data) > 1 and isinstance(snapshot_data[1], dict):
                    # Try agent_0 path
                    if "agent_0" in snapshot_data[1]:
                        agent_vars = snapshot_data[1]["agent_0"].get("variables", {})
                        nodes = agent_vars.get("nodes", {})
                        if "agent_0" in nodes:
                            text = nodes["agent_0"].get("text", "")
                            if text:
                                logger.info(f"Yielding from STATE_SNAPSHOT (agent_0): {text[:100]}...")
                                yield text
                                return
                    
                    # Try final_response path
                    if "final_response" in snapshot_data[1]:
                        final_vars = snapshot_data[1]["final_response"].get("variables", {})
                        nodes = final_vars.get("nodes", {})
                        if "agent_0" in nodes:
                            text = nodes["agent_0"].get("text", "")
                            if text:
                                logger.info(f"Yielding from STATE_SNAPSHOT (final_response): {text[:100]}...")
                                yield text
                                return
            
            # If still nothing, yield a default message
            if text_deltas_count == 0 and not state_snapshot:
                logger.warning("Could not extract any text from Leo streaming response")
                yield "I processed your request, but couldn't extract a response."
            
        except requests.exceptions.Timeout:
            logger.error("Leo API request timed out")
            raise RuntimeError("Leo API request timed out after 120 seconds")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Leo API: {e}")
            raise RuntimeError(f"Could not connect to Leo API: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error in streaming call to Leo API: {e}", exc_info=True)
            raise RuntimeError(f"Leo API streaming error: {e}")
