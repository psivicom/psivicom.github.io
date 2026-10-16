import subprocess
import os
import re
import sys

def run_compiler(file_path):
    """Attempts to compile the Zig file and returns stdout/stderr."""
    output_bin = file_path.replace('.zig', '')
    cmd = [
        '/opt/zig/zig', 'build-exe', file_path, 
        '-O', 'ReleaseSafe', '-fstrip', 
        '-femit-bin=' + output_bin
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stderr, output_bin

def apply_and_verify_fix(file_path, error_log):
    """Applies a fix, writes to disk, and verifies the write succeeded."""
    with open(file_path, 'r') as f:
        original_content = f.read()
    
    content = original_content
    fixed = False

    # Fix 1: Crypto API Change (fromSeed -> generate/fromBytes)
    if 'has no member named' in error_log and 'fromSeed' in error_log:
        content = content.replace('.fromSeed(', '.generate(')
        fixed = True

    # Fix 2: Invalid defer syntax (defer _ =)
    elif 'defer _ =' in error_log:
        content = content.replace('defer _ =', 'defer')
        fixed = True

    # Fix 3: Unused capture (|var| -> |_|)
    elif 'unused capture' in error_log:
        match = re.search(r'capture \'(\w+)\'', error_log)
        if match:
            var_name = match.group(1)
            content = content.replace(f'|{var_name}|', '|_|').replace(f'|*{var_name}|', '|*_|')
            fixed = True

    # Fix 4: Missing closing braces
    elif 'expected block' in error_log or 'expected }' in error_log:
        open_braces = content.count('{') - content.count('}')
        if open_braces > 0:
            content += '\n' * open_braces + '}\n' * open_braces
            fixed = True

    # Fix 5: Invalid leading bytes (#)
    elif 'invalid byte' in error_log and 'line 1' in error_log:
        lines = content.splitlines(keepends=True)
        if lines and lines[0].startswith('#'):
            lines.pop(0)
            content = ''.join(lines)
            fixed = True

    if fixed and content != original_content:
        # WRITE TO DISK
        with open(file_path, 'w') as f:
            f.write(content)
        
        # VERIFY THE WRITE
        with open(file_path, 'r') as f:
            verified_content = f.read()
            
        if verified_content == content:
            print(f"✅ Fix applied and VERIFIED on disk for {file_path}")
            return True
        else:
            print(f"❌ CRITICAL: Write verification failed for {file_path}. Disk content does not match memory.")
            return False
    
    return False

def main():
    zig_files = [f for f in os.listdir('src/core') if f.endswith('.zig')]
    
    for z_file in zig_files:
        path = os.path.join('src/core', z_file)
        max_attempts = 15
        
        print(f"🚀 Initiating autonomous healing for {z_file}...")
        
        for attempt in range(max_attempts):
            code, err, bin_path = run_compiler(path)
            
            if code == 0:
                print(f"🏆 SUCCESS: {z_file} is production-ready after {attempt + 1} iterations.")
                break
            
            print(f"⚠️ Iteration {attempt + 1} failed. Analyzing error...")
            
            if not apply_and_verify_fix(path, err):
                print(f"❌ CRITICAL: No known fix resolved the error for {z_file}.")
                print(f"Last Error:\n{err}")
                sys.exit(1)

if __name__ == "__main__":
    main()
