"""
AgentID Python SDK - Email Verification Flow Example

This example demonstrates how an agent can autonomously complete
email verification flows for service signups.

Workflow:
1. Create agent with email identity
2. Sign up for target service
3. Wait for verification email
4. Extract verification link
5. Complete verification
"""

import re
import time
from typing import Optional
from agentid import AgentID


class EmailVerificationAgent:
    """Agent that can handle email verification flows autonomously."""
    
    def __init__(self, agent_id: str, email_address: str):
        """
        Initialize verification agent.
        
        Args:
            agent_id: AgentID agent identifier
            email_address: Agent's email address
        """
        self.client = AgentID()
        self.agent_id = agent_id
        self.email_address = email_address
    
    def signup_and_verify(
        self,
        service_name: str,
        signup_url: str,
        signup_data: dict,
        sender_domain: str,
        timeout: int = 300
    ) -> bool:
        """
        Complete signup and email verification flow.
        
        Args:
            service_name: Name of service for logging
            signup_url: Service signup endpoint
            signup_data: Signup form data (excluding email)
            sender_domain: Expected sender domain for verification email
            timeout: Max seconds to wait for verification email
            
        Returns:
            True if verification successful, False otherwise
        """
        print(f"🚀 Starting signup for {service_name}...")
        
        # 1. Sign up for service
        print(f"📝 Submitting signup form...")
        import requests
        
        signup_data['email'] = self.email_address
        response = requests.post(signup_url, json=signup_data)
        
        if response.status_code != 200:
            print(f"❌ Signup failed: {response.status_code}")
            return False
        
        print(f"✓ Signup successful")
        
        # 2. Wait for verification email
        print(f"📧 Waiting for verification email from {sender_domain}...")
        verification_link = self._wait_for_verification_email(
            sender_domain=sender_domain,
            timeout=timeout
        )
        
        if not verification_link:
            print(f"❌ Verification email not received within {timeout}s")
            return False
        
        print(f"✓ Verification link received: {verification_link[:50]}...")
        
        # 3. Click verification link
        print(f"🔗 Clicking verification link...")
        response = requests.get(verification_link)
        
        if response.status_code != 200:
            print(f"❌ Verification failed: {response.status_code}")
            return False
        
        print(f"✅ Verification successful!")
        return True
    
    def _wait_for_verification_email(
        self,
        sender_domain: str,
        timeout: int
    ) -> Optional[str]:
        """
        Poll for verification email and extract link.
        
        Args:
            sender_domain: Expected sender domain
            timeout: Max seconds to wait
            
        Returns:
            Verification link or None if not found
        """
        start_time = time.time()
        last_check = None
        
        while time.time() - start_time < timeout:
            # Fetch recent messages
            messages = self.client.messages.list_email(
                agent_id=self.agent_id,
                since=last_check,
                limit=10
            )
            
            # Check each message
            for msg in messages.data:
                if sender_domain in msg.from_address:
                    # Retrieve full message body
                    full_message = self.client.messages.get_email(msg.id)
                    
                    # Extract verification link
                    link = self._extract_verification_link(full_message.body_plain)
                    if link:
                        return link
            
            # Update last check timestamp
            if messages.data:
                last_check = messages.data[0].received_at
            
            # Wait before next poll
            time.sleep(5)
        
        return None
    
    def _extract_verification_link(self, body: str) -> Optional[str]:
        """
        Extract verification link from email body.
        
        Args:
            body: Email body text
            
        Returns:
            Verification link or None if not found
        """
        # Common verification link patterns
        patterns = [
            r'https?://[^\s]+/verify[^\s]*',
            r'https?://[^\s]+/confirm[^\s]*',
            r'https?://[^\s]+/activate[^\s]*',
            r'https?://[^\s]+/email-verification[^\s]*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                # Clean up common trailing characters
                link = match.group(0).rstrip('.,;:)')
                return link
        
        return None


# Example usage
if __name__ == '__main__':
    import os
    
    # Initialize client
    client = AgentID(api_key=os.environ['AGENTID_API_KEY'])
    
    # Create agent
    agent = client.agents.create(
        name="EmailVerificationBot",
        description="Autonomously handles email verification flows"
    )
    
    # Provision email
    email = client.identities.create_email(
        agent_id=agent.id,
        domain="agentid.io"
    )
    
    print(f"Agent email: {email.address}")
    
    # Create verification agent
    verification_agent = EmailVerificationAgent(
        agent_id=agent.id,
        email_address=email.address
    )
    
    # Complete signup and verification
    success = verification_agent.signup_and_verify(
        service_name="Example SaaS",
        signup_url="https://example.com/api/signup",
        signup_data={
            "name": "Test Agent",
            "company": "AgentID"
        },
        sender_domain="example.com",
        timeout=300
    )
    
    if success:
        print("\n✅ Agent successfully signed up and verified!")
    else:
        print("\n❌ Verification flow failed")
