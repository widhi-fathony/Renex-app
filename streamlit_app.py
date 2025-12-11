import streamlit as st
from abc import ABC, abstractmethod
import datetime
import uuid
import os

# ==========================================
# BAGIAN 1: MODEL & LOGIC (Backend)
# ==========================================

# --- Abstract Class: Kendaraan ---
class Kendaraan(ABC):
    # UPDATE: Menambah parameter image_url
    def __init__(self, id_k, merk, nopol, harga_sewa, image_url):
        self.id = id_k
        self.merk = merk
        self.nopol = nopol
        self.harga_sewa = harga_sewa
        self.image_url = image_url # Menyimpan link/path gambar
        self.is_available = True

    def get_status(self):
        return self.is_available

    def get_harga(self):
        return self.harga_sewa

    @abstractmethod
    def get_detail_info(self):
        pass

# --- Concrete Classes ---
class Hatchback(Kendaraan):
    def __init__(self, id_k, merk, nopol, harga_sewa, image_url, kapasitas_bagasi):
        super().__init__(id_k, merk, nopol, harga_sewa, image_url)
        self.kapasitas_bagasi = kapasitas_bagasi

    def get_detail_info(self):
        return f"Hatchback - Bagasi: {self.kapasitas_bagasi}L"

class Sedan(Kendaraan):
    def __init__(self, id_k, merk, nopol, harga_sewa, image_url, tingkat_kenyamanan):
        super().__init__(id_k, merk, nopol, harga_sewa, image_url)
        self.tingkat_kenyamanan = tingkat_kenyamanan

    def get_detail_info(self):
        return f"Sedan - Kenyamanan: {self.tingkat_kenyamanan}"

class SUV(Kendaraan):
    def __init__(self, id_k, merk, nopol, harga_sewa, image_url, four_wheel_drive):
        super().__init__(id_k, merk, nopol, harga_sewa, image_url)
        self.four_wheel_drive = four_wheel_drive

    def get_detail_info(self):
        wd_status = "4WD" if self.four_wheel_drive else "2WD"
        return f"SUV - {wd_status}"

# --- Class: User ---
class User:
    def __init__(self, user_id, nama, email):
        self.user_id = user_id
        self.nama = nama
        self.email = email

# --- Class: Pembayaran ---
class Pembayaran:
    def __init__(self, pay_id, jumlah, metode):
        self.pay_id = pay_id
        self.jumlah = jumlah
        self.metode = metode
        self.tgl_bayar = datetime.datetime.now()
        self.status_sukses = False

    def verifikasi(self):
        self.status_sukses = True
        return True

# --- Class: Booking ---
class Booking:
    def __init__(self, booking_id, user, kendaraan, durasi_hari):
        self.booking_id = booking_id
        self.user = user
        self.kendaraan = kendaraan
        self.tgl_sewa = datetime.date.today()
        self.durasi_hari = durasi_hari
        self.total_biaya = self.hitung_total()
        self.status_booking = "Active" 
        self.pembayaran = None

    def hitung_total(self):
        return self.kendaraan.get_harga() * self.durasi_hari

    def set_pembayaran(self, pembayaran):
        self.pembayaran = pembayaran
            
    def get_tgl_kembali(self):
        return self.tgl_sewa + datetime.timedelta(days=self.durasi_hari)

# --- Class: InventoryManager ---
class InventoryManager:
    def __init__(self):
        self.daftar_mobil = [] 

    def tambah_unit(self, kendaraan):
        self.daftar_mobil.append(kendaraan)

    def update_stok(self, id_k, status):
        for mobil in self.daftar_mobil:
            if mobil.id == id_k:
                mobil.is_available = status

    def get_all_mobil(self):
        return self.daftar_mobil
        
    def get_mobil_by_id(self, id_k):
        for mobil in self.daftar_mobil:
            if mobil.id == id_k:
                return mobil
        return None

# --- Class: BookingService ---
class BookingService:
    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager
        if 'all_bookings' not in st.session_state:
            st.session_state.all_bookings = []

    def buat_pesanan(self, user, kendaraan_id, durasi, metode_bayar):
        mobil = self.inventory_manager.get_mobil_by_id(kendaraan_id)
        if mobil and mobil.get_status():
            booking_id = str(uuid.uuid4())[:8]
            booking = Booking(booking_id, user, mobil, durasi)
            
            pay_id = f"PAY-{str(uuid.uuid4())[:6]}"
            pembayaran = Pembayaran(pay_id, booking.total_biaya, metode_bayar)
            pembayaran.verifikasi()
            booking.set_pembayaran(pembayaran)
            
            self.inventory_manager.update_stok(kendaraan_id, False)
            
            st.session_state.all_bookings.append(booking)
            return booking
        return None

    def selesaikan_pesanan(self, booking):
        self.inventory_manager.update_stok(booking.kendaraan.id, True)
        booking.status_booking = "Completed"

# ==========================================
# BAGIAN 2: STREAMLIT UI (Frontend)
# ==========================================

# URL Gambar Default (Placeholder Online)
IMG_HATCHBACK = "https://upload.wikimedia.org/wikipedia/commons/b/b5/2021_Toyota_Yaris_TRD_Sportivo_1.5_%28Indonesia%29_front_view_01.jpg"
IMG_SEDAN = "https://upload.wikimedia.org/wikipedia/commons/8/84/2018_Honda_Civic_1.5_E_hatchback_%28FK4%3B_01-23-2019%29%2C_South_Tangerang.jpg"
IMG_SUV = "https://assets.promediateknologi.id/crop/0x0:0x0/0x0/webp/photo/jawapos/2021/02/New-Pajero-Sport-Mistubishi.jpg"

# --- Init State ---
if 'inventory' not in st.session_state:
    inv = InventoryManager()
    
    # UPDATE: Menambahkan URL Gambar pada Data Dummy
    inv.tambah_unit(Hatchback("C01", "Toyota Yaris", "L 1234 ABC", 300000, IMG_HATCHBACK, 250))
    inv.tambah_unit(Sedan("C02", "Honda Civic", "L 5678 DEF", 500000, IMG_SEDAN, "High"))
    inv.tambah_unit(SUV("C03", "Pajero Sport", "L 9999 XYZ", 700000, IMG_SUV, True))
    
    st.session_state.inventory = inv
    st.session_state.service = BookingService(inv)

def login_page():
    st.title("🚗 Welcome to RENEX (Rental Mobil Express)")
    st.write("Sistem Rental Mobil Express")
    
    with st.form("login_form"):
        nama = st.text_input("Nama Lengkap")
        email = st.text_input("Email")
        password = st.text_input("Password")
        submitted = st.form_submit_button("Masuk Aplikasi")
        
        if submitted:
            if nama and email:
                user_id = str(uuid.uuid4())[:6]
                new_user = User(user_id, nama, email)
                st.session_state.user = new_user
                st.rerun()
            else:
                st.error("Mohon lengkapi nama dan email.")

def main_app():
    user = st.session_state.user
    st.sidebar.title(f"Hi, {user.nama}")
    
    menu = st.sidebar.radio("Menu", ["Katalog Mobil", "Pesanan Saya", "Admin Dashboard"])
    
    inv_manager = st.session_state.inventory
    service = st.session_state.service
    
  # ---------------- PAGE: KATALOG MOBIL ----------------
    if menu == "Katalog Mobil":
        st.header("Katalog Mobil Tersedia")
        st.info("Pilih mobil, tentukan durasi, dan lakukan pembayaran.")
        
        mobil_list = inv_manager.get_all_mobil()
        
        cols = st.columns(3)
        for idx, mobil in enumerate(mobil_list):
            with cols[idx % 3]:
                with st.container(border=True):
                    # Menampilkan Gambar Mobil
                    st.image(mobil.image_url, use_container_width=True)
                    
                    st.markdown(f"### {mobil.merk}")
                    st.caption(mobil.get_detail_info())
                    st.write(f"**Plat**: {mobil.nopol}")
                    st.write(f"**Harga**: Rp {mobil.harga_sewa:,.0f} /hari")
                    
                    if mobil.is_available:
                        st.success("Tersedia")
                        
                        # Key untuk state checkout dan penyimpanan durasi sementara
                        checkout_key = f"checkout_{mobil.id}"
                        duration_key = f"saved_duration_{mobil.id}" # <--- KEY BARU UNTUK MENYIMPAN DURASI

                        if checkout_key not in st.session_state:
                            st.session_state[checkout_key] = False

                        if not st.session_state[checkout_key]:
                            # TAHAP 1: INPUT DURASI
                            # Widget ini akan hilang saat masuk tahap 2, jadi kita perlu simpan nilainya
                            durasi_input = st.number_input(f"Durasi (Hari)", min_value=1, value=1, key=f"d_{mobil.id}")
                            
                            if st.button("Booking Sekarang", key=f"btn_book_{mobil.id}"):
                                # SIMPAN NILAI DURASI KE VARIABLE PERMANEN SEBELUM RERUN
                                st.session_state[duration_key] = durasi_input 
                                st.session_state[checkout_key] = True
                                st.rerun()
                        else:
                            # TAHAP 2: KONFIRMASI & PEMBAYARAN
                            st.markdown("---")
                            st.markdown("#### 💳 Konfirmasi")
                            
                            # AMBIL DARI VARIABLE YANG DISIMPAN TADI (Bukan dari key widget)
                            durasi_fix = st.session_state.get(duration_key, 1) 
                            
                            total_harga = mobil.harga_sewa * durasi_fix
                            
                            st.write(f"Sewa: **{durasi_fix} Hari**")
                            st.markdown(f"Total: **Rp {total_harga:,.0f}**")
                            
                            with st.form(key=f"form_bayar_{mobil.id}"):
                                metode = st.selectbox("Metode Pembayaran", ["QRIS", "Virtual Account", "Transfer Bank"])
                                c1, c2 = st.columns(2)
                                with c1:
                                    confirm = st.form_submit_button("✅ Bayar", type="primary")
                                with c2:
                                    cancel = st.form_submit_button("❌ Batal")
                                
                                if confirm:
                                    booking = service.buat_pesanan(user, mobil.id, durasi_fix, metode)
                                    if booking:
                                        st.session_state[checkout_key] = False
                                        st.success(f"Pembayaran via {metode} berhasil!")
                                        st.rerun()
                                if cancel:
                                    st.session_state[checkout_key] = False
                                    st.rerun()
                    else:
                        st.error("Sedang Disewa")
                        st.button("Tidak Tersedia", disabled=True, key=f"dis_{mobil.id}")

    # ---------------- PAGE: PESANAN SAYA ----------------
    elif menu == "Pesanan Saya":
        st.header("Riwayat Pesanan Saya")
        my_bookings = [b for b in st.session_state.all_bookings if b.user.user_id == user.user_id]
        
        if not my_bookings:
            st.warning("Anda belum menyewa mobil.")
        else:
            for booking in my_bookings:
                with st.expander(f"{booking.kendaraan.merk} ({booking.tgl_sewa})"):
                    # Tampilkan gambar kecil di riwayat
                    c_img, c_det = st.columns([1, 3])
                    with c_img:
                        st.image(booking.kendaraan.image_url, width=150)
                    with c_det:
                        st.write(f"**Total:** Rp {booking.total_biaya:,.0f} ({booking.durasi_hari} Hari)")
                        st.write(f"**Status:** {booking.status_booking}")
                        st.write(f"**Kembali:** {booking.get_tgl_kembali()}")

    # ---------------- PAGE: ADMIN DASHBOARD ----------------
    # ---------------- PAGE: ADMIN DASHBOARD ----------------
    elif menu == "Admin Dashboard":
        st.title("Panel Admin")
        
        tab1, tab2 = st.tabs(["Manajemen Pesanan", "Tambah Unit Mobil"])
        
        # --- TAB 1: TRACKING PESANAN ---
        with tab1:
            st.subheader("Tracking Pesanan")
            # Pastikan list booking ada di session state
            if 'all_bookings' not in st.session_state:
                st.session_state.all_bookings = []

            active_bookings = [b for b in st.session_state.all_bookings if b.status_booking == "Active"]
            
            if not active_bookings:
                st.info("Tidak ada mobil yang sedang disewa.")
            
            for b in active_bookings:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c1:
                        # Menampilkan gambar mobil
                        try:
                            st.image(b.kendaraan.image_url, use_container_width=True)
                        except:
                            st.write("No Image")
                    with c2:
                        st.markdown(f"**{b.kendaraan.merk}**")
                        st.caption(f"Penyewa: {b.user.nama}")
                        st.write(f"Kembali: **{b.get_tgl_kembali()}**")
                    with c3:
                        if st.button("Selesai & Restock", key=f"done_{b.booking_id}", type="primary"):
                            service.selesaikan_pesanan(b)
                            st.success("Sewa Selesai")
                            st.rerun()

        # --- TAB 2: INPUT MOBIL BARU ---
        with tab2:
            st.subheader("Input Mobil Baru")
            
            # 1. Cek folder penyimpanan gambar
            if not os.path.exists("car_images"):
                os.makedirs("car_images")

            # 2. Mulai Form
            with st.form("add_car_form"):
                tipe_mobil = st.selectbox("Tipe Mobil", ["Hatchback", "Sedan", "SUV"])
                
                col1, col2 = st.columns(2)
                with col1:
                    merk = st.text_input("Merk Mobil (Contoh: Honda Jazz)")
                    nopol = st.text_input("Nomor Polisi")
                with col2:
                    harga = st.number_input("Harga Sewa per Hari", min_value=100000, step=50000)
                    
                # Input Spesifik & Default Image
                extra_attr = None
                default_img = ""
                
                # Gunakan placeholder image online jika user tidak upload
                IMG_HATCHBACK = "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=500&q=60"
                IMG_SEDAN = "https://images.unsplash.com/photo-1555215695-3004980adade?auto=format&fit=crop&w=500&q=60"
                IMG_SUV = "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=500&q=60"
                
                if tipe_mobil == "Hatchback":
                    extra_attr = st.number_input("Kapasitas Bagasi (Liter)", min_value=100)
                    default_img = IMG_HATCHBACK
                elif tipe_mobil == "Sedan":
                    extra_attr = st.selectbox("Tingkat Kenyamanan", ["Standard", "High", "Luxury"])
                    default_img = IMG_SEDAN
                elif tipe_mobil == "SUV":
                    is_4wd = st.checkbox("Four Wheel Drive (4WD)?")
                    extra_attr = is_4wd
                    default_img = IMG_SUV

                st.write("---")
                st.write("Foto Kendaraan (Opsional)")
                
                # Upload File ada DI DALAM form
                uploaded_file = st.file_uploader("Upload Foto (JPG/PNG)", type=["jpg", "png", "jpeg"])
                
                # PENTING: Tombol submit ada DI DALAM form (sejajar dengan uploaded_file)
                submit_add = st.form_submit_button("Simpan ke Inventory")
                
                # --- LOGIKA PENYIMPANAN ---
                if submit_add:
                    if merk and nopol:
                        id_baru = f"C{len(inv_manager.daftar_mobil)+1:02d}"
                        
                        # Tentukan path gambar (Upload atau Default)
                        final_img_path = default_img 
                        
                        if uploaded_file is not None:
                            # Simpan file ke folder lokal
                            file_path = os.path.join("car_images", f"{id_baru}_{uploaded_file.name}")
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            final_img_path = file_path 
                        
                        # Buat Objek Mobil
                        new_car = None
                        if tipe_mobil == "Hatchback":
                            new_car = Hatchback(id_baru, merk, nopol, harga, final_img_path, extra_attr)
                        elif tipe_mobil == "Sedan":
                            new_car = Sedan(id_baru, merk, nopol, harga, final_img_path, extra_attr)
                        elif tipe_mobil == "SUV":
                            new_car = SUV(id_baru, merk, nopol, harga, final_img_path, extra_attr)
                        
                        # Simpan ke Inventory
                        inv_manager.tambah_unit(new_car)
                        st.success(f"Berhasil menambahkan {merk}!")
                        st.rerun()
                    else:
                        st.error("Mohon lengkapi Merk dan Nomor Polisi!")

# --- Main Execution ---
def main():
    st.set_page_config(page_title="Rental Mobil App", layout="wide")
    
    if 'user' not in st.session_state:
        login_page()
    else:
        main_app()
        if st.sidebar.button("Logout"):
            del st.session_state['user']
            st.rerun()

if __name__ == "__main__":
    main()
