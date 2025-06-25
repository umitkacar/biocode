import asyncio
from typing import Dict, Any, Optional, List, Set
import jwt
import hashlib
from datetime import datetime, timedelta
import os

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.codecell_example import CodeCell
from src.core.advanced_codetissue import AdvancedCodeTissue


class LoginCell(CodeCell):
    """Kullanıcı giriş işlemleri için specialized cell"""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.db_connection = kwargs.get('db_connection')
        self.max_attempts = 3
        self.lockout_duration = timedelta(minutes=15)
        self.failed_attempts: Dict[str, int] = {}
        
    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """Kullanıcı doğrulama"""
        try:
            # Check lockout
            if self._is_locked_out(username):
                raise Exception(f"Account locked for {username}")
                
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Simulate DB check - In production, use proper DB with hashed passwords
            # This is just for demo purposes
            demo_users = {
                "demo_user": hashlib.sha256("demo_pass".encode()).hexdigest(),
                "test_admin": hashlib.sha256("test_admin_pass".encode()).hexdigest()
            }
            
            if username in demo_users and password_hash == demo_users[username]:
                self.failed_attempts.pop(username, None)
                return {
                    'success': True,
                    'user_id': hashlib.md5(username.encode()).hexdigest()[:8],
                    'username': username,
                    'roles': ['admin', 'user'] if 'admin' in username else ['user']
                }
            else:
                self._record_failed_attempt(username)
                return {'success': False, 'reason': 'Invalid credentials'}
                
        except Exception as e:
            self.infect(e)
            raise
            
    def _is_locked_out(self, username: str) -> bool:
        return self.failed_attempts.get(username, 0) >= self.max_attempts
        
    def _record_failed_attempt(self, username: str):
        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
        
    async def receive_signal(self, signal: Any):
        """LoginCell'e gelen sinyalleri işle"""
        if signal.get('type') == 'reset_attempts':
            username = signal.get('username')
            if username:
                self.failed_attempts.pop(username, None)


class TokenCell(CodeCell):
    """JWT token yönetimi için specialized cell"""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.secret_key = kwargs.get('secret_key', os.environ.get('JWT_SECRET_KEY', os.urandom(32).hex()))
        self.token_expiry = timedelta(hours=1)
        self.refresh_expiry = timedelta(days=7)
        self.active_tokens: Set[str] = set()
        
    async def generate_token(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """JWT token üret"""
        try:
            now = datetime.utcnow()
            
            # Access token
            access_payload = {
                'user_id': user_data['user_id'],
                'username': user_data['username'],
                'roles': user_data['roles'],
                'exp': now + self.token_expiry,
                'iat': now,
                'type': 'access'
            }
            
            # Refresh token
            refresh_payload = {
                'user_id': user_data['user_id'],
                'exp': now + self.refresh_expiry,
                'iat': now,
                'type': 'refresh'
            }
            
            access_token = jwt.encode(access_payload, self.secret_key, algorithm='HS256')
            refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm='HS256')
            
            self.active_tokens.add(access_token)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': self.token_expiry.total_seconds()
            }
            
        except Exception as e:
            self.infect(e)
            raise
            
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Token doğrula"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            if token not in self.active_tokens and payload.get('type') == 'access':
                raise jwt.InvalidTokenError("Token not active")
                
            return payload
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'reason': 'Token expired'}
        except jwt.InvalidTokenError as e:
            self.infect(e)
            return {'valid': False, 'reason': str(e)}
            
    async def revoke_token(self, token: str):
        """Token'ı iptal et"""
        self.active_tokens.discard(token)
        
    async def receive_signal(self, signal: Any):
        """TokenCell'e gelen sinyalleri işle"""
        if signal.get('type') == 'revoke_all':
            user_id = signal.get('user_id')
            # Kullanıcının tüm token'larını iptal et
            self.active_tokens.clear()  # Simplified for demo


class PermissionCell(CodeCell):
    """Yetki kontrolü için specialized cell"""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.permissions_db = {
            'admin': ['read', 'write', 'delete', 'admin'],
            'user': ['read', 'write'],
            'guest': ['read']
        }
        
    async def check_permission(self, user_roles: List[str], required_permission: str) -> bool:
        """Yetki kontrolü"""
        try:
            user_permissions = set()
            
            for role in user_roles:
                permissions = self.permissions_db.get(role, [])
                user_permissions.update(permissions)
                
            return required_permission in user_permissions
            
        except Exception as e:
            self.infect(e)
            return False
            
    async def get_user_permissions(self, user_roles: List[str]) -> List[str]:
        """Kullanıcının tüm yetkilerini getir"""
        permissions = set()
        
        for role in user_roles:
            perms = self.permissions_db.get(role, [])
            permissions.update(perms)
            
        return list(permissions)


async def authentication_tissue_demo():
    """Authentication Tissue Demo"""
    print("🧬 Authentication Tissue Demo Starting...")
    
    # Tissue oluştur
    auth_tissue = AdvancedCodeTissue("AuthenticationTissue")
    
    # Cell tiplerini kaydet
    auth_tissue.cell_types['LoginCell'] = LoginCell
    auth_tissue.cell_types['TokenCell'] = TokenCell
    auth_tissue.cell_types['PermissionCell'] = PermissionCell
    
    # Dependencies inject et
    auth_tissue.inject_dependency('secret_key', os.environ.get('AUTH_SECRET_KEY', os.urandom(32).hex()))
    auth_tissue.inject_dependency('db_connection', 'mock_db_connection')
    
    # Cell'leri grow et
    login_cell = auth_tissue.grow_cell("main_login", "LoginCell")
    token_cell = auth_tissue.grow_cell("jwt_handler", "TokenCell")
    perm_cell = auth_tissue.grow_cell("permission_checker", "PermissionCell")
    
    # Cell'leri bağla
    auth_tissue.connect_cells("main_login", "jwt_handler")
    auth_tissue.connect_cells("jwt_handler", "permission_checker")
    
    print("\n✅ Tissue Created Successfully!")
    print(f"Active Cells: {len(auth_tissue.cells)}")
    
    # Test authentication flow
    print("\n🔐 Testing Authentication Flow...")
    
    # 1. Login attempt
    login_result = await login_cell.authenticate("test_admin", "test_admin_pass")
    print(f"Login Result: {login_result}")
    
    if login_result['success']:
        # 2. Generate token
        token_result = await token_cell.generate_token(login_result)
        print(f"\nToken Generated: {token_result['access_token'][:50]}...")
        
        # 3. Verify token
        verify_result = await token_cell.verify_token(token_result['access_token'])
        print(f"\nToken Verification: Valid={verify_result.get('username') is not None}")
        
        # 4. Check permissions
        can_delete = await perm_cell.check_permission(verify_result['roles'], 'delete')
        print(f"Can Delete: {can_delete}")
        
        user_perms = await perm_cell.get_user_permissions(verify_result['roles'])
        print(f"User Permissions: {user_perms}")
    
    # Test error handling
    print("\n🦠 Testing Error Handling...")
    
    # Failed login attempts
    for i in range(4):
        try:
            result = await login_cell.authenticate("hacker", "wrong")
            print(f"Attempt {i+1}: {result}")
        except Exception as e:
            print(f"Attempt {i+1}: Locked - {e}")
    
    # Check tissue health
    print("\n📊 Tissue Diagnostics:")
    diagnostics = auth_tissue.get_tissue_diagnostics()
    print(f"Health Score: {diagnostics['metrics']['health_score']:.1f}")
    print(f"Infected Cells: {diagnostics['metrics']['infected_cells']}")
    print(f"Cell States: {diagnostics['cell_states']}")
    
    # Test transaction
    print("\n💱 Testing Transaction...")
    
    try:
        with auth_tissue.transaction("user_logout") as tx:
            # Simulate logout operations
            tx.affected_cells.add("main_login")
            tx.affected_cells.add("jwt_handler")
            
            # Clear user session
            await auth_tissue.send_signal("main_login", "jwt_handler", 
                                        {'type': 'revoke_all', 'user_id': '123'})
            
            print("Transaction completed successfully")
            
    except Exception as e:
        print(f"Transaction failed: {e}")
    
    print("\n✨ Demo Completed!")


if __name__ == "__main__":
    asyncio.run(authentication_tissue_demo())