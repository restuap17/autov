import os
import sys
import datetime
import psutil  # For server info
import platform  # To get system info
from pyrogram import Client, filters
import time

# Masukkan API ID dan API Hash Anda
API_ID = 22320496  # Ganti dengan API ID Anda
API_HASH = "e968756305722371dff681ef35382f9e"  # Ganti dengan API Hash Anda

# Masukkan ID owner bot (dua ID Telegram)
OWNER_IDS = [7866362776, 6715388586]  # Ganti dengan dua ID Telegram Anda

# Fungsi untuk memeriksa apakah pengguna adalah owner
def is_owner(user_id):
    return user_id in OWNER_IDS

# Fungsi untuk membuat string session jika belum ada
def get_or_create_session():
    session_file = "userbot.session"  # Nama file session

    # Jika file string session belum ada, buat session baru
    if not os.path.exists(session_file):
        print("Tidak ada String Session. Silakan login untuk membuatnya:")
        with Client("userbot", api_id=API_ID, api_hash=API_HASH) as app:
            string_session = app.export_session_string()
            print(f"String Session Anda:\n{string_session}\n")
            return string_session
    else:
        # Jika sudah ada, baca string session dari file
        with open(session_file, "r") as f:
            return f.read()

# Mendapatkan String Session
STRING_SESSION = get_or_create_session()

# Simpan String Session ke file (jika baru dibuat)
if not os.path.exists("userbot.session"):
    with open("userbot.session", "w") as f:
        f.write(STRING_SESSION)

# Membuat instance client
app = Client("userbot", session_string=STRING_SESSION, api_id=API_ID, api_hash=API_HASH)

# Command /start untuk menampilkan menu
@app.on_message(filters.command("start"))
async def start(client, message):
    menu_text = """
Selamat datang di Userbot Telegram!

Berikut adalah daftar fitur yang tersedia:
1. **/membercount [id_grup]** - Menampilkan jumlah anggota online dan offline (hanya untuk owner).
2. **/joingroup [id_grup atau tautan]** - Meminta userbot untuk bergabung ke grup (hanya untuk owner).
3. **/leavegroup [id_grup]** - Meminta userbot untuk keluar dari grup (hanya untuk owner).
4. **/restart** - Merestart userbot (hanya untuk owner).
5. **/ping** - Memeriksa latency server.
6. **/serverinfo** - Menampilkan informasi server userbot.
7. **/transfermembers @grup1 @grup2 [jumlah]** - Memindahkan anggota dari grup pertama ke grup kedua (hanya untuk owner).
8. **/start** - Menampilkan menu ini.

Silakan gunakan perintah sesuai kebutuhan Anda!
"""
    await message.reply(menu_text)

# Command /ping untuk memeriksa latency server
@app.on_message(filters.command("ping"))
async def ping(client, message):
    start_time = time.time()
    await message.reply("Pinging server...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000)  # Convert to milliseconds
    await message.reply(f"Ping: {latency}ms")

# Command /serverinfo untuk mendapatkan informasi server
@app.on_message(filters.command("serverinfo"))
async def server_info(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    try:
        # Get system info
        uname = platform.uname()
        cpu_count = psutil.cpu_count(logical=True)
        memory = psutil.virtual_memory()
        uptime = datetime.timedelta(seconds=int(time.time() - psutil.boot_time()))
        
        info = f"""
Informasi Server Userbot:
- **Sistem**: {uname.system} {uname.release} ({uname.machine})
- **Hostname**: {uname.node}
- **CPU**: {cpu_count} Cores
- **RAM**: {memory.total / (1024 * 1024 * 1024):.2f} GB
- **Uptime**: {uptime}
- **Python Version**: {platform.python_version()}
        """
        await message.reply(info)
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {e}")

# Command untuk mengetahui jumlah anggota online dan offline berdasarkan ID grup
@app.on_message(filters.command("membercount"))
async def member_count(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    try:
        if len(message.command) < 2:
            await message.reply("Harap berikan ID grup. Contoh: /membercount -123456789")
            return

        chat_id = int(message.command[1])
        chat = await client.get_chat(chat_id)

        online_count = 0
        offline_count = 0
        async for member in client.get_chat_members(chat_id):
            if member.user.is_bot:
                continue  # Abaikan bot
            if member.user.status == "online":
                online_count += 1
            else:
                offline_count += 1

        total_count = online_count + offline_count
        await message.reply(f"Grup {chat.title} memiliki {total_count} anggota, dengan {online_count} online dan {offline_count} offline.")
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {e}")

# Command untuk userbot bergabung ke grup
@app.on_message(filters.command("joingroup"))
async def join_group(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    try:
        if len(message.command) < 2:
            await message.reply("Harap berikan ID grup atau tautan undangan. Contoh: /joingroup -123456789 atau /joingroup https://t.me/joinchat/XXXX")
            return

        group_input = message.command[1]
        await client.join_chat(group_input)
        await message.reply(f"Berhasil bergabung ke grup dengan ID/tautan: {group_input}")
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {e}")

# Command untuk userbot keluar dari grup
@app.on_message(filters.command("leavegroup"))
async def leave_group(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    try:
        if len(message.command) < 2:
            await message.reply("Harap berikan ID grup. Contoh: /leavegroup -123456789")
            return

        chat_id = int(message.command[1])
        await client.leave_chat(chat_id)
        await message.reply(f"Berhasil keluar dari grup dengan ID: {chat_id}")
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {e}")

# Command untuk merestart userbot
@app.on_message(filters.command("restart"))
async def restart(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    await message.reply("Userbot sedang merestart...")
    os.execv(sys.executable, ['python'] + sys.argv)

# Command untuk transfer anggota dari grup1 ke grup2
@app.on_message(filters.command("transfermembers"))
async def transfer_members(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    try:
        # Periksa apakah ada dua argumen grup dan jumlah transfer
        if len(message.command) < 4:
            await message.reply("Harap berikan username atau ID dari dua grup dan jumlah anggota yang ingin ditransfer. Contoh: /transfermembers @grup1 @grup2 30")
            return

        group1 = message.command[1]  # Grup asal
        group2 = message.command[2]  # Grup tujuan
        transfer_limit = int(message.command[3])  # Jumlah anggota yang ingin ditransfer

        # Batasi transfer sesuai dengan ketentuan Telegram (maksimal 50 anggota)
        if transfer_limit > 50:
            transfer_limit = 50

        # Ambil daftar anggota grup 2
        members_in_group2 = []
        async for member in client.get_chat_members(group2):
            if member.user.username:  # Pastikan memiliki username
                members_in_group2.append(member.user.username)

        added_count = 0  # Hitung jumlah anggota yang berhasil ditambahkan
        async for member in client.get_chat_members(group1):
            if added_count >= transfer_limit:  # Batas maksimal transfer
                break

            if member.user.username and member.user.username not in members_in_group2:
                try:
                    await client.add_chat_members(group2, member.user.id)  # Tambahkan anggota
                    added_count += 1
                except Exception as e:
                    print(f"Gagal menambahkan {member.user.username}: {e}")

        await message.reply(f"Berhasil menambahkan {added_count} anggota dari {group1} ke {group2}.")
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {e}")
        app.run()
                            
