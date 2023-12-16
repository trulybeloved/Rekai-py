import pathlib


tts_path = pathlib.Path('/tts_outputs/')
print(tts_path)
file_path = f'{tts_path}file.txt'

with open('C:\\Users\\prav9\\OneDrive\\Desktop\\Coding\\MTL\Rekai\\tts_outputs\\text.txt', 'w') as file:
    file.write('THis is some text')
