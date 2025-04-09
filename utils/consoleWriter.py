from datetime import datetime
import os

def writeShapeListToConsole(shape_list):
    #os.system("cls")
    print('\n----------------------------------------------------')
    time = datetime.now().time()
    time_str = f'| {time.hour}:{time.minute}:{time.second} |'
    
    shape_count = len(shape_list)
    if shape_count > 0:
        print(f'{time_str}  Detected following {len(shape_list)} Object(s): ')
    else:
        print(f'{time_str}  There were no Objects found ')

    placeholder = '|'
    for i in range(len(time_str)-2):
        placeholder += ' '
    placeholder += '|'

    print(placeholder)

    left_column = placeholder

    for i in range(len(shape_list)):

        left_column_list = list(left_column)
        indexToReplace = len(left_column) // 2 - 1
        if i - 9 >= 0:
            left_column_list[indexToReplace+1] = ''
            left_column_list[indexToReplace] = f'{i+1}'
        else:
            left_column_list[indexToReplace] = f'0'
            left_column_list[indexToReplace+1] = f'{i+1}'

        left_column = "".join(left_column_list)

        print(f'{left_column}  {shape_list[i]} ')

    print(placeholder)

    print('----------------------------------------------------\n')