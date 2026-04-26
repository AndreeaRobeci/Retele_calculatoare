import socket

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


def receive_full_message(sock):
    """Primeste un mesaj cu lungimea prefixata: '<len> <mesaj>'"""
    try:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            return None

        string_data = data.decode("utf-8")
        first_space = string_data.find(" ")

        if first_space == -1 or not string_data[:first_space].isdigit():
            return "ERROR: format invalid de la server"

        message_length = int(string_data[:first_space])
        full_data = string_data[first_space + 1:]
        remaining = message_length - len(full_data.encode("utf-8"))

        while remaining > 0:
            chunk = sock.recv(BUFFER_SIZE)
            if not chunk:
                return None
            decoded = chunk.decode("utf-8")
            full_data += decoded
            remaining -= len(decoded.encode("utf-8"))

        return full_data

    except Exception as e:
        return f"ERROR: {e}"


# Functie de help care afiseaza toate comenzile disponibile
def print_help():
    print("""
Comenzi disponibile:
  ADD <key> <value>      - Adauga o intrare in dictionar
  GET <key>              - Returneaza valoarea pentru cheie
  REMOVE <key>           - Sterge o intrare din dictionar
  LIST                   - Listeaza toate intrarile
  COUNT                  - Numara intrarile din dictionar
  CLEAR                  - Sterge tot dictionarul
  UPDATE <key> <value>   - Actualizeaza valoarea unei chei
  POP <key>              - Returneaza si sterge o intrare
  QUIT                   - Inchide conexiunea
  help                   - Afiseaza acest mesaj
""")



def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # ---  gestionare eroare daca serverul nu ruleaza ---
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print(f"[CLIENT] Nu ma pot conecta la {HOST}:{PORT}. Serverul ruleaza?")
            return

        print(f"[CLIENT] Conectat la {HOST}:{PORT}")

        # --- afisare help la pornire ---
        print_help()

        while True:
            # ---  gestionare Ctrl+C / EOF fara crash ---
            try:
                command = input("client> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[CLIENT] Iesire.")
                break

            if not command:
                continue

            # ---  comanda locala "help", nu se trimite la server ---
            if command.lower() == "help":
                print_help()
                continue

            s.sendall(command.encode("utf-8"))
            response = receive_full_message(s)

            if response is None:
                print("[CLIENT] Conexiune inchisa de server.")
                break

            print(f"[SERVER] {response}")

            # ---  clientul se inchide dupa QUIT, la fel ca serverul ---
            if command.strip().upper() == "QUIT":
                break


if __name__ == "__main__":
    main()
