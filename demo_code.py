#!/usr/bin/env python3
"""
Demo Python file for testing LSP integration.
Contains functions and classes to test go-to-definition, find-references, and hover.
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class User:
    """User entity with authentication capabilities."""
    id: int
    name: str
    email: str
    is_active: bool = True


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class UserService:
    """Service for managing user operations and authentication."""
    
    def __init__(self):
        self.users: List[User] = []
        self.current_user: Optional[User] = None
    
    def authenticate(self, email: str, password: str) -> User:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Authenticated User object
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Mock authentication logic
        user = self.find_user_by_email(email)
        if not user:
            raise AuthenticationError(f"User not found: {email}")
        
        # In real implementation, verify password hash
        if password == "wrong":
            raise AuthenticationError("Invalid password")
        
        self.current_user = user
        return user
    
    def find_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email address."""
        return next((user for user in self.users if user.email == email), None)
    
    def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        user = User(
            id=len(self.users) + 1,
            name=name,
            email=email
        )
        self.users.append(user)
        return user


def main():
    """Main function demonstrating user service usage."""
    service = UserService()
    
    # Create users
    user1 = service.create_user("Alice", "alice@example.com")
    user2 = service.create_user("Bob", "bob@example.com")
    
    # Authenticate user
    try:
        authenticated_user = service.authenticate("alice@example.com", "password123")
        print(f"Authenticated: {authenticated_user.name}")
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")


if __name__ == "__main__":
    main()