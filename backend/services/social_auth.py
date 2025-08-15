import os
import httpx
from typing import Optional, Dict, Any
import logging
from google.auth.transport import requests
from google.oauth2 import id_token

logger = logging.getLogger(__name__)

class SocialAuthService:
    def __init__(self):
        # Google OAuth
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        
        # Facebook OAuth
        self.facebook_client_id = os.getenv("FACEBOOK_CLIENT_ID")
        self.facebook_client_secret = os.getenv("FACEBOOK_CLIENT_SECRET")

    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token and return user info"""
        try:
            if not self.google_client_id:
                logger.warning("Google client ID not configured")
                return None

            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), self.google_client_id
            )

            # Extract user information
            user_info = {
                "email": idinfo.get("email"),
                "name": idinfo.get("name"),
                "given_name": idinfo.get("given_name"),
                "family_name": idinfo.get("family_name"),
                "picture": idinfo.get("picture"),
                "provider": "google",
                "provider_id": idinfo.get("sub")
            }
            
            return user_info
        except Exception as e:
            logger.error(f"Google token verification failed: {e}")
            return None

    async def verify_facebook_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Facebook access token and return user info"""
        try:
            if not self.facebook_client_id or not self.facebook_client_secret:
                logger.warning("Facebook credentials not configured")
                return None

            # Verify token with Facebook
            async with httpx.AsyncClient() as client:
                # First, verify the token
                verify_url = f"https://graph.facebook.com/debug_token"
                verify_params = {
                    "input_token": token,
                    "access_token": f"{self.facebook_client_id}|{self.facebook_client_secret}"
                }
                
                verify_response = await client.get(verify_url, params=verify_params)
                verify_data = verify_response.json()
                
                if not verify_data.get("data", {}).get("is_valid"):
                    logger.error("Invalid Facebook token")
                    return None

                # Get user information
                user_url = "https://graph.facebook.com/me"
                user_params = {
                    "access_token": token,
                    "fields": "id,name,email,first_name,last_name,picture"
                }
                
                user_response = await client.get(user_url, params=user_params)
                user_data = user_response.json()
                
                if "error" in user_data:
                    logger.error(f"Facebook API error: {user_data['error']}")
                    return None

                user_info = {
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "given_name": user_data.get("first_name"),
                    "family_name": user_data.get("last_name"),
                    "picture": user_data.get("picture", {}).get("data", {}).get("url"),
                    "provider": "facebook",
                    "provider_id": user_data.get("id")
                }
                
                return user_info
        except Exception as e:
            logger.error(f"Facebook token verification failed: {e}")
            return None

    async def verify_instagram_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Instagram access token and return user info"""
        try:
            # Instagram uses Facebook's Graph API
            async with httpx.AsyncClient() as client:
                # Get user information from Instagram Basic Display API
                user_url = "https://graph.instagram.com/me"
                user_params = {
                    "access_token": token,
                    "fields": "id,username"
                }
                
                user_response = await client.get(user_url, params=user_params)
                user_data = user_response.json()
                
                if "error" in user_data:
                    logger.error(f"Instagram API error: {user_data['error']}")
                    return None

                user_info = {
                    "email": None,  # Instagram doesn't provide email through Basic Display API
                    "name": user_data.get("username"),
                    "given_name": user_data.get("username"),
                    "family_name": None,
                    "picture": None,
                    "provider": "instagram",
                    "provider_id": user_data.get("id"),
                    "username": user_data.get("username")
                }
                
                return user_info
        except Exception as e:
            logger.error(f"Instagram token verification failed: {e}")
            return None

    async def verify_apple_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Apple ID token and return user info"""
        try:
            # Apple Sign-In uses JWT tokens
            # This is a simplified implementation - in production, you'd want to:
            # 1. Verify the JWT signature using Apple's public keys
            # 2. Validate the token's claims (issuer, audience, expiration)
            
            import jwt
            
            # For demo purposes, we'll decode without verification
            # In production, implement proper JWT verification
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            user_info = {
                "email": decoded.get("email"),
                "name": decoded.get("name"),
                "given_name": decoded.get("given_name"),
                "family_name": decoded.get("family_name"),
                "picture": None,
                "provider": "apple",
                "provider_id": decoded.get("sub")
            }
            
            return user_info
        except Exception as e:
            logger.error(f"Apple token verification failed: {e}")
            return None

    async def authenticate_social_user(self, provider: str, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with social provider"""
        if provider == "google":
            return await self.verify_google_token(token)
        elif provider == "facebook":
            return await self.verify_facebook_token(token)
        elif provider == "instagram":
            return await self.verify_instagram_token(token)
        elif provider == "apple":
            return await self.verify_apple_token(token)
        else:
            logger.error(f"Unsupported social provider: {provider}")
            return None

# Global social auth service instance
social_auth_service = SocialAuthService()