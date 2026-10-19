import asyncio
import json
import os
import random
import sys
import time
import urllib.parse
import aiohttp
import websockets

SELF_TOKEN = "MTU2MDMzNDUxNzA0MDk4MDAwNA.GI19Vr.YSEuB44fOT1qnYfMoGgXLCYuWoNOjaG27pCf_Q"

MASTER_OWNER_ID = 1360926339762356315
AUTHORIZED_USERS = {MASTER_OWNER_ID}
PREFIX = '*'

BOT_STATS = {"total_renames_done": 0, "total_gcs_created": 0, "total_gcs_failed": 0, "uptime": time.time()}
GLOBAL_NC_TASK = None
SERVER_NC_TASK = None
BLAST2_TASKS = {}

EMOJIS = ["👿", "🔥", "💀", "⚡", "🖕", "🔞", "🔪", "💥", "👑", "👺", "🧨", "🌀"]
HEARTS = ["💖", "💗", "💓", "💞", "💕", "💘", "🩷", "🩵", "❤️", "🧡", "💛", "💚", "💙", "💜"]

def get_emoji(): return random.choice(EMOJIS)
def get_heart(): return random.choice(HEARTS)

def apply_fancy_font(text):
    font_map = {'A':'ꪑ','B':'ʙ','C':'ᴄ','D':'ᴅ','E':'ᴇ','F':'ғ','G':'ɢ','H':'ʜ','I':'ɪ','J':'ᴊ','K':'ᴋ','L':'ʟ','M':'ᴍ','N':'ɴ','O':'ᴏ','P':'ᴘ','Q':'ǫ','R':'ʀ','S':'s','T':'ᴛ','U':'ᴜ','V':'ᴠ','W':'ᴡ','X':'x','Y':'ʏ','Z':'ᴢ'}
    return ''.join(font_map.get(c, c) for c in text)

UNAUTHORIZED_DENIAL_MSG = "𝐀𝐏𝐍𝐈 𝐌𝐀𝐀 𝐃𝐄 𝐏𝐄𝐇𝐋𝐄 𝐅𝐈𝐑 𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐔𝐍𝐆𝐀🤰🏻🍑😍"
LEAVE_GC_MESSAGE = "KARTIK DADDY NE SAB H8RS PEL DIYE AB MAI CHALTA HU😍🍑\nhttps://klipy.com/gifs/game-over-79"

STYLE_GAALIYON_LIST = [
    "RNDIKE ꪑᴀ𝐃ᴀRᴄ𝐇⭕ᴅ-👿 ⃤  RNDIKE ꪑᴀ𝐃ᴀRᴄ𝐇⭕ᴅ-👿",
    "MADARCHOD KI AULAAD BHOSDIKE - TERI MAA KI CHUT ME KARTIK KA LUND"
]

def get_styled_gc_name(target_name=""):
    g = random.choice(STYLE_GAALIYON_LIST)
    e = get_emoji()
    return f"[{target_name}] {e} ⃤  {apply_fancy_font(g)}-{e}" if target_name else f"{e} ⃤  {apply_fancy_font(g)}-{e}"

SPAM_GAALIYON_LIST = ["KYA RE RNDYKE AUR BHIDEGA?", "KARTIK PAPA BOL YA CHUD"]

def get_random_msg(target):
    selected_text = random.choice(SPAM_GAALIYON_LIST)
    e = get_emoji()
    return f"# 🎯 {target} 🎯\n\n# {target} {apply_fancy_font(selected_text)} {e}\n"

# --- SUPER FAST LIGHTWEIGHT AI GENERATOR ---
async def get_kartik_ai_response(session: aiohttp.ClientSession, prompt: str) -> str:
    if not prompt.strip():
        return "Bolo kya bolna hai?"
    
    system_persona = "You are KARTIK AI, an aggressive, dominant, savage, and highly intelligent AI created by Kartik. Always reply in short savage Hinglish."
    full_prompt = f"{system_persona}\nUser: {prompt}\nReply:"
    encoded = urllib.parse.quote(full_prompt)
    
    url = f"https://text.pollinations.ai/{encoded}?model=openai&cache=false"
    
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=4)) as resp:
            if resp.status == 200:
                text = await resp.text()
                if text and len(text.strip()) > 0:
                    return text.strip()
    except Exception:
        pass

    return f"Abe BSDK {prompt} - Sun KARTIK AI hamesha fast hai! 🔥"

async def send_message(session, channel_id, content):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {"Authorization": SELF_TOKEN, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Content-Type": "application/json"}
    try:
        async with session.post(url, headers=headers, json={"content": content}) as resp:
            if resp.status in [200, 201]:
                data = await resp.json()
                return data.get("id")
    except Exception: pass
    return None

async def edit_message(session, channel_id, message_id, new_content):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
    headers = {"Authorization": SELF_TOKEN, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Content-Type": "application/json"}
    try:
        async with session.patch(url, headers=headers, json={"content": new_content}) as resp:
            return resp.status in [200, 201]
    except Exception: return False

async def run_bot():
    global GLOBAL_NC_TASK, SERVER_NC_TASK
    headers = {"Authorization": SELF_TOKEN, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Content-Type": "application/json"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get("https://discord.com/api/v9/users/@me") as resp:
            if resp.status == 200:
                user_data = await resp.json()
                bot_user_id = user_data.get('id')
                AUTHORIZED_USERS.add(int(bot_user_id))
                print(f"✅ Connected as {user_data.get('username')} (ID: {bot_user_id})")
            else:
                print("❌ Token validation failed")
                return

        async with session.get("https://discord.com/api/v9/gateway") as resp:
            gw_data = await resp.json()
            ws_url = gw_data.get("url") + "/?v=9&encoding=json"

        print("🌐 Connecting to Gateway...")
        async with websockets.connect(ws_url) as websocket:
            hello = json.loads(await websocket.recv())
            heartbeat_interval = hello['d']['heartbeat_interval'] / 1000

            await websocket.send(json.dumps({
                "op": 2, "d": {
                    "token": SELF_TOKEN, "capabilities": 16383,
                    "properties": {"os": "Windows", "browser": "Chrome", "device": "", "browser_user_agent": "Mozilla/5.0", "browser_version": "115.0", "os_version": "10"},
                    "presence": {"status": "online", "since": 0, "activities": [], "afk": False}
                }
            }))
            print("🚀 Kartik DOMINATORZ Gateway Online!")

            async def heartbeat():
                while True:
                    await asyncio.sleep(heartbeat_interval)
                    try: await websocket.send(json.dumps({"op": 1, "d": None}))
                    except Exception: break
            asyncio.create_task(heartbeat())

            while True:
                try:
                    event = json.loads(await websocket.recv())
                    if event.get("t") == "MESSAGE_CREATE":
                        msg_data = event.get("d")
                        author = msg_data.get("author", {})
                        author_id = int(author.get("id", 0))
                        content = msg_data.get("content", "")
                        channel_id = msg_data.get("channel_id")

                        if content.startswith(PREFIX):
                            if author_id not in AUTHORIZED_USERS and author_id != MASTER_OWNER_ID:
                                await send_message(session, channel_id, UNAUTHORIZED_DENIAL_MSG)
                                continue

                            parts = content[len(PREFIX):].strip().split(" ")
                            cmd = parts[0].lower()
                            args = " ".join(parts[1:]) if len(parts) > 1 else ""

                            if cmd in ["help", "cmds"]:
                                help_txt = (
                                    "```ini\n"
                                    "==================================================\n"
                                    "           ✨ KARTIK DOMINATORZ VIP MENU ✨        \n"
                                    "==================================================\n"
                                    "[ AI & CORE COMMANDS ]\n"
                                    "*ai <prompt>       - Query local/online AI Model\n"
                                    "*ping              - Check bot latency\n"
                                    "*status            - Show system uptime & stats\n"
                                    "*gcstatus          - Display GC creation metrics\n\n"
                                    "[ GROUP CHAT AUTOMATION ]\n"
                                    "*makegc <n> [@s]   - Spawn multiple group chats\n"
                                    "*kickall [@user]   - Kick user from all mutual GCs\n"
                                    "*leaveall / *dead  - Leave and delete all group chats\n"
                                    "*globalnc <name>   - Globally rename all GCs\n\n"
                                    "[ RAID & SPAM TOOLS ]\n"
                                    "*blast <target>    - Single spam blast round\n"
                                    "*blast2 <target>   - Continuous high-speed loop blast\n"
                                    "*stopblast2        - Stop active blast loop\n"
                                    "*dmblast [@user]   - Blast user DMs with payloads\n"
                                    "*nuke / *delall    - Delete all server channels\n"
                                    "*servernc <name>   - Rename all channels in server\n\n"
                                    "[ UTILITIES & ADMIN ]\n"
                                    "*setstatus <txt>   - Update rich presence status\n"
                                    "*accessgive [@u]   - Grant control permissions\n"
                                    "*removeaccess [@u] - Revoke control permissions\n"
                                    "*listaccess        - List all authorized users\n"
                                    "*shutdown          - Terminate selfbot process\n"
                                    "==================================================\n"
                                    "```"
                                )
                                await send_message(session, channel_id, help_txt)

                            elif cmd == "ai":
                                async def process_ai():
                                    ans = await get_kartik_ai_response(session, args)
                                    await send_message(session, channel_id, f"🧠 **KARTIK AI Core**: {ans}")
                                asyncio.create_task(process_ai())

                            elif cmd in ["accessgive", "giveaccess"]:
                                if author_id == MASTER_OWNER_ID and msg_data.get("mentions"):
                                    tid = int(msg_data["mentions"][0]["id"])
                                    AUTHORIZED_USERS.add(tid)
                                    await send_message(session, channel_id, f"✅ Access granted to <@{tid}>")

                            elif cmd == "removeaccess":
                                if author_id == MASTER_OWNER_ID and msg_data.get("mentions"):
                                    tid = int(msg_data["mentions"][0]["id"])
                                    if tid in AUTHORIZED_USERS and tid != MASTER_OWNER_ID:
                                        AUTHORIZED_USERS.remove(tid)
                                        await send_message(session, channel_id, f"🔒 Access removed for <@{tid}>")

                            elif cmd == "listaccess":
                                ulist = ", ".join([f"<@{uid}>" for uid in AUTHORIZED_USERS])
                                await send_message(session, channel_id, f"👑 **Authorized Users**:\n{ulist}")

                            elif cmd == "ping":
                                st = time.time()
                                mid = await send_message(session, channel_id, "⚡ Measuring ping...")
                                ms = round((time.time() - st) * 1000, 2)
                                if mid: await edit_message(session, channel_id, mid, f"⚡ Latency: `{ms}ms`")

                            elif cmd == "status":
                                ut = round(time.time() - BOT_STATS["uptime"], 1)
                                await send_message(session, channel_id, f"🔥 Uptime: `{ut}s` | GCs: `{BOT_STATS['total_gcs_created']}` | Renames: `{BOT_STATS['total_renames_done']}`")

                            elif cmd == "gcstatus":
                                await send_message(session, channel_id, f"📊 Created: `{BOT_STATS['total_gcs_created']}` | Failed: `{BOT_STATS['total_gcs_failed']}`")

                            elif cmd in ["makegc", "gcmake"]:
                                sub = args.split(" ")
                                count = int(sub[0]) if sub and sub[0].isdigit() else 10
                                recips = [str(m["id"]) for m in msg_data.get("mentions", []) if str(m["id"]) != str(bot_user_id)]
                                
                                async def bg_makegc():
                                    sid = await send_message(session, channel_id, f"🚀 Spawning {count} GCs...")
                                    cc = fc = 0
                                    for i in range(count):
                                        if i > 0 and i % 50 == 0: await asyncio.sleep(3.0)
                                        try:
                                            async with session.post("https://discord.com/api/v9/users/@me/channels", headers=headers, json={"recipients": recips}) as r:
                                                if r.status in [200, 201]:
                                                    BOT_STATS['total_gcs_created'] += 1; cc += 1
                                                else:
                                                    async with session.post("https://discord.com/api/v9/users/@me/channels", headers=headers, json={"recipients": []}) as r2:
                                                        if r2.status in [200, 201]:
                                                            BOT_STATS['total_gcs_created'] += 1; cc += 1
                                                        else:
                                                            BOT_STATS['total_gcs_failed'] += 1; fc += 1
                                        except Exception:
                                            BOT_STATS['total_gcs_failed'] += 1; fc += 1
                                        await asyncio.sleep(0.3)
                                    if sid: await edit_message(session, channel_id, sid, f"✅ Completed! Created: `{cc}` | Failed: `{fc}`")
                                asyncio.create_task(bg_makegc())

                            elif cmd == "kickall":
                                tuid = msg_data["mentions"][0]["id"] if msg_data.get("mentions") else None
                                if tuid:
                                    async def bg_kickall():
                                        async with session.get("https://discord.com/api/v9/users/@me/channels", headers=headers) as resp:
                                            if resp.status == 200:
                                                kc = 0
                                                for ch in await resp.json():
                                                    if ch.get("type") == 3:
                                                        async with session.delete(f"https://discord.com/api/v9/channels/{ch['id']}/recipients/{tuid}", headers=headers) as k:
                                                            if k.status in [200, 204]: kc += 1
                                                        await asyncio.sleep(0.15)
                                                await send_message(session, channel_id, f"✅ Kicked target from `{kc}` GCs.")
                                    asyncio.create_task(bg_kickall())

                            elif cmd in ["leavegc", "leaveall", "alldead"]:
                                async def bg_leave():
                                    async with session.get("https://discord.com/api/v9/users/@me/channels", headers=headers) as resp:
                                        if resp.status == 200:
                                            lc = 0
                                            for ch in await resp.json():
                                                if ch.get("type") == 3:
                                                    cid = ch['id']
                                                    await send_message(session, cid, LEAVE_GC_MESSAGE)
                                                    await asyncio.sleep(0.2)
                                                    async with session.delete(f"https://discord.com/api/v9/channels/{cid}", headers=headers) as d:
                                                        if d.status in [200, 204]: lc += 1
                                                    await asyncio.sleep(0.1)
                                            await send_message(session, channel_id, f"🧹 Left `{lc}` GCs.")
                                asyncio.create_task(bg_leave())

                            elif cmd == "blast":
                                target = args if args else "@everyone"
                                for _ in range(4):
                                    await send_message(session, channel_id, get_random_msg(target))
                                    await asyncio.sleep(0.2)

                            elif cmd == "blast2":
                                target = args if args else "@everyone"
                                if channel_id in BLAST2_TASKS: BLAST2_TASKS[channel_id].cancel()
                                async def run_b2():
                                    while True:
                                        try:
                                            await send_message(session, channel_id, f"# 🎯 {target} {get_heart()} {get_heart()} 🎯\n# {target} {apply_fancy_font(random.choice(SPAM_GAALIYON_LIST))} {get_emoji()}")
                                            await asyncio.sleep(0.4)
                                        except asyncio.CancelledError: break
                                        except Exception: await asyncio.sleep(0.5)
                                BLAST2_TASKS[channel_id] = asyncio.create_task(run_b2())
                                await send_message(session, channel_id, "💖 Blast2 loop started! Type `*stopblast2` to stop.")

                            elif cmd == "stopblast2":
                                if channel_id in BLAST2_TASKS:
                                    BLAST2_TASKS[channel_id].cancel()
                                    del BLAST2_TASKS[channel_id]
                                    await send_message(session, channel_id, "🛑 Blast2 stopped.")

                            elif cmd == "dmblast":
                                tuid = msg_data["mentions"][0]["id"] if msg_data.get("mentions") else None
                                if tuid:
                                    async def bg_dm():
                                        async with session.post("https://discord.com/api/v9/users/@me/channels", headers=headers, json={"recipient_id": tuid}) as r:
                                            if r.status in [200, 201]:
                                                dcid = (await r.json())["id"]
                                                for _ in range(5):
                                                    await send_message(session, dcid, f"KARTIK ABBU BOL RNDYKE 🤣🔥 {get_random_msg('TARGET')}")
                                                    await asyncio.sleep(0.3)
                                    asyncio.create_task(bg_dm())

                            elif cmd == "globalnc":
                                if GLOBAL_NC_TASK: GLOBAL_NC_TASK.cancel()
                                async def run_gnc():
                                    while True:
                                        try:
                                            async with session.get("https://discord.com/api/v9/users/@me/channels", headers=headers) as resp:
                                                if resp.status == 200:
                                                    for ch in await resp.json():
                                                        if ch.get("type") == 3:
                                                            await session.patch(f"https://discord.com/api/v9/channels/{ch['id']}", headers=headers, json={"name": get_styled_gc_name(args)})
                                                            BOT_STATS['total_renames_done'] += 1
                                                            await asyncio.sleep(0.05)
                                        except asyncio.CancelledError: break
                                        except Exception: await asyncio.sleep(0.1)
                                GLOBAL_NC_TASK = asyncio.create_task(run_gnc())
                                await send_message(session, channel_id, "🌐 Global Name Change started!")

                            elif cmd == "servernc":
                                async with session.get(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers) as resp:
                                    if resp.status == 200:
                                        gid = (await resp.json()).get("guild_id")
                                        if gid:
                                            async def run_snc():
                                                while True:
                                                    try:
                                                        async with session.get(f"https://discord.com/api/v9/guilds/{gid}/channels", headers=headers) as g:
                                                            if g.status == 200:
                                                                for gch in await g.json():
                                                                    await session.patch(f"https://discord.com/api/v9/channels/{gch['id']}", headers=headers, json={"name": args or "KARTIK DOMINATORZ"})
                                                                    await asyncio.sleep(0.1)
                                                    except asyncio.CancelledError: break
                                                    except Exception: await asyncio.sleep(0.2)
                                            global SERVER_NC_TASK
                                            SERVER_NC_TASK = asyncio.create_task(run_snc())
                                            await send_message(session, channel_id, "🌍 Server renaming started!")

                            elif cmd == "setstatus":
                                await websocket.send(json.dumps({"op": 3, "d": {"since": 0, "activities": [{"name": args or "Kartik Dominatorz", "type": 0}], "status": "online", "afk": False}}))
                                await send_message(session, channel_id, f"✅ Status updated to: `{args}`")

                            elif cmd == "nuke":
                                async with session.get(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers) as resp:
                                    if resp.status == 200:
                                        gid = (await resp.json()).get("guild_id")
                                        if gid:
                                            async with session.get(f"https://discord.com/api/v9/guilds/{gid}/channels", headers=headers) as g:
                                                if g.status == 200:
                                                    for gch in await g.json():
                                                        await session.delete(f"https://discord.com/api/v9/channels/{gch['id']}", headers=headers)
                                                        await asyncio.sleep(0.1)

                            elif cmd == "delall":
                                async with session.get(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers) as resp:
                                    if resp.status == 200:
                                        gid = (await resp.json()).get("guild_id")
                                        if gid:
                                            async with session.get(f"https://discord.com/api/v9/guilds/{gid}/channels", headers=headers) as g:
                                                if g.status == 200:
                                                    for gch in await g.json():
                                                        await session.delete(f"https://discord.com/api/v9/channels/{gch['id']}", headers=headers)
                                                        await asyncio.sleep(0.1)

                            elif cmd == "shutdown":
                                await send_message(session, channel_id, "🛑 Shutting down...")
                                os._exit(0)

                except Exception: await asyncio.sleep(1)

if __name__ == "__main__":
    while True:
        try: asyncio.run(run_bot())
        except Exception as e:
            print(f"⚠️ Crashed: {e}. Restarting...")
            time.sleep(3)
