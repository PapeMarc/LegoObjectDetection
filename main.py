from program import Program
from dotenv import dotenv_values
import os

from utils import consoleWriter

# Load environment variables
config = dotenv_values(".env")

# Read the project directory path from environment variables
project_dir = config['PROJECT_DIR']

# Change the current working directory to the project directory if necessary
if os.getcwd() != project_dir:
    os.chdir(project_dir)

# Start the program when this file (main) is executed
if __name__ == '__main__':
    # Basic error handling
    try:
        # Declare and initialize the Program
        program = Program([config])
        # Execute the Program
        program.main()
        
    except Exception as e:
        # Catch exceptions and log an error message
        consoleWriter.writeError('An uncaught Exception reached top. Program shutdown.', e)
            
    finally:
        # Exit the program regardless of the runtime result
        program.exit()