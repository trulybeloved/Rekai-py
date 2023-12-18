# import pathlib
#
#
# tts_path = pathlib.Path('/tts_outputs/')
# print(tts_path)
# file_path = f'{tts_path}file.txt'
#
# with open('C:\\Users\\prav9\\OneDrive\\Desktop\\Coding\\MTL\Rekai\\tts_outputs\\text.txt', 'w') as file:
#     file.write('THis is some text')


string = r'\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF65-\uFF9F\u0020-\u007E\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF01-\uFF5E\u2000-\u206F\u3000-\u303F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]'

splitat = str(r'\')
split_string = string.split(splitat)
print(split_string)

