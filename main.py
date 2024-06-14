import modules.resource_manager as rm

def main():
    manager = rm.ResourceManager(2, 10, 10)
    output = manager.main()
    return output
main()