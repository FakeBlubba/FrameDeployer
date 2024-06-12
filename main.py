from modules.local_imports import *

def main():
    generator = resourceGenerator(1, 10, 10)
    output = generator.main()
    #if output != None:
    #   modules.editing.create_video_with_data(output)
    return output

main()
