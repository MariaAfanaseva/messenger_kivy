import subprocess
import time


class Processes:
    """Open new server and 4 clients"""
    def __init__(self, clients):
        self.clients = clients

    def start_server_clients(self):
        processes = []
        while True:
            action = input('Enter the necessary command: \nst server - start the server,'
                           '\nst clients - start clients,\nclose - close all windows, '
                           '\nexit - exit\n')
            if action == 'st server':
                processes.append(subprocess.Popen('python server/server_main.py',
                                                  creationflags=subprocess.CREATE_NEW_CONSOLE))
            elif action == 'st clients':
                print('Make sure that the number of clients with a password of 123 is registered on the server.')
                clients_count = int(
                    input('Enter the number of test clients to run: '))
                for i in range(clients_count):
                    processes.append(
                        subprocess.Popen(
                            f'python client/client_main.py -n test{i + 1} -p 123',
                            creationflags=subprocess.CREATE_NEW_CONSOLE))
            elif action == 'close':
                while processes:
                    client = processes.pop()
                    client.kill()
            elif action == 'exit':
                break


def main():
    processes = Processes(3)
    processes.start_server_clients()


if __name__ == '__main__':
    main()
