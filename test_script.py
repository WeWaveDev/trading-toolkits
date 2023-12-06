import glob
import subprocess


def run_script(file_path):
    try:
        # Run the script using Python and capture any output
        subprocess.check_output(['python', file_path], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        # If there's an error, print it out
        print(f"Error in {file_path}: {e.output.decode()}")
        return False

def test_all_examples():
    # Find all files that match the pattern 'example_*.py'
    example_files = glob.glob('*_example_*.py')
    
    all_passed = True
    for file in example_files:
        if not run_script(file):
            all_passed = False
    
    if all_passed:
        print("All examples ran successfully!")
    else:
        print("Some examples failed.")

# Run the test
test_all_examples()
