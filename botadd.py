import datetime
from pyrogram import Client, filters

# Ganti dengan token bot Anda
api_id = "22320496"  # Dapatkan dari my.telegram.org
api_hash = "e968756305722371dff681ef35382f9e"  # Dapatkan dari my.telegram.orga
bot_token = "7738380382:AAGbnuv1J2SiERPn-eAt8BwCsNBf68k9ZR4"  # Ganti dengan token bot Telegram Anda

# Masukkan ID owner bot (dua ID Telegram)
OWNER_IDS = [7866362776, 6715388586]  # Ganti dengan dua ID Telegram Anda

# Membuat instance client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


# Fungsi untuk memeriksa apakah pengguna adalah owner
def is_owner(user_id):
    return user_id in OWNER_IDS


# Command /start untuk menampilkan menu
@app.on_message(filters.command("start"))
async def start(client, message):
    menu_text = """
Selamat datang di Bot Telegram!

Berikut adalah daftar fitur yang tersedia:
1. **/membercount [id_grup]** - Menampilkan jumlah anggota online dan offline (hanya untuk owner).
2. **/joingroup [id_grup atau tautan]** - Meminta bot untuk bergabung ke grup (hanya untuk owner).
3. **/leavegroup [id_grup]** - Meminta bot untuk keluar dari grup (hanya untuk owner).
4. **/restart** - Merestart bot (hanya untuk owner).
5. **/stop** - Menghentikan bot (hanya untuk owner).
6. **/start** - Menampilkan menu ini.

Silakan gunakan perintah sesuai kebutuhan Anda!
"""
    await message.reply(menu_text)


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

        if chat.type in ["private", "bot"]:
            await message.reply("ID yang Anda masukkan bukan grup. Pastikan Anda menggunakan ID grup yang valid.")
            return

        online_count = 0
        offline_count = 0
        last_online_time_limit = datetime.datetime.now() - datetime.timedelta(days=7)  # Anggap offline jika lebih dari 7 hari

        async for member in client.get_chat_members(chat_id):
            if member.status == "online":
                online_count += 1
            elif member.status == "offline":
                # Periksa kapan terakhir kali aktif jika member offline
                if member.last_online and member.last_online > last_online_time_limit:
                    online_count += 1
                else:
                    offline_count += 1

        total_count = online_count + offline_count
        await message.reply(f"Grup {chat.title} memiliki {total_count} anggota, dengan {online_count} online dan {offline_count} offline.")
    except Exception as e:
        if "CHAT_ID_INVALID" in str(e):
            await message.reply("ID grup tidak valid atau bot tidak memiliki akses ke grup tersebut.")
        elif "PEER_ID_INVALID" in str(e):
            await message.reply("Bot tidak dapat menemukan grup ini. Pastikan bot sudah diundang ke grup.")
        else:
            await message.reply(f"Terjadi kesalahan: {e}")


# Command untuk bot bergabung ke grup
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
        if "USER_ALREADY_PARTICIPANT" in str(e):
            await message.reply("Bot sudah menjadi anggota grup tersebut.")
        elif "INVITE_HASH_INVALID" in str(e):
            await message.reply("Tautan undangan tidak valid. Harap periksa kembali tautannya.")
        elif "CHAT_ADMIN_REQUIRED" in str(e):
            await message.reply("Bot tidak dapat bergabung. Pastikan bot diundang secara langsung.")
        else:
            await message.reply(f"Terjadi kesalahan: {e}")


# Command untuk bot keluar dari grup
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
        if "CHAT_ID_INVALID" in str(e):
            await message.reply("ID grup tidak valid atau bot tidak memiliki akses ke grup tersebut.")
        elif "PEER_ID_INVALID" in str(e):
            await message.reply("Bot tidak dapat menemukan grup ini. Pastikan bot sudah menjadi anggota grup tersebut.")
        else:
            await message.reply(f"Terjadi kesalahan: {e}")


# Command untuk merestart bot
@app.on_message(filters.command("restart"))
async def restart(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    await message.reply("Bot sedang merestart...")
    os.execv(sys.executable, ['python'] + sys.argv)


# Command untuk menghentikan bot
@app.on_message(filters.command("stop"))
async def stop(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    await message.reply("Bot dihentikan.")
    await client.stop()


@app.on_message(filters.command("transfermembers"))
async def transfer_members(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    try:
        # Periksa apakah ada dua argumen grup
        if len(message.command) < 3:
            await message.reply("Harap berikan username atau ID dari dua grup. Contoh: /transfermembers @grup1 @grup2")
            return

        group1 = message.command[1]  # Grup asal
        group2 = message.command[2]  # Grup tujuan

        # Ambil daftar anggota grup 2
        members_in_group2 = []
        async for member in client.get_chat_members(group2):
            if member.user.username:  # Pastikan memiliki username
                members_in_group2.append(member.user.username)

        added_count = 0  # Hitung jumlah anggota yang berhasil ditambahkan
        async for member in client.get_chat_members(group1):
            if added_count >= 40:  # Batas maksimum 40 anggota
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

# Jalankan bot
app.run()
