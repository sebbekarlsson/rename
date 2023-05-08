import re
import os
import pathlib
import shutil

def get_extension(filename):
    return pathlib.Path(filename).suffix


BINARY_EXTS = [
    '.pyc',
    '.out',
    '.bin',
    '.dll',
    '.so',
    '.a',
    '.png',
    '.jpeg',
    '.jpg',
    '.bmp',
    '.gif',
    '.webm',
    '.webmp',
    '.o'
]

def is_dir(fname):
    return os.path.isdir(fname) or pathlib.Path(fname).is_dir()

def is_binary(filename):
    if is_dir(filename):
        return False
    
    # Emacs files
    if '#' in filename or '~' in filename:
        return True
    
    ext = get_extension(filename)

    if not ext:
        return True
    
    if ext.lower() in BINARY_EXTS:
        return True
    
    f = open(filename, 'rb')
    try:
        chunk_size = 256
        while True:
            chunk = f.read(chunk_size)
            if b'\0' in chunk:
                return True
            if len(chunk) < chunk_size:
                break
    finally:
        f.close()


SKIP_PATTERNS = [
    'venv/',
    'cache/',
    '.egg',
    'dist/',
    '.git/',
    'build/'
]

def should_skip(filename):
    for skip in SKIP_PATTERNS:
       if skip in filename.lower():
           return True

    if is_binary(filename):
        return True

    return False
        
def _replace_icase(match, old_name, new_name):
    if match.group().isupper():
        return new_name.upper()
    elif match.group().islower():
        return new_name.lower()
    elif match.group().istitle():
        return new_name.title()
    else:
        return new_name

def replace_icase(content, old_name, new_name):
    regex = re.compile(re.escape(old_name), re.IGNORECASE)
    return regex.sub(lambda match: _replace_icase(match, old_name, new_name), content)


def replace_contents(filepath, old_name, new_name, dry=False):
    f = open(filepath, 'r')
    contents = f.read()
    f.close()

    if old_name.lower() not in contents.lower():
        return False
    
    new_contents = replace_icase(contents, old_name, new_name)

    print(f'replace contents inside {filepath}')
    
    if not dry:
        f = open(filepath, 'w')
        f.write(new_contents)
        f.close()

    return True
    
def replace_filename(filename, old_name, new_name, dry=False):
    if old_name.lower() not in filename.lower():
        return False

    p = pathlib.Path(filename)
    if not p.parts or len(p.parts) <= 0:
        return False
    
    last = p.parts[-1]

    if not old_name.lower() in last.lower():
        return False
    
    new_last = replace_icase(last, old_name, new_name)
    new_name = os.path.join(*[*p.parts[:-1], new_last])

    print(f'move {filename} => {new_name}')
    
    if not dry:
        shutil.move(filename, new_name)

    return True


def is_leaf(path):
    if not is_dir(path) or path.count('/') <= 0:
        return True

    for i, data in enumerate(os.walk(path)):
        dirpath, dirnames, filenames = data
        if i > 0 and is_dir(dirpath):
            return False
        
    return True


def rename_project_(path, old_name, new_name, dry=False):
    # replace contents
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            
            if not should_skip(fullpath) and is_leaf(fullpath):
                replace_contents(fullpath, old_name, new_name, dry)

    # move directories
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        if not should_skip(dirpath) and is_leaf(dirpath):
            replace_filename(dirpath, old_name, new_name, dry) 

    # move files
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            
            if not should_skip(fullpath) and is_leaf(fullpath) and old_name.lower() in filename.lower():
                replace_filename(fullpath, old_name, new_name, dry)
    return True

    
def rename_project(path, old_name, new_name, dry=False):
    return rename_project_(path, old_name, new_name, dry)
    
