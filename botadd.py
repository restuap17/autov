import os
import sys
import datetime
from pyrogram import Client, filters

# Ganti dengan token bot Anda
api_id = "22320496"  # Dapatkan dari my.telegram.org
api_hash = "e968756305722371dff681ef35382f9e"  # Dapatkan dari my.telegram.org
bot_token = "7738380382:AAGbnuv1J2SiERPn-eAt8BwCsNBf68k9ZR4"  # Ganti dengan token bot Telegram Anda

# Masukkan ID owner bot (dua ID Telegram)
OWNER_IDS = [7866362776, 6715388586]  # Ganti dengan dua ID Telegram Anda

# Membuat instance client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


# Fungsi untuk memeriksa apakah pengguna adalah owner
def is_owner(user_id):
    return user_id in OWNER_IDS


# Command untuk menambahkan anggota dari Grup 1 ke Grup 2 menggunakan username
@app.on_message(filters.command("addmembers"))
async def add_members(client, message):
    if not is_owner(message.from_user.id):
        await message.reply("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    try:
        # Periksa apakah ada username grup dalam perintah
        if len(message.command) < 3:
            await message.reply("Harap berikan username grup asal dan tujuan. Contoh: /addmembers @grup1 @grup2")
            return

        group1_username = message.command[1]  # Username Grup 1 (contoh: @grup1)
        group2_username = message.command[2]  # Username Grup 2 (contoh: @grup2)

        # Dapatkan informasi grup dari username
        group1 = await client.get_chat(group1_username)
        group2 = await client.get_chat(group2_username)

        # Pastikan bot adalah admin di Grup 2
        group2_member = await client.get_chat_member(group2.id, "me")
        if not group2_member.can_add_users:
            await message.reply("Bot harus menjadi admin dengan izin untuk menambahkan anggota di Grup 2.")
            return

        # Maksimal jumlah anggota yang akan ditambahkan
        max_members = 40
        added_count = 0

        # Iterasi melalui anggota Grup 1
        async for member in client.get_chat_members(group1.id):
            if added_count >= max_members:
                break

            # Cek apakah anggota sudah ada di Grup 2
            try:
                await client.get_chat_member(group2.id, member.user.id)
                continue  # Jika sudah ada, lanjutkan ke anggota berikutnya
            except:
                pass  # Jika belum ada, tambahkan ke Grup 2

            # Tambahkan anggota ke Grup 2
            try:
                await client.add_chat_members(group2.id, member.user.id)
                added_count += 1
                await message.reply(f"Berhasil menambahkan: {member.user.first_name} ke {group2.title}.")
            except Exception as e:
                await message.reply(f"Gagal menambahkan {member.user.first_name}: {e}")
                continue

        if added_count == 0:
            await message.reply(f"Tidak ada anggota yang berhasil ditambahkan dari {group1.title} ke {group2.title}.")
        else:
            await message.reply(f"Berhasil menambahkan {added_count} anggota dari {group1.title} ke {group2.title}.")
    except Exception as e:
        await message.reply(f"Terjadi kesalahan: {e}")


# Jalankan bot
app.run()