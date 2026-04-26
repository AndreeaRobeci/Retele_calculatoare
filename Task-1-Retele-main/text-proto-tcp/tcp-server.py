import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            self.data[key] = value
        return f"OK - record add"

    def get(self, key):
        with self.lock:
            if key not in self.data:
                return f"ERROR invalid key"
            return f"DATA {self.data[key]}"

    def remove(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            del self.data[key]
            return "OK value deleted"


    def list_all(self):
        # Returneaza toate perechile cheie=valoare separate prin virgula
        with self.lock:
            if not self.data:
                return "DATA"
            items = ",".join(f"{k}={v}" for k, v in self.data.items())
            return f"DATA|{items}"

    def count(self):
        # Returneaza numarul de elemente din dictionar
        with self.lock:
            return f"DATA {len(self.data)}"

    def clear(self):
        # Sterge tot dictionarul
        with self.lock:
            self.data.clear()
        return "OK all data deleted"

    def update(self, key, value):
        # Actualizeaza valoarea unei chei existente; eroare daca nu exista
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            self.data[key] = value
        return "OK Data updated"

    def pop(self, key):
        # Returneaza valoarea si o sterge din dictionar
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            value = self.data.pop(key)
        return f"DATA {value}"



state = State()


def process_command(command):
    parts = command.split()

    if not parts:
        return "ERROR empty command"

    cmd = parts[0].upper()

    if cmd == "ADD":
        if len(parts) < 3:
            return "ERROR usage: ADD <key> <value>"
        key = parts[1]
        value = " ".join(parts[2:])
        return state.add(key, value)

    elif cmd == "GET":
        if len(parts) != 2:
            return "ERROR usage: GET <key>"
        return state.get(parts[1])

    elif cmd == "REMOVE":
        if len(parts) != 2:
            return "ERROR usage: REMOVE <key>"
        return state.remove(parts[1])


    elif cmd == "LIST":
        return state.list_all()

    elif cmd == "COUNT":
        return state.count()

    elif cmd == "CLEAR":
        return state.clear()

    elif cmd == "UPDATE":
        if len(parts) < 3:
            return "ERROR usage: UPDATE <key> <new_value>"
        key = parts[1]
        value = " ".join(parts[2:])
        return state.update(key, value)

    elif cmd == "POP":
        if len(parts) != 2:
            return "ERROR usage: POP <key>"
        return state.pop(parts[1])

    elif cmd == "QUIT":
        return "QUIT"


    else:
        return f"ERROR unknown command '{cmd}'"


# functie separata pentru trimiterea raspunsului cu lungime prefixata 
def send_response(client_socket, response):
    encoded = response.encode("utf-8")
    header = f"{len(encoded)} ".encode("utf-8")
    client_socket.sendall(header + encoded)


def handle_client(client_socket, addr):
    print(f"[SERVER] Client conectat: {addr}")
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    print(f"[SERVER] Client deconectat: {addr}")
                    break

                command = data.decode("utf-8").strip()
                print(f"[SERVER] Comanda primita de la {addr}: {command}")

                response = process_command(command)

                # Gestionarea comenzii QUIT: trimite raspuns si inchide conexiunea
                if response == "QUIT":
                    send_response(client_socket, "OK goodbye")
                    print(f"[SERVER] Client {addr} a trimis QUIT. Conexiune inchisa.")
                    break
                

                send_response(client_socket, response)

            except ConnectionResetError:
                #  gestionare specifica pentru deconectare brusca 
                print(f"[SERVER] Conexiune resetata de {addr}")
                break
            except Exception as e:
                try:
                    send_response(client_socket, f"ERROR {str(e)}")
                except Exception:
                    pass
                break


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        #  SO_REUSEADDR permite repornirea serverului fara eroare "address already in use" 
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Asculta pe {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(
                target=handle_client, args=(client_socket, addr), daemon=True
            )
            thread.start()


if __name__ == "__main__":
    start_server()
