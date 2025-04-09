from program import Program
import sys
import os

def main():

    laptop = True

    if laptop:
        project_dir = 'C:/Users/marcp/Documents/GitHub/LegoObjectDetection'
    else: 
        project_dir = 'C:/Users/marcp/SynologyDrive/FHDW/Unterrichtsmaterial/Semester 6/Projekt Algorithmen/task_solution/LegoObjectDetection'

    if os.getcwd() != project_dir:
        os.chdir(project_dir)

    program = Program()
    try:
        program.main([])
    except:
        print("WARNING: An uncatched Exception reached top. Program shutdown.")
    finally:
        program.exit()

if __name__ == "__main__":    
    main()