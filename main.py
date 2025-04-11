from program import Program
from dotenv import dotenv_values
import sys
import os

config = dotenv_values(".env")

def main():

    project_dir = config['PROJECT_DIR']

    if os.getcwd() != project_dir:
        os.chdir(project_dir)

    program = Program()
    
    try:
        program.main([config])
        
    except:
        print("WARNING: An uncatched Exception reached top. Program shutdown.")
        
    finally:
        program.exit()

if __name__ == "__main__":    
    main()