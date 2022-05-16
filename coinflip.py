import json, websockets, asyncio, random
async def coinflip():
    session_id = input("Session-id: "); auth_session = json.dumps({"id":"authSession","sessionID":session_id})

    bet = 1;bet_side = "heads";bet_data = json.dumps({"id":"onCoinflip","sessionID":session_id,"bet":bet,"side":bet_side})
    username = None;history = [];current_balance = 0.0

    async for ws in websockets.connect("wss://ws.growcasino.net/"):
        await ws.send(auth_session)
        username = (json.loads(str(await ws.recv())))["username"]
        print("Logged in as", username)
        await ws.send(bet_data)
        while True:
            message = await ws.recv()
            response = json.loads(str(message))
            if response["id"] == "onBalanceUpdated":
                current_balance = (float(response["balance"])*100)
                if current_balance >= 1000.0: # gapped to reach 10dls then stop
                    print(f"[+] Reached 10DLS")
                    break
                else:
                    await asyncio.sleep(0.5)
                    if current_balance > 0:
                        bet_data = json.dumps({"id":"onCoinflip","sessionID":session_id,"bet":bet,"side":bet_side})
                        await ws.send(bet_data)
                        print("[=] Wallet: ", str(current_balance)+"WL")
                    else:
                        print("[-] Lost all")
            if response["id"] == "onCoinflipResult" and response["username"] == username:
                history.append(response["outcome"])
                cside = history[len(history)-1]

                # make your autobet scripts here :) enjoy

                if len(history) >= 2 and history[len(history)-1] == history[len(history)-2]:
                    if cside == "tails":
                        bet_side = "heads"
                    else:
                        bet_side = "tails"

                    if history[len(history)-1] == history[len(history)-2] == history[len(history)-3] == history[len(history)-4]:
                        bet_side = history[len(history)-1]
                    elif history[len(history)-1] == history[len(history)-2] == history[len(history)-3]:
                        bet = random.randint(1, 2)
                    else:
                        bet = random.randint(1, 4)
                else:
                    bet_side = cside
                    bet = 1
                if bet > current_balance and current_balance > 1:
                    bet = current_balance/2

if __name__ == "__main__": asyncio.run(coinflip())
