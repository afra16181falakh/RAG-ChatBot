"""
Fix SQLite version compatibility for ChromaDB on Streamlit Cloud
This script ensures we use the newer SQLite version from pysqlite3-binary
"""
import sys
import os

def fix_sqlite_version():
    """Replace the system sqlite3 with pysqlite3 to ensure compatibility with ChromaDB"""
    try:
        # Import pysqlite3 and replace system sqlite3
        import pysqlite3
        sys.modules['sqlite3'] = pysqlite3
        print("✅ Successfully loaded pysqlite3 for ChromaDB compatibility")
    except ImportError:
        print("⚠️ pysqlite3 not available, using system sqlite3")
        pass

# Apply the fix immediately when this module is imported
fix_sqlite_version()
