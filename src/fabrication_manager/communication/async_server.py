# async_server.py
import asyncio

class AsyncTCPServer:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.server = None
        self.server_task = None
        self.clients = set()
        self.lock = asyncio.Lock()

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
                print(f"Received from {addr}: {message}")
                # Echo the received message back to the client.
                async with lock:
                    for client in clients:
                        if client is not writer:
                            try:
                                client.write((message + "\n").encode())
                                await client.drain()
                            except Exception as e:
                                print(f"[Server] Error broadcasting to a client: {e}")
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
        addr = self.server.sockets[0].getsockname()
        print(f"Server listening on {addr}")
        async with self.server:
            await self.server.serve_forever()

    def start(self):
        self.server_task = asyncio.create_task(self._run_server())
        print("AsyncTCPServer started.")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                print("AsyncTCPServer cancelled.")
    

async def interactive_main(host='127.0.0.1', port=8888):
    server = AsyncTCPServer(host, port)
    print("Interactive Async TCP Server")
    print("Available commands: start, stop, exit")
    while True:
        # Use run_in_executor to get input without blocking the event loop.
        command = await asyncio.get_event_loop().run_in_executor(None, input, "Command> ")
        command = command.strip().lower()
        if command == "start":
            server.start()
        elif command == "stop":
            await server.stop()
        elif command == "exit":
            await server.stop()
            break
        else:
            print("Unknown command. Available commands: start, stop, exit")
    print("Exiting interactive server.")

if __name__ == '__main__':
    asyncio.run(interactive_main("192.168.52.1", 8888))