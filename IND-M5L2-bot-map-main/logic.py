import sqlite3
import matplotlib

matplotlib.use('Agg')  # Menginstal backend Matplotlib untuk menyimpan file dalam memori tanpa menampilkan jendela
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  # Mengimpor modul yang akan memungkinkan kita bekerja dengan proyeksi peta

class DB_Map():
    def __init__(self, database):
        self.database = database  # Menginisiasi jalur database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)  # Menghubungkan ke database
        with conn:
            # Membuat tabel, jika tidak ada, untuk menyimpan kota pengguna
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  # Menyimpan perubahan

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mencari kota dalam database berdasarkan nama
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Menambahkan kota ke daftar kota pengguna
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  # Menunjukkan bahwa operasi berhasil
            else:
                return 0  # Menunjukkan bahwa kota tidak ditemukan

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Memilih semua kota pengguna
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  # Mengembalikan daftar kota pengguna

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mendapatkan koordinat kota berdasarkan nama
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  # Mengembalikan koordinat kota

    def create_graph(self, path, cities):
        # Membuat peta dengan kota-kota yang diberikan
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Menambahkan fitur peta dasar
        ax.stock_img()
        ax.coastlines()

        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                # Menggambar titik kota (lng adalah X, lat adalah Y)
                ax.plot(lng, lat, 'ro', markersize=5, transform=ccrs.PlateCarree())
                # Menambahkan label nama kota
                ax.text(lng + 1, lat + 1, city, transform=ccrs.PlateCarree(), fontsize=9)

        # Menyimpan peta ke jalur file yang ditentukan
        plt.savefig(path)
        plt.close()
        pass

    def draw_distance(self, city1, city2, path):
        # Menggambar garis antara dua kota untuk menampilkan jarak
        # Mendapatkan koordinat kedua kota
        coord1 = self.get_coordinates(city1)
        coord2 = self.get_coordinates(city2)

        if coord1 and coord2:
            fig = plt.figure(figsize=(10, 5))
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.stock_img()
            ax.coastlines()

            lats = [coord1[0], coord2[0]]
            lngs = [coord1[1], coord2[1]]

            # Menggambar garis antara dua kota (Geodetic untuk garis melengkung mengikuti bumi)
            ax.plot(lngs, lats, color='blue', linewidth=2, marker='o',
                    transform=ccrs.Geodetic())
            
            # Menambahkan label
            ax.text(lngs[0], lats[0], city1, transform=ccrs.PlateCarree())
            ax.text(lngs[1], lats[1], city2, transform=ccrs.PlateCarree())

            plt.savefig(path)
            plt.close()
        pass


if __name__ == "__main__":
    m = DB_Map("database.db")  # Membuat objek yang akan berinteraksi dengan database
    m.create_user_table()   # Membuat tabel dengan kota pengguna, jika tidak sudah ada