import streamlit as st
from abc import ABC, abstractmethod
import datetime
import uuid

# ==========================================
# BAGIAN 1: MODEL & LOGIC (Backend)
# ==========================================

# --- Abstract Class: Kendaraan ---
class Kendaraan(ABC):
    def __init__(self, id_k, merk, nopol, harga_sewa):
        self.id = id_k
        self.merk = merk
        self.nopol = nopol
        self.harga_sewa = harga_sewa
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
    def __init__(self, id_k, merk, nopol, harga_sewa, kapasitas_bagasi):
        super().__init__(id_k, merk, nopol, harga_sewa)
        self.kapasitas_bagasi = kapasitas_bagasi

    def get_detail_info(self):
        return f"Hatchback - Bagasi: {self.kapasitas_bagasi}L"

class Sedan(Kendaraan):
    def __init__(self, id_k, merk, nopol, harga_sewa, tingkat_kenyamanan):
        super().__init__(id_k, merk, nopol, harga_sewa)
        self.tingkat_kenyamanan = tingkat_kenyamanan

    def get_detail_info(self):
        return f"Sedan - Kenyamanan: {self.tingkat_kenyamanan}"

class SUV(Kendaraan):
    def __init__(self, id_k, merk, nopol, harga_sewa, four_wheel_drive):
        super().__init__(id_k, merk, nopol, harga_sewa)
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
    def __init__(self, pay_id, jumlah):
        self.pay_id = pay_id
        self.jumlah = jumlah
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
        self.status_booking = "Active" # Status: Active, Completed, Cancelled
        self.pembayaran = None

    def hitung_total(self):
        return self.kendaraan.get_harga() * self.durasi_hari

    def set_pembayaran(self, pembayaran):
        self.pembayaran = pembayaran
        if pembayaran.status_sukses:
            # Di real app, status mungkin berubah jadi 'Paid', tapi di sini kita anggap Active
            pass
            
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
        # Simpan semua booking di sini agar admin bisa akses
        if 'all_bookings' not in st.session_state:
            st.session_state.all_bookings = []

    def buat_pesanan(self, user, kendaraan_id, durasi):
        mobil = self.inventory_manager.get_mobil_by_id(kendaraan_id)
        if mobil and mobil.get_status():
            booking_id = str(uuid.uuid4())[:8]
            booking = Booking(booking_id, user, mobil, durasi)
            
            # Update stok mobil jadi tidak available
            self.inventory_manager.update_stok(kendaraan_id, False)
            
            # Simpan ke global list
            st.session_state.all_bookings.append(booking)
            return booking
        return None

    def selesaikan_pesanan(self, booking):
        # Admin menandai mobil sudah kembali
        self.inventory_manager.update_stok(booking.kendaraan.id, True)
        booking.status_booking = "Completed"

# ==========================================
# BAGIAN 2: STREAMLIT UI (Frontend)
# ==========================================

# --- Init State ---
if 'inventory' not in st.session_state:
    inv = InventoryManager()
    # Data Awal
    inv.tambah_unit(Hatchback("C01", "Toyota Yaris", "L 1234 ABC", 300000, 250))
    inv.tambah_unit(Sedan("C02", "Honda Civic", "L 5678 DEF", 500000, "High"))
    inv.tambah_unit(SUV("C03", "Pajero Sport", "L 9999 XYZ", 700000, True))
    
    st.session_state.inventory = inv
    st.session_state.service = BookingService(inv)

def login_page():
    st.title("🚗 Welcome to RENEX (Rental Mobil Express)")
    st.write("Silakan isi data diri Anda sebelum melanjutkan.")
    
    with st.form("login_form"):
        nama = st.text_input("Nama Lengkap")
        email = st.text_input("Email")
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
    
    # Menu Navigasi
    menu = st.sidebar.radio("Menu", ["Katalog Mobil", "Pesanan Saya", "Admin Dashboard"])
    
    inv_manager = st.session_state.inventory
    service = st.session_state.service
    
    # ---------------- PAGE: KATALOG MOBIL ----------------
    if menu == "Katalog Mobil":
        st.header("Katalog Mobil Tersedia")
        st.info("Pilih mobil dan tentukan durasi sewa.")
        
        mobil_list = inv_manager.get_all_mobil()
        
        # Grid layout
        cols = st.columns(3)
        for idx, mobil in enumerate(mobil_list):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {mobil.merk}")
                    st.caption(mobil.get_detail_info())
                    st.write(f"**Plat**: {mobil.nopol}")
                    st.write(f"**Harga**: Rp {mobil.harga_sewa:,.0f} /hari")
                    
                    if mobil.is_available:
                        st.success("Tersedia")
                        # REVISI 3: User menentukan durasi di dashboard
                        durasi = st.number_input(f"Durasi (Hari)", min_value=1, value=1, key=f"d_{mobil.id}")
                        
                        if st.button("Booking Sekarang", key=f"btn_{mobil.id}"):
                            booking = service.buat_pesanan(user, mobil.id, durasi)
                            if booking:
                                st.success(f"Berhasil booking {mobil.merk} selama {durasi} hari!")
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
                with st.expander(f"{booking.kendaraan.merk} - {booking.status_booking}"):
                    st.write(f"**Durasi:** {booking.durasi_hari} Hari")
                    st.write(f"**Total Biaya:** Rp {booking.total_biaya:,.0f}")
                    st.write(f"**Tanggal Sewa:** {booking.tgl_sewa}")
                    st.write(f"**Perkiraan Kembali:** {booking.get_tgl_kembali()}")

    # ---------------- PAGE: ADMIN DASHBOARD ----------------
    elif menu == "Admin Dashboard":
        st.title("Panel Admin")
        
        tab1, tab2 = st.tabs(["Manajemen Pesanan (Tracking)", "Tambah Unit Mobil"])
        
        # --- SUB-PAGE: TRACKING PESANAN ---
        with tab1:
            st.subheader("Daftar Pesanan Aktif")
            st.write("Monitor durasi sewa dan selesaikan pesanan jika mobil sudah dikembalikan.")
            
            active_bookings = [b for b in st.session_state.all_bookings if b.status_booking == "Active"]
            
            if not active_bookings:
                st.info("Tidak ada mobil yang sedang disewa saat ini.")
            
            for b in active_bookings:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        st.markdown(f"**{b.kendaraan.merk}** ({b.kendaraan.nopol})")
                        st.caption(f"Penyewa: {b.user.nama}")
                    with c2:
                        st.write(f"📅 Mulai: {b.tgl_sewa}")
                        st.write(f"⏳ Durasi: **{b.durasi_hari} Hari**")
                        st.write(f"🔙 Kembali: **{b.get_tgl_kembali()}**")
                    with c3:
                        # REVISI 2: Menandai booking selesai & mobil available kembali
                        if st.button("Selesaikan Sewa", key=f"done_{b.booking_id}", type="primary"):
                            service.selesaikan_pesanan(b)
                            st.success("Mobil telah dikembalikan & stok diperbarui!")
                            st.rerun()

        # --- SUB-PAGE: TAMBAH MOBIL ---
        with tab2:
            st.subheader("Input Mobil Baru")
            # REVISI 2: Admin menambah tipe mobil
            with st.form("add_car_form"):
                tipe_mobil = st.selectbox("Tipe Mobil", ["Hatchback", "Sedan", "SUV"])
                col1, col2 = st.columns(2)
                with col1:
                    merk = st.text_input("Merk Mobil (Contoh: Honda Jazz)")
                    nopol = st.text_input("Nomor Polisi")
                with col2:
                    harga = st.number_input("Harga Sewa per Hari", min_value=100000, step=50000)
                    
                # Input Spesifik berdasarkan tipe
                extra_attr = None
                if tipe_mobil == "Hatchback":
                    extra_attr = st.number_input("Kapasitas Bagasi (Liter)", min_value=100)
                elif tipe_mobil == "Sedan":
                    extra_attr = st.selectbox("Tingkat Kenyamanan", ["Standard", "High", "Luxury"])
                elif tipe_mobil == "SUV":
                    is_4wd = st.checkbox("Four Wheel Drive (4WD)?")
                    extra_attr = is_4wd

                submit_add = st.form_submit_button("Simpan ke Inventory")
                
                if submit_add and merk and nopol:
                    id_baru = f"C{len(inv_manager.daftar_mobil)+1:02d}"
                    new_car = None
                    
                    if tipe_mobil == "Hatchback":
                        new_car = Hatchback(id_baru, merk, nopol, harga, extra_attr)
                    elif tipe_mobil == "Sedan":
                        new_car = Sedan(id_baru, merk, nopol, harga, extra_attr)
                    elif tipe_mobil == "SUV":
                        new_car = SUV(id_baru, merk, nopol, harga, extra_attr)
                    
                    inv_manager.tambah_unit(new_car)
                    st.success(f"Berhasil menambahkan {merk} ke database!")
                    st.rerun()

# --- Main Execution ---
def main():
    st.set_page_config(page_title="Rental Mobil App", layout="wide")
    
    # REVISI 1: Cek apakah user sudah login
    if 'user' not in st.session_state:
        login_page()
    else:
        main_app()
        # Tombol Logout sederhana di sidebar bawah
        if st.sidebar.button("Logout"):
            del st.session_state['user']
            st.rerun()

if __name__ == "__main__":
    main()
