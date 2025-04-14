from program import Program
from dotenv import dotenv_values
import os

from utils import consoleWriter

config = dotenv_values(".env")

project_dir = config['PROJECT_DIR']

if os.getcwd() != project_dir:
    os.chdir(project_dir)

if __name__ == '__main__':
    try:
        program = Program([config])
        program.main()
        
    except Exception as e:
        consoleWriter.writeError('An uncaught Exception reached top. Program shutdown.', e)
            
    finally:
        program.exit()