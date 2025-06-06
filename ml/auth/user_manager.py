import sqlite3
import bcrypt
from typing import Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path

class UserManager:
    def __init__(self, db_path: str = "data/users.db"):
        """Initialize UserManager with database path."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database and create users table if it doesn't exist."""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            conn.commit()
    
    def register_user(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            name: User's full name
            email: User's email address
            password: User's password (will be hashed)
            
        Returns:
            Dict containing user data or error message
        """
        try:
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash)
                    VALUES (?, ?, ?)
                """, (name, email, password_hash.decode('utf-8')))
                conn.commit()
                
                # Get the created user
                cursor.execute("""
                    SELECT id, name, email, created_at
                    FROM users
                    WHERE email = ?
                """, (email,))
                user = cursor.fetchone()
                
                return {
                    "status": "success",
                    "user": {
                        "id": user[0],
                        "name": user[1],
                        "email": user[2],
                        "created_at": user[3]
                    }
                }
        except sqlite3.IntegrityError:
            return {
                "status": "error",
                "message": "Email already registered"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dict containing user data or error message
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, email, password_hash, created_at
                    FROM users
                    WHERE email = ? AND is_active = TRUE
                """, (email,))
                user = cursor.fetchone()
                
                if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                    # Update last login
                    cursor.execute("""
                        UPDATE users
                        SET last_login = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (user[0],))
                    conn.commit()
                    
                    return {
                        "status": "success",
                        "user": {
                            "id": user[0],
                            "name": user[1],
                            "email": user[2],
                            "created_at": user[4]
                        }
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Invalid email or password"
                    }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user details by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict containing user data or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, email, created_at, last_login
                    FROM users
                    WHERE id = ? AND is_active = TRUE
                """, (user_id,))
                user = cursor.fetchone()
                
                if user:
                    return {
                        "id": user[0],
                        "name": user[1],
                        "email": user[2],
                        "created_at": user[3],
                        "last_login": user[4]
                    }
                return None
        except Exception:
            return None
    
    def update_user(self, user_id: int, name: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Update user details.
        
        Args:
            user_id: User's ID
            name: New name (optional)
            email: New email (optional)
            
        Returns:
            Dict containing updated user data or error message
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query based on provided fields
                update_fields = []
                params = []
                
                if name is not None:
                    update_fields.append("name = ?")
                    params.append(name)
                
                if email is not None:
                    update_fields.append("email = ?")
                    params.append(email)
                
                if not update_fields:
                    return {
                        "status": "error",
                        "message": "No fields to update"
                    }
                
                # Add user_id to params
                params.append(user_id)
                
                # Execute update
                cursor.execute(f"""
                    UPDATE users
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, params)
                conn.commit()
                
                # Get updated user
                return self.get_user(user_id)
        except sqlite3.IntegrityError:
            return {
                "status": "error",
                "message": "Email already registered"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user's password.
        
        Args:
            user_id: User's ID
            current_password: Current password
            new_password: New password
            
        Returns:
            Dict containing success/error message
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT password_hash
                    FROM users
                    WHERE id = ? AND is_active = TRUE
                """, (user_id,))
                result = cursor.fetchone()
                
                if result and bcrypt.checkpw(current_password.encode('utf-8'), result[0].encode('utf-8')):
                    # Hash new password
                    new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    
                    # Update password
                    cursor.execute("""
                        UPDATE users
                        SET password_hash = ?
                        WHERE id = ?
                    """, (new_password_hash.decode('utf-8'), user_id))
                    conn.commit()
                    
                    return {
                        "status": "success",
                        "message": "Password updated successfully"
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Current password is incorrect"
                    }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def deactivate_user(self, user_id: int) -> Dict[str, Any]:
        """
        Deactivate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict containing success/error message
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users
                    SET is_active = FALSE
                    WHERE id = ?
                """, (user_id,))
                conn.commit()
                
                return {
                    "status": "success",
                    "message": "Account deactivated successfully"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            } 