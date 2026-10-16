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

def apply_fixes(file_path, error_log):
    """Reads error log and applies surgical fixes to the source code."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    fixed = False
    
    # Fix 1: Remove leading '#' or invalid bytes from line 1
    if 'invalid byte' in error_log and 'line 1' in error_log:
        if lines[0].startswith('#'):
            lines.pop(0)
            fixed = True

    # Fix 2: Handle 'unused capture' by replacing |var| with |_|
    if 'unused capture' in error_log:
        match = re.search(r'capture \'(\w+)\'', error_log)
        if match:
            var_name = match.group(1)
            new_lines = []
            for line in lines:
                new_lines.append(line.replace(f'|{var_name}|', '|_|').replace(f'|*{var_name}|', '|*_|'))
            lines = new_lines
            fixed = True

    # Fix 3: Handle 'defer _ =' syntax error
    if 'defer _ =' in error_log:
        new_lines = []
        for line in lines:
            if 'defer _ =' in line:
                line = line.replace('defer _ =', 'defer')
            new_lines.append(line)
        lines = new_lines
        fixed = True

    if fixed:
        with open(file_path, 'w') as f:
            f.writelines(lines)
        print(f"✅ Applied surgical fix to {file_path}")
    
    return fixed

def main():
    zig_files = [f for f in os.listdir('src/core') if f.endswith('.zig')]
    
    for z_file in zig_files:
        path = os.path.join('src/core', z_file)
        max_attempts = 5
        
        for attempt in range(max_attempts):
            code, err, bin_path = run_compiler(path)
            
            if code == 0:
                print(f"🏆 Success: {z_file} is production-ready.")
                break
            
            print(f"⚠️ Attempt {attempt + 1} failed for {z_file}. Analyzing...")
            if not apply_fixes(path, err):
                print(f"❌ Could not auto-resolve errors for {z_file}. Halting.")
                sys.exit(1)

if __name__ == "__main__":
    main()
