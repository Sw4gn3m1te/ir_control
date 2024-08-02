import asyncio
import socket
import argparse as ap
import json

parser = ap.ArgumentParser()
parser.add_argument('-c', '--color')
parser.add_argument('-a', '--address')
parser.add_argument('-p', '--port')
parser.add_argument('-f', '--file')
args = parser.parse_args()
print(args)
color, ip, port, fp = args.color, args.address, args.port, args.file


async def send():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                await asyncio.get_event_loop().sock_connect(s, (ip, port))
                s.send(color.encode())
                await asyncio.sleep(5)
    except Exception as e:
        print(f"{e} in send()")
        await asyncio.sleep(5)
        await send()


async def update_db(fp, data):
    with open(fp, "w+") as f:
        try:
            jdata = json.load(f)
        except json.JSONDecodeError:
            jdata = {}

        jdata.update({f"{color}{hash(data.decode())}": data.decode()})
        json.dump(jdata, f)

        f.close()


async def rec():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            await asyncio.get_event_loop().sock_connect(s, (ip, port))
            while True:
                data = await asyncio.get_event_loop().sock_recv(s, 1024)
                print('Received:', data.decode())
                await update_db(fp, data)
    except Exception as e:
        print(f"{e} in rec()")
        await asyncio.sleep(5)
        await rec()


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(send())
        tg.create_task(rec())


if __name__ == '__main__':
    asyncio.run(main())


