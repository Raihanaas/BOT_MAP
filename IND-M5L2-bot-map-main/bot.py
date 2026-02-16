from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN

# Menginisiasi pengelola database
manager = DB_Map("database.db")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot started")

@bot.command()
async def start(ctx: commands.Context):
    await ctx.send(f"Halo, {ctx.author.name}. Masukkan !help_me untuk mengeksplorasi daftar perintah yang tersedia")

@bot.command()
async def help_me(ctx: commands.Context):
    help_text = (
        "**Daftar Perintah Bot Peta:**\n"
        "`!start` - Memulai interaksi dengan bot\n"
        "`!remember_city [Nama Kota]` - Menyimpan kota ke daftar favorit Anda\n"
        "`!show_city [Nama Kota]` - Menampilkan lokasi kota tertentu di peta\n"
        "`!show_my_cities` - Menampilkan semua kota yang sudah Anda simpan di satu peta\n"
        "`!help_me` - Menampilkan pesan bantuan ini"
    )
    await ctx.send(help_text)

@bot.command()
async def show_city(ctx: commands.Context, *, city_name=""):
    if not city_name:
        await ctx.send("Silakan masukkan nama kota. Contoh: `!show_city Jakarta`平衡")
        return

    path = f"{ctx.author.id}_city.png"
    # Membuat peta hanya dengan satu kota tersebut
    manager.create_graph(path, [city_name])
    
    # Mengirimkan file gambar ke Discord
    with open(path, 'rb') as f:
        picture = discord.File(f)
        await ctx.send(f"Berikut adalah lokasi dari {city_name}:", file=picture)
    
@bot.command()
async def show_my_cities(ctx: commands.Context):
    cities = manager.select_cities(ctx.author.id)  # Mengambil daftar kota yang diingat oleh pengguna

    if not cities:
        await ctx.send("Anda belum menyimpan kota favorit.")
        return

    path = f"{ctx.author.id}_my_cities.png"
    manager.create_graph(path, cities)
    
    with open(path, 'rb') as f:
        picture = discord.File(f)
        await ctx.send(f"Berikut adalah peta kota-kota favorit Anda:", file=picture)
        
@bot.command()
async def remember_city(ctx: commands.Context, *, city_name=""):
    if manager.add_city(ctx.author.id, city_name):  # Memeriksa apakah kota ada dalam database; jika ya, menambahkannya ke memori pengguna
        await ctx.send(f'Kota {city_name} telah berhasil disimpan!')
    else:
        await ctx.send("Format tidak benar. Silakan masukkan nama kota dalam bahasa Inggris, dengan spasi setelah perintah.")

if __name__ == "__main__":
    bot.run(TOKEN)