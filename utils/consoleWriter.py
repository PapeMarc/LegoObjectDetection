from datetime import datetime
import os
import cv2

# Dictionary to store different types of messages (status, warnings, errors, etc.)
messages = {'messages': [], 'status': [], 'warnings': [], 'errors': []}

# Flag to indicate whether the loop is active, preventing redundant console output
loop_active = False

# Function to write a list of shapes to the console and optionally generate a visual representation
def writeShapeListToConsole(shape_list, generateConsoleImage, console_image):
    global loop_active
    loop_active = True  # Set the loop_active flag to prevent redundant output

    # Clear the console for clean output
    os.system("cls")
    
    # Initialize the console string with a separator line
    consoleString = '\n-------------------------------------------------------------------\n'
    
    # Format the current time as HH:MM:SS
    time = datetime.now().time()
    hour, minute, second = time.hour, time.minute, time.second
    if time.hour < 10:
        hour = f'0{time.hour}'
    if time.minute < 10:
        minute = f'0{time.minute}'
    if time.second < 10:
        second = f'0{time.second}'
    time_str = f'| {hour}:{minute}:{second} |'
    
    # Add shape detection information to the console string
    shape_count = len(shape_list)
    if shape_count > 0:
        consoleString += f'{time_str} Detected {len(shape_list)} Object(s) \n'
        consoleString += '-------------------------------------------------------------------\n'
    else:
        consoleString += f'{time_str}  There were no Objects found \n'

    # Create a placeholder for formatting columns
    placeholder = '|'
    for i in range(len(time_str) - 2):
        placeholder += ' '
    placeholder += '|'

    # Add column headers and separators to the console string
    consoleString += placeholder + '          |             |                |       \n'
    
    left_column = placeholder

    # Iterate through the shape list and format each shape for display
    for i in range(len(shape_list)):
        left_column_list = list(left_column)
        indexToReplace = len(left_column) // 2 - 1
        
        # Format shape index for display (e.g., "01", "10")
        if i - 9 >= 0:
            left_column_list[indexToReplace + 1] = ''
            left_column_list[indexToReplace] = f'{i + 1}'
        else:
            left_column_list[indexToReplace] = f'0'
            left_column_list[indexToReplace + 1] = f'{i + 1}'
        
        left_column = "".join(left_column_list)
        
        # Add formatted shape information to the console string
        consoleString += f'{left_column} {shape_list[i]} \n'

    # Add footer separators to the console string
    consoleString += placeholder + '          |             |                |       \n'
    consoleString += '-------------------------------------------------------------------\n'
    
    # Append messages (warnings, errors) to the console string
    for messageType in messages:
        if messageType == 'status':
            continue # Skip status messages for this output
        for message in messages[messageType]:
            consoleString += f'| {message}\n'
    
    consoleString += '-------------------------------------------------------------------\n\n'

    # Print the final formatted console string
    print(consoleString)

    # Generate a visual representation of the console output using OpenCV if enabled
    if generateConsoleImage:
        if console_image is None:
            writeWarning('console_image in consoleWriter was None.')
        
        line_height = 22
        
        # Split the console string into individual lines and replace special characters for rendering
        lines = consoleString.replace('|', '').replace(chr(176), ' degrees').split('\n')

        y_offset = line_height
        
        # Render each line of text onto the provided image
        for line in lines:
            cv2.putText(console_image, line, (10, y_offset), cv2.FONT_ITALIC, 0.5, [0,255,0], 2)
            y_offset += line_height

        return console_image
    

# Function to log general messages
def writeMessage(message):
    messages['messages'].append(message)
    
    # Print immediately if loop is not active
    if not loop_active:
        print(message)
    
# Function to log warnings with a ⚠️ symbol
def writeWarning(message):
    messages['warnings'].append(f'⚠️ {message}')
    
    if not loop_active:
        print(f'⚠️ {message}')
    
# Function to log errors with a ❌ symbol and optional error details
def writeError(message, error):
    if error:
        messages['errors'].append(f'❌ {message}. Error Message: {error}')
        
        if not loop_active:
            print(f'❌ {message}. Error Message: {error}')
    else:
        messages['errors'].append(f'❌ {message}.') 
        
        if not loop_active:
            print(f'❌ {message}.')
            
# Function to log status updates
def writeStatus(message):
    messages['status'].append(message)
    
    if not loop_active:
        print(message)
