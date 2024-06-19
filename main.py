from modules.bot import start_bot
from modules.resource_manager import ResourceManager

def main():
    for i in range(5):
        resource_manager = ResourceManager(trend_number=i)
        description_text = resource_manager.main()
        print(description_text)

    start_bot()

if __name__ == '__main__':
    main()
