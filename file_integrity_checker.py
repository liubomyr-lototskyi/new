#!/usr/bin/env python3
rized modifications, additions, or deletions.
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class FileIntegrityChecker:
    def __init__(self, db_file="integrity_db.json"):
        self.db_file = db_file
        self.database = self._load_database()
    
    def _load_database(self):
        """Load the integrity database from file."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Corrupt database file. Starting fresh.")
                return {}
        return {}
    
    def _save_database(self):
        """Save the integrity database to file."""
        with open(self.db_file, 'w') as f:
            json.dump(self.database, f, indent=2)
    
    def _calculate_hash(self, filepath):
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def add_files(self, paths):
        """Add files or directories to monitoring."""
        added_count = 0
        for path in paths:
            path_obj = Path(path)
            if path_obj.is_file():
                if self._add_file(path_obj):
                    added_count += 1
            elif path_obj.is_dir():
                for file_path in path_obj.rglob('*'):
                    if file_path.is_file():
                        if self._add_file(file_path):
                            added_count += 1
            else:
                print(f"Warning: {path} not found")
        
        self._save_database()
        print(f"\n✓ Added {added_count} file(s) to monitoring")
        return added_count
    
    def _add_file(self, filepath):
        """Add a single file to the database."""
        file_str = str(filepath.absolute())
        file_hash = self._calculate_hash(file_str)
        
        if file_hash:
            file_stat = os.stat(file_str)
            self.database[file_str] = {
                "hash": file_hash,
                "size": file_stat.st_size,
                "modified": file_stat.st_mtime,
                "added_date": datetime.now().isoformat()
            }
            print(f"Added: {filepath.name}")
            return True
        return False
    
    def check_integrity(self):
        """Check integrity of all monitored files."""
        if not self.database:
            print("No files are being monitored. Use 'add' command first.")
            return
        
        print(f"\nChecking integrity of {len(self.database)} file(s)...\n")
        
        modified = []
        deleted = []
        intact = []
        
        for filepath, stored_data in self.database.items():
            if not os.path.exists(filepath):
                deleted.append(filepath)
                print(f"⚠ DELETED: {filepath}")
            else:
                current_hash = self._calculate_hash(filepath)
                if current_hash != stored_data["hash"]:
                    modified.append(filepath)
                    print(f"⚠ MODIFIED: {filepath}")
                    print(f"  Original hash: {stored_data['hash'][:16]}...")
                    print(f"  Current hash:  {current_hash[:16]}...")
                else:
                    intact.append(filepath)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"INTEGRITY CHECK SUMMARY")
        print(f"{'='*60}")
        print(f"✓ Intact:   {len(intact)} file(s)")
        print(f"⚠ Modified: {len(modified)} file(s)")
        print(f"⚠ Deleted:  {len(deleted)} file(s)")
        print(f"{'='*60}\n")
        
        if not modified and not deleted:
            print("All monitored files are intact! ✓")
    
    def list_files(self):
        """List all monitored files."""
        if not self.database:
            print("No files are being monitored.")
            return
        
        print(f"\nMonitored Files ({len(self.database)}):\n")
        for filepath, data in self.database.items():
            print(f"📄 {filepath}")
            print(f"   Hash: {data['hash'][:32]}...")
            print(f"   Size: {data['size']} bytes")
            print(f"   Added: {data['added_date'][:19]}")
            print()
    
    def remove_files(self, paths):
        """Remove files from monitoring."""
        removed_count = 0
        for path in paths:
            abs_path = str(Path(path).absolute())
            if abs_path in self.database:
                del self.database[abs_path]
                removed_count += 1
                print(f"Removed: {path}")
            else:
                print(f"Not monitored: {path}")
        
        self._save_database()
        print(f"\n✓ Removed {removed_count} file(s) from monitoring")
    
    def update_baseline(self, paths=None):
        """Update baseline hashes for specified files or all files."""
        if paths:
            updated_count = 0
            for path in paths:
                abs_path = str(Path(path).absolute())
                if abs_path in self.database and os.path.exists(abs_path):
                    new_hash = self._calculate_hash(abs_path)
                    file_stat = os.stat(abs_path)
                    self.database[abs_path]["hash"] = new_hash
                    self.database[abs_path]["size"] = file_stat.st_size
                    self.database[abs_path]["modified"] = file_stat.st_mtime
                    updated_count += 1
                    print(f"Updated: {path}")
            self._save_database()
            print(f"\n✓ Updated {updated_count} file(s)")
        else:
            # Update all
            updated_count = 0
            for filepath in list(self.database.keys()):
                if os.path.exists(filepath):
                    new_hash = self._calculate_hash(filepath)
                    file_stat = os.stat(filepath)
                    self.database[filepath]["hash"] = new_hash
                    self.database[filepath]["size"] = file_stat.st_size
                    self.database[filepath]["modified"] = file_stat.st_mtime
                    updated_count += 1
            self._save_database()
            print(f"\n✓ Updated baseline for {updated_count} file(s)")


def print_usage():
    """Print usage information."""
    print("""
File Integrity Checker - Usage:

  python file_integrity_checker.py add <file/directory> [...]
      Add files or directories to monitoring
      
  python file_integrity_checker.py check
      Check integrity of all monitored files
      
  python file_integrity_checker.py list
      List all monitored files
      
  python file_integrity_checker.py remove <file> [...]
      Remove files from monitoring
      
  python file_integrity_checker.py update [file ...]
      Update baseline hash for files (all if none specified)

Examples:
  python file_integrity_checker.py add /etc/passwd /etc/shadow
  python file_integrity_checker.py add ~/important_docs/
  python file_integrity_checker.py check
  python file_integrity_checker.py update /etc/passwd
    """)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    checker = FileIntegrityChecker()
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Specify files or directories to add")
            sys.exit(1)
        checker.add_files(sys.argv[2:])
    
    elif command == "check":
        checker.check_integrity()
    
    elif command == "list":
        checker.list_files()
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Error: Specify files to remove")
            sys.exit(1)
        checker.remove_files(sys.argv[2:])
    
    elif command == "update":
        if len(sys.argv) > 2:
            checker.update_baseline(sys.argv[2:])
        else:
            checker.update_baseline()
    
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":

    main()

