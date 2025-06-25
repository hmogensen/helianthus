#!/usr/bin/env python3

import os
import shutil
import fnmatch
import argparse
from pathlib import Path

class GitIgnoreParser:
    def __init__(self, gitignore_path):
        self.patterns = []
        self.load_gitignore(gitignore_path)
    
    def load_gitignore(self, gitignore_path):
        if not os.path.exists(gitignore_path):
            return
        
        with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                self.patterns.append(line)
    
    def is_ignored(self, file_path, repo_root):
        try:
            rel_path = os.path.relpath(file_path, repo_root)
        except ValueError:
            return False
        
        rel_path = rel_path.replace(os.sep, '/')
        
        for pattern in self.patterns:
            negate = pattern.startswith('!')
            if negate:
                pattern = pattern[1:]
            
            if pattern.endswith('/'):
                pattern = pattern[:-1]
                if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.dirname(rel_path), pattern):
                    return not negate
            else:
                if (fnmatch.fnmatch(rel_path, pattern) or 
                    fnmatch.fnmatch(os.path.basename(rel_path), pattern) or
                    fnmatch.fnmatch(rel_path, f"*/{pattern}")):
                    return not negate
        
        return False

def copy_with_gitignore(src_dir, dest_dir):
    if not os.path.exists(src_dir):
        print(f"Warning: {src_dir} does not exist, skipping...")
        return
    
    gitignore_path = os.path.join(src_dir, '.gitignore')
    parser = GitIgnoreParser(gitignore_path)
    
    os.makedirs(dest_dir, exist_ok=True)
    
    copied_count = 0
    ignored_count = 0
    
    for root, dirs, files in os.walk(src_dir):
        rel_root = os.path.relpath(root, src_dir)
        if rel_root == '.':
            dest_root = dest_dir
        else:
            dest_root = os.path.join(dest_dir, rel_root)
        
        dirs_to_remove = []
        for d in dirs[:]:
            dir_path = os.path.join(root, d)
            if parser.is_ignored(dir_path, src_dir):
                dirs_to_remove.append(d)
                ignored_count += 1
        
        for d in dirs_to_remove:
            dirs.remove(d)
        
        if files:
            os.makedirs(dest_root, exist_ok=True)
        
        for file in files:
            src_file = os.path.join(root, file)
            if not parser.is_ignored(src_file, src_dir):
                dest_file = os.path.join(dest_root, file)
                try:
                    shutil.copy2(src_file, dest_file)
                    copied_count += 1
                except Exception as e:
                    print(f"Error copying {src_file}: {e}")
            else:
                ignored_count += 1
    
    print(f"Repository {os.path.basename(src_dir)}: {copied_count} files copied, {ignored_count} files/dirs ignored")

def copy_directory_simple(src_dir, dest_dir):
    if not os.path.exists(src_dir):
        print(f"Warning: {src_dir} does not exist, skipping...")
        return
    
    try:
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        shutil.copytree(src_dir, dest_dir)
        
        file_count = sum(len(files) for _, _, files in os.walk(dest_dir))
        print(f"Directory {os.path.basename(src_dir)}: {file_count} files copied")
    except Exception as e:
        print(f"Error copying {src_dir}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Backup script with git-aware copying')
    parser.add_argument('destination', help='Destination directory for backup')
    parser.add_argument('--home', default=os.path.expanduser('~'), 
                       help='Home directory path (default: current user home)')
    
    args = parser.parse_args()
    
    home_dir = args.home
    dest_dir = args.destination
    
    os.makedirs(dest_dir, exist_ok=True)
    
    print(f"Starting backup from {home_dir} to {dest_dir}")
    print("-" * 50)
    
    # Copy ~/settings and ~/data directories (simple copy)
    for dirname in ['settings', 'data']:
        src_path = os.path.join(home_dir, dirname)
        dest_path = os.path.join(dest_dir, dirname)
        print(f"Copying {dirname}...")
        copy_directory_simple(src_path, dest_path)
    
    # Handle ~/repos with git-aware copying
    repos_src = os.path.join(home_dir, 'repos')
    repos_dest = os.path.join(dest_dir, 'repos')
    
    if os.path.exists(repos_src):
        print("Processing repositories with .gitignore awareness...")
        os.makedirs(repos_dest, exist_ok=True)
        
        for item in os.listdir(repos_src):
            item_path = os.path.join(repos_src, item)
            if os.path.isdir(item_path):
                dest_repo_path = os.path.join(repos_dest, item)
                print(f"Processing repository: {item}")
                copy_with_gitignore(item_path, dest_repo_path)
    else:
        print("Warning: ~/repos directory does not exist, skipping...")
    
    print("-" * 50)
    print("Backup completed!")

if __name__ == "__main__":
    main()