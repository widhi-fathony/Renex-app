import streamlit as st
from abc import ABC, abstractmethod
import datetime
import uuid

# ==========================================
# BAGIAN 1: IMPLEMENTASI CLASS DIAGRAM (MODEL)
# ==========================================

# --- Abstract Class: Kendaraan ---
class Kendaraan(ABC):
    def __init__(self, id_k, merk, nopol, harga_sewa):
        self.id = id_k
        self.merk = merk
        self.nopol = nopol
        self.harga_sewa = harga_sewa
        self.is_available = True  # Default True

    def get_status(self):
        return self.is_available

    def get_harga(self):
        return self.harga_sewa

    @abstractmethod
    def get_detail_info(self):
        pass

# --- Concrete Classes (Inheritance) ---
class Hatchback(Kendaraan):
    def __init__(self, id_k, merk, nopol, harga_sewa, kapasitas_bagasi):
        super().__init__(id_k, merk, nopol, harga_sewa)
        self.kapasitas_bagasi = kapasitas_bagasi

    def get_detail_info(self):
        return f"Hatchback - Bagasi: {self.kapasitas_bagasi}L"

class Sedan(Kendaraan):
    def __init__(self, id_k, merk, nopol, harga_sewa, tingkat_kenyamanan):
        super().__init__(id_k, merk, nopol, harga_sewa)
        self.tingkat_kenyamanan = tingkat_kenyamanan # String, e.g., "Mewah"

    def get_detail_info(self):
        return f"Sedan - Kenyamanan: {self.tingkat_kenyamanan}"

class SUV(Kendaraan):
    def __init__(self, id_k, merk, nopol, harga_sewa, four_wheel_drive):
        super().__init__(id_k, merk, nopol, harga_sewa)
        self.four_wheel_drive = four_wheel_drive # Boolean

    def get_detail_info(self):
        wd_status = "4WD" if self.four_wheel_drive else "2WD"
        return f"SUV - {wd_status}"

# --- Class: User ---
class User:
    def __init__(self, user_id, nama, email, password):
        self.user_id = user_id
        self.nama = nama
        self.email = email
        self.password = password

    def get_profile(self):
        return f"{self.nama} ({self.email})"

# --- Class: Pembayaran ---
class Pembayaran:
    def __init__(self, pay_id, jumlah):
        self.pay_id = pay_id
        self.jumlah = jumlah
        self.tgl_bayar = datetime.datetime.now()
        self.status_sukses = False

    def verifikasi(self):
        # Simulasi verifikasi sukses
        self.status_sukses = True
        return True

# --- Class: Booking ---
class Booking:
    def __init__(self, booking_id, user, kendaraan, durasi_hari):
        self.booking_id = booking_id
        self.user = user  # Relasi: Melakukan
        self.kendaraan = kendaraan # Relasi: Memilih
        self.tgl_sewa = datetime.date.today()
        self.durasi_hari = durasi_hari
        self.total_biaya = self.hitung_total()
        self.status_booking = "Pending"
        self.pembayaran = None # Relasi: Memiliki (Composition/Aggregation)

    def hitung_total(self):
        return self.kendaraan.get_harga() * self.durasi_hari

    def set_pembayaran(self, pembayaran):
        self.pembayaran = pembayaran
        if pembayaran.status_sukses:
            self.status_booking = "Confirmed"

# --- Class: InventoryManager ---
class InventoryManager:
    def __init__(self):
        self.daftar_mobil = [] # List<Kendaraan>

    def tambah_unit(self, kendaraan):
        self.daftar_mobil.append(kendaraan)

    def cek_ketersediaan(self, id_k):
        for mobil in self.daftar_mobil:
            if mobil.id == id_k:
                return mobil.is_available
        return False

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

# --- Class: BookingService (Controller/Facade) ---
class BookingService:
    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager

    def buat_pesanan(self, user, kendaraan_id, durasi):
        mobil = self.inventory_manager.get_mobil_by_id(kendaraan_id)
        if mobil and mobil.get_status():
            booking_id = str(uuid.uuid4())[:8]
            booking = Booking(booking_id, user, mobil, durasi)
            # Update status mobil jadi tidak available sementara
            self.inventory_manager.update_stok(kendaraan_id, False)
            return booking
        return None

    def proses_pembayaran(self, booking, metode):
        # Membuat objek pembayaran
        pay_id = f"PAY-{str(uuid.uuid4())[:8]}"
        pembayaran = Pembayaran(pay_id, booking.total_biaya)
        
        # Verifikasi (Simulasi logika verifikasi)
        if pembayaran.verifikasi():
            booking.set_pembayaran(pembayaran)
            return pembayaran
        return None
    
    def batalkan_pesanan(self, booking):
        # Kembalikan stok mobil
        self.inventory_manager.update_stok(booking.kendaraan.id, True)
        booking.status_booking = "Cancelled"

# ==========================================
# BAGIAN 2: STREAMLIT INTERFACE (VIEW)
# ==========================================

# Inisialisasi Data Dummy (Hanya dijalankan sekali saat app start)
if 'inventory' not in st.session_state:
    inv = InventoryManager()
    inv.tambah_unit(Hatchback("C01", "Toyota Yaris", "B 1234 ABC", 300000, 250))
    inv.tambah_unit(Sedan("C02", "Honda Civic", "B 5678 DEF", 500000, "High"))
    inv.tambah_unit(SUV("C03", "Pajero Sport", "B 9999 XYZ", 700000, True))
    
    st.session_state.inventory = inv
    st.session_state.service = BookingService(inv)
    st.session_state.user = User("U01", "Budi Santoso", "budi@email.com", "pass123")
    st.session_state.my_bookings = [] # List untuk menyimpan booking user

def main():
    st.set_page_config(page_title="Sistem Rental Mobil", layout="wide")
    st.title("🚗 Sistem Rental Mobil")

    # Sidebar Navigation
    menu = st.sidebar.selectbox("Menu", ["Katalog Mobil", "Pesanan Saya", "Admin Inventory"])

    inv_manager = st.session_state.inventory
    service = st.session_state.service
    current_user = st.session_state.user

    # --- HALAMAN KATALOG MOBIL ---
    if menu == "Katalog Mobil":
        st.subheader(f"Halo, {current_user.nama}. Silakan pilih mobil.")
        
        mobil_list = inv_manager.get_all_mobil()
        
        cols = st.columns(3)
        for idx, mobil in enumerate(mobil_list):
            with cols[idx % 3]:
                status_color = "green" if mobil.is_available else "red"
                status_text = "Tersedia" if mobil.is_available else "Disewa"
                
                with st.container(border=True):
                    st.markdown(f"### {mobil.merk}")
                    st.caption(mobil.get_detail_info())
                    st.write(f"**Plat:** {mobil.nopol}")
                    st.write(f"**Harga:** Rp {mobil.harga_sewa:,.0f} /hari")
                    st.markdown(f"Status: :{status_color}[{status_text}]")
                    
                    if mobil.is_available:
                        durasi = st.number_input(f"Durasi (hari) - {mobil.merk}", min_value=1, value=1, key=f"d_{mobil.id}")
                        if st.button(f"Booking {mobil.merk}", key=f"btn_{mobil.id}"):
                            # Menggunakan BookingService untuk buat pesanan
                            booking = service.buat_pesanan(current_user, mobil.id, durasi)
                            if booking:
                                st.session_state.my_bookings.append(booking)
                                st.success(f"Berhasil booking {mobil.merk}!")
                                st.rerun()
                            else:
                                st.error("Gagal booking. Mobil tidak tersedia.")
                    else:
                        st.button("Tidak Tersedia", disabled=True, key=f"dis_{mobil.id}")

    # --- HALAMAN PESANAN SAYA ---
    elif menu == "Pesanan Saya":
        st.subheader("Riwayat Pesanan Anda")
        
        if not st.session_state.my_bookings:
            st.info("Belum ada pesanan.")
        else:
            for booking in st.session_state.my_bookings:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    
                    with c1:
                        st.write(f"**ID Booking:** {booking.booking_id}")
                        st.write(f"**Mobil:** {booking.kendaraan.merk} ({booking.kendaraan.nopol})")
                        st.write(f"**Total:** Rp {booking.total_biaya:,.0f} ({booking.durasi_hari} hari)")
                    
                    with c2:
                        st.write(f"**Status:** {booking.status_booking}")
                        if booking.pembayaran:
                            st.write(f"Paid: {booking.pembayaran.tgl_bayar.strftime('%Y-%m-%d')}")
                    
                    with c3:
                        # Logika Pembayaran
                        if booking.status_booking == "Pending":
                            if st.button("Bayar Sekarang", key=f"pay_{booking.booking_id}"):
                                service.proses_pembayaran(booking, "Transfer")
                                st.success("Pembayaran Berhasil!")
                                st.rerun()
                            
                            if st.button("Batalkan", key=f"cancel_{booking.booking_id}", type="primary"):
                                service.batalkan_pesanan(booking)
                                st.warning("Pesanan dibatalkan.")
                                st.rerun()

    # --- HALAMAN ADMIN (Untuk melihat Inventory) ---
    elif menu == "Admin Inventory":
        st.subheader("Manajemen Stok (Inventory Manager)")
        st.write("Daftar seluruh kendaraan di sistem:")
        
        data = []
        for m in inv_manager.get_all_mobil():
            data.append({
                "ID": m.id,
                "Merk": m.merk,
                "Nopol": m.nopol,
                "Kategori": type(m).__name__,
                "Status": "Available" if m.is_available else "Booked"
            })
        st.table(data)
        
        st.info("Fitur tambah unit bisa ditambahkan di sini memanggil `InventoryManager.tambahUnit`")

if __name__ == "__main__":
    main()
