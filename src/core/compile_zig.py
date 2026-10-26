#!/usr/bin/env python3
import os
import subprocess

def compile_zig_project():
    source_dir = "src/core"
    root_dir = os.path.dirname(os.path.abspath(__file__))
    full_source_path = os.path.join(root_dir, source_dir)

    if not os.path.exists(full_source_path):
        print(f"Error: Directory {source_dir} not found!")
        return

    # Get list of all .zig files
    zig_files = [f for f in os.listdir(full_source_path) if f.endswith('.zig')]
    
    if not zig_files:
        print(f"No Zig files found in {source_dir}!")
        return

    print(f"Starting sequential compilation of {len(zig_files)} files...\n")

    for filename in zig_files:
        # Setup paths for this specific file
        input_path = os.path.join(source_dir, filename)
        # Output binary name is the filename without .zig (e.g. test.zig -> test)
        output_name = filename.replace(".zig", "")
        output_path = os.path.join(source_dir, output_name)

        print(f"--- Processing: {filename} ---")
        
        # Command to compile ONLY this one file
        command = ["zig", "build-exe", input_path, "-o", output_path]

        try:
            # We use capture_output=True so the error doesn't flood the screen 
            # unless we choose to print it.
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Successfully compiled: {output_name}")
            else:
                # If the file refuses to compile, we print the error but the loop continues
                print(f"❌ Failed to compile {filename}:")
                print(result.stderr)
                print("Skipping to next file...\n")

        except Exception as e:
            print(f"⚠️ System error processing {filename}: {e}")

    print("\nSequential process complete.")

if __name__ == "__main__":
    compile_zig_project()
