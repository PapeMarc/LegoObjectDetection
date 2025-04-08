from program import Program
import sys
import os

def main():
    if os.getcwd() != 'C:/Users/marcp/SynologyDrive/FHDW/Unterrichtsmaterial/Semester 6/Projekt Algorithmen/task_solution/LegoObjectDetection':
        os.chdir('C:/Users/marcp/SynologyDrive/FHDW/Unterrichtsmaterial/Semester 6/Projekt Algorithmen/task_solution/LegoObjectDetection')

    program = Program()
#try:
    program.main([])
#except:
#    print("An unhandeled Error occured.")
#finally:
    program.exit()

if __name__ == "__main__":    
    main()