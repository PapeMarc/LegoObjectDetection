from program import Program
from dotenv import dotenv_values
import sys
import os

from utils import consoleWriter

config = dotenv_values(".env")

def main():

    project_dir = config['PROJECT_DIR']

    if os.getcwd() != project_dir:
        os.chdir(project_dir)

    program = Program()
    
    #try:
    program.main([config])
        
    #except Exception as e:
    #    consoleWriter.writeError('An uncaught Exception reached top. Program shutdown.', e)
        
    #finally:
    program.exit()

if __name__ == "__main__":
    main()