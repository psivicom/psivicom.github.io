#!/usr/bin/env python3
import os
import subprocess

#!/usr/bin/env python3
import os
import subprocess

def compile_zig_project():
    # --- PATH LOGIC START ---
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # If the script is in src/core, the project root is two levels up
    # This ensures it works both on GitHub and locally
    root_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
    os.chdir(root_dir)
    
    source_dir = "src/core"
    full_source_path = os.path.join(root_dir, source_dir)
    # --- PATH LOGIC END ---

    # Check if the directory actually exists now
    if not os.path.exists(full_source_path):
        print(f"Error: Directory {full_source_path} not found!")
        print(f"Current Working Directory: {os.getcwd()}")
        return

    # Rest of your code...
    zig_files = [f for f in os.listdir(full_source_path) if f.endswith('.zig')]
    # ... (the rest of your loop and subprocess calls)

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
