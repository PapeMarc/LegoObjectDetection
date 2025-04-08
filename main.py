from program import Program

def main():
    program = Program()
    try:
        program.main([])
    except:
        print("An unhandeled Error occured.")
    finally:
        program.exit()

if __name__ == "__main__":
    main()