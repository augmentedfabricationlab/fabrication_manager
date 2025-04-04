# async_server.py
import asyncio

class AsyncTCPServer:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.server = None
        self.server_task = None
        self.clients = set()
        self.history = []
        self.lock = asyncio.Lock()

    async def broadcast(self, message, exclude_writer=None):
        """Send a message to all clients (optionally excluding one writer)."""
        async with self.lock:
            for client in self.clients:
                if client is not exclude_writer:
                    try:
                        client.write((message + "\n").encode())
                        await client.drain()
                    except Exception as e:
                        print(f"[Server] Error sending message: {e}")

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, clients: set, lock: asyncio.Lock):
        addr = writer.get_extra_info('peername')
        print(f"Connected by {addr}")
        async with lock:
            clients.add(writer)

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break  # Connection closed.
                message = data.decode().strip()
                
                # Echo the received message back to the client.
                if message:
                    print(f"[Server] Received from {addr}: {message}")
                    self.history.append(message)
                    await self.broadcast(message, exclude_writer=writer)
        except Exception as e:
            print(f"[Server] Error with client {addr}: {e}")
        finally:
            async with lock:
                if writer in clients:
                    clients.remove(writer)
            writer.close()
            await writer.wait_closed()
            print(f"[Server] Connection closed for {addr}")

    async def _run_server(self):
        self.server = await asyncio.start_server(
            lambda r, w: self.handle_client(r, w, self.clients, self.lock),
            self.host, self.port
        )
        async with self.server:
            await self.server.serve_forever()

    def start(self):
        if self.server_task is None or self.server_task.done():
            self.server_task = asyncio.create_task(self._run_server())
            print("[Control] Server started in background.")
            print("[Control] Running on:", self.host, self.port)
        else:
            print("[Control] Server is already running.")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("[Control] Server stopped.")
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                print("AsyncTCPServer cancelled.")
            self.server_task = None
    

async def interactive_main(host='127.0.0.1', port=8888):
    """
    Provides an interactive prompt for the server operator.
    Commands include:
      - start: start the server
      - stop: stop the server
      - client_list: list connected clients
      - show_history: display message history
      - clear_history: clear message history
      - broadcast <message>: send a message to all clients
      - exit: stop the server and exit
    """
    server = AsyncTCPServer(host, port)
    print("Interactive Async TCP Server")
    print("Available commands: start, stop, client_list, show_history, clear_history, broadcast, exit")
    while True:
        # Use run_in_executor to get input without blocking the event loop.
        try:
            cmd_line = await asyncio.get_event_loop().run_in_executor(None, input, "$ Server Command>>> ")
        except EOFError:
            print("EOF encountered. Exiting interactive prompt.")
            break
        if not cmd_line.strip():
            continue
        tokens = cmd_line.strip().split()
        command = tokens[0].lower()
        
        if command == "start":
            server.start()
        elif command == "stop":
            await server.stop()
        elif command == "client_list":
            async with server.lock:
                print(f"[Control] {len(server.clients)} Connected clients:")    
                for client in server.clients:
                    addr = client.get_extra_info('peername')
                    print(f"  - {addr}")
        elif command == "show_history":
            print("[Control] Message history:")
            for msg in server.history:
                print(f"  - {msg}")
        elif command == "clear_history":
            server.history.clear()
            print("[Control] Cleared message history.")
        elif command == "broadcast":
            if len(tokens) >= 2:
                message = cmd_line[len("broadcast "):]
                server.history.append(message)
                await server.broadcast(message)
                print("[Control] Message broadcast.")
            else:
                print("[Control] Usage: broadcast <message>")
        elif command == "exit":
            await server.stop()
            print("[Control] Exiting interactive server.")
            break
        else:
            print("Unknown command. Available commands: start, stop, list, history, broadcast, exit")
    print("Exiting interactive server.")

if __name__ == '__main__':
    asyncio.run(interactive_main("192.168.52.1", 8888))