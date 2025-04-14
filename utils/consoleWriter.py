from datetime import datetime
import os
import cv2

messages = {'messages':[], 'status':[], 'warnings':[], 'errors':[]}
loop_active = False

def writeShapeListToConsole(shape_list, generateConsoleImage, console_image):
    global loop_active
    loop_active = True
    
    os.system("cls")
    consoleString = '\n-------------------------------------------------------------------\n'
    time = datetime.now().time()
    hour, minute, second = time.hour, time.minute, time.second
    if time.hour < 10:
        hour = f'0{time.hour}'
    if time.minute < 10:
        minute = f'0{time.minute}'
    if time.second < 10:
        second = f'0{time.second}'

    time_str = f'| {hour}:{minute}:{second} |'
    
    shape_count = len(shape_list)
    if shape_count > 0:
        consoleString += f'{time_str} Detected {len(shape_list)} Object(s) \n'
        consoleString += '-------------------------------------------------------------------\n'
    else:
       consoleString += f'{time_str}  There were no Objects found \n'

    placeholder = '|'
    for i in range(len(time_str)-2):
        placeholder += ' '
    placeholder += '|'

    consoleString += placeholder + '          |             |                |       \n'

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

        consoleString += f'{left_column} {shape_list[i]} \n'

    consoleString += placeholder + '          |             |                |       \n'

    consoleString += '-------------------------------------------------------------------\n'
    
    for messageType in messages:
        if messageType == 'status':
            continue
        for message in messages[messageType]:
            consoleString += f'| {message}\n'
    
    consoleString += '-------------------------------------------------------------------\n\n'

    print(consoleString)

    if generateConsoleImage:
        if console_image is None:
            writeWarning('console_image in consoleWriter was None.')
        line_height = 22

        lines = consoleString.replace('|','').replace(chr(176),' degrees').split('\n')

        y_offset = line_height
        for line in lines:
            cv2.putText(console_image, line, (10, y_offset), cv2.FONT_ITALIC, 0.5, [0,255,0], 2)
            y_offset += line_height

        return console_image
    

def writeMessage(message):
    messages['messages'].append(message)
    if not loop_active:
        print(message)
    
def writeWarning(message):
    messages['warnings'].append(f'⚠️ {message}')
    if not loop_active:
        print(f'⚠️ {message}')
    
def writeError(message, error):
    if error:
        messages['errors'].append(f'❌ {message}. Error Message: ', error)
        if not loop_active:
            print(f'❌ {message}. Error Message: ', error)
    else:
        messages['errors'].append(f'❌ {message}.')
        if not loop_active:
            print(f'❌ {message}.')
            
def writeStatus(message):
    messages['status'].append(message)
    if not loop_active:
        print(message)