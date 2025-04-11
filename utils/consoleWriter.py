from datetime import datetime
import os

messages = {'messages':[], 'status':[], 'warnings':[], 'errors':[]}
loop_active = False

def writeShapeListToConsole(shape_list):
    global loop_active
    loop_active = True
    
    os.system("cls")
    print('\n-------------------------------------------------------------------')
    time = datetime.now().time()
    time_str = f'| {time.hour}:{time.minute}:{time.second} |'
    
    shape_count = len(shape_list)
    if shape_count > 0:
        print(f'{time_str} Detected {len(shape_list)} Object(s) ')
        print('-------------------------------------------------------------------')
    else:
        print(f'{time_str}  There were no Objects found ')

    placeholder = '|'
    for i in range(len(time_str)-2):
        placeholder += ' '
    placeholder += '|'

    print(placeholder + '          |             |                |       ')

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

        print(f'{left_column} {shape_list[i]} ')

    print(placeholder + '          |             |                |       ')

    print('-------------------------------------------------------------------')
    
    for messageType in messages:
        if messageType == 'status':
            continue
        for message in messages[messageType]:
            print(f'| {message}')
    
    print('-------------------------------------------------------------------\n')
    
    
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