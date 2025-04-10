from program import Program
from dotenv import dotenv_values
import sys
import os

config = dotenv_values(".env")

def main():

    laptop = True

    if laptop:
        project_dir = config['PROJECT_DIR_LAPTOP']
    else: 
        project_dir = config['PROJECT_DIR_HOME_PC']

    if os.getcwd() != project_dir:
        os.chdir(project_dir)

    program = Program()
#try:
    program.main([config])
#except:
#    print("WARNING: An uncatched Exception reached top. Program shutdown.")
#finally:
    program.exit()

if __name__ == "__main__":    
    main()