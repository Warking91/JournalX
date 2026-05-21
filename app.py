import streamlit as st
import sqlite3
import os

# 1. Postavke stranice
st.set_page_config(page_title="JournalX Panel", page_icon="📝", layout="wide")

# 2. Inicijalizacija SQLite baze podataka
def inicijaliziraj_bazu():
    conn = sqlite3.connect("journalx.db")
    c = conn.cursor()
    # Kreiranje tablice za korisnike ako ne postoji
    c.execute('''
        CREATE TABLE IF NOT EXISTS korisnici (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            uloga TEXT,
            status TEXT
        )
    ''')
    
    # Unos zadanih računa ako je baza prazna
    c.execute("SELECT COUNT(*) FROM korisnici")
    if c.fetchone() == 0:
        c.execute("INSERT INTO korisnici (username, password, email, uloga, status) VALUES ('bog', 'bog123', 'bog@journalx.com', 'Bog', 'Aktivan')")
        c.execute("INSERT INTO korisnici (username, password, email, uloga, status) VALUES ('mod', 'mod123', 'mod@journalx.com', 'Mod', 'Aktivan')")
        c.execute("INSERT INTO korisnici (username, password, email, uloga, status) VALUES ('customer', 'user123', 'user@journalx.com', 'Customer', 'Aktivan')")
        conn.commit()
    conn.close()

inicijaliziraj_bazu()

# Pomoćne funkcije za rad s bazom
def provjeri_korisnika(username, password):
    conn = sqlite3.connect("journalx.db")
    c = conn.cursor()
    c.execute("SELECT uloga FROM korisnici WHERE username=? AND password=?", (username, password))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

def dohvati_sve_korisnike():
    conn = sqlite3.connect("journalx.db")
    c = conn.cursor()
    c.execute("SELECT username, email, uloga, status FROM korisnici")
    res = c.fetchall()
    conn.close()
    return res

def dodaj_korisnika(username, password, email, uloga, status):
    try:
        conn = sqlite3.connect("journalx.db")
        c = conn.cursor()
        c.execute("INSERT INTO motifs (username, password, email, uloga, status) VALUES (?, ?, ?, ?, ?)", 
                  (username, password, email, uloga, status))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# 3. Login i Registracija Forma
def login_i_registracija():
    st.subheader("🔒 Pristup JournalX Panelu")
    izbor = st.radio("Odaberite akciju", ["Prijava", "Registracija"], horizontal=True)
    
    if izbor == "Prijava":
        username = st.text_input("Korisničko ime")
        password = st.text_input("Lozinka", type="password")
        
        if st.button("Prijavi se", use_container_width=True):
            uloga = provjeri_korisnika(username, password)
            if uloga:
                st.session_state.uloga = uloga
                st.session_state.korisnik = username
                st.session_state.prijavljen = True
                st.success(f"Uspješna prijava! Dobrodošao {username}")
                st.rerun()
            else:
                st.error("Pogrešno korisničko ime ili lozinka!")
                
    elif izbor == "Registracija":
        novi_user = st.text_input("Željeno korisničko ime")
        novi_email = st.text_input("Vaš Email")
        nova_sifra = st.text_input("Željena lozinka", type="password")
        
        if st.button("Registriraj se", use_container_width=True):
            if novi_user and novi_email and nova_sifra:
                # Svi novi registrirani su automatski 'Customer' na čekanju
                uspjeh = dodaj_korisnika(novi_user, nova_sifra, novi_email, "Customer", "Na čekanju")
                if uspjeh:
                    st.success("Registracija uspješna! Bog ili Mod moraju odobriti vaš račun.")
                else:
                    st.error("Korisničko ime je već zauzeto!")
            else:
                st.warning("Molimo ispunite sva polja.")

# Upravljanje prikazom stranice
if "prijavljen" not in st.session_state:
    login_i_registracija()
else:
    # Sidebar za navigaciju
    st.sidebar.title("JournalX Medij")
    st.sidebar.write(f"Korisnik: **{st.session_state.korisnik}**")
    st.sidebar.write(f"Ranga: **{st.session_state.uloga}**")
    
    if st.sidebar.button("Odjavi se", use_container_width=True):
        del st.session_state.prijavljen
        del st.session_state.uloga
        del st.session_state.korisnik
        st.rerun()

    # --- 👑 BOG PANEL (SUPER ADMIN) ---
    if st.session_state.uloga == "Bog":
        st.title("⚡ BOG PANEL (Potpuna Kontrola)")
        
        tab1, tab2, tab3 = st.tabs(["📊 Statistika", "👥 Korisnici & Dozvole", "⚙️ Postavke"])
        
        with tab1:
            korisnici = dohvati_sve_korisnike()
            col1, col2 = st.columns(2)
            col1.metric("Ukupno Korisnika", len(korisnici))
            col2.metric("Status Baze", "Online / Aktivna")
            
        with tab2:
            st.write("Svi registrirani u bazi podataka:")
            for u in korisnici:
                st.text(f"👤 Korisnik: {u[0]} | Email: {u[1]} | Uloga: {u[2]} | Status: {u[3]}")
                
            st.markdown("---")
            st.subheader("➕ Brzo dodavanje novog tima (Mod/Klijent)")
            add_user = st.text_input("Korisničko ime za dodati")
            add_pass = st.text_input("Lozinka za dodati", type="password")
            add_role = st.selectbox("Dodijeli ulogu", ["Customer", "Mod", "Bog"])
            
            if st.button("Spremi novog člana"):
                if add_user and add_pass:
                    dodaj_korisnika(add_user, add_pass, f"{add_user}@jx.com", add_role, "Aktivan")
                    st.success("Član uspješno dodan u bazu!")
                    st.rerun()
        with tab3:
            st.warning("Postavke gašenja sustava u razvoju.")

    # --- 🛠️ MOD PANEL (MODERATOR) ---
    elif st.session_state.uloga == "Mod":
        st.title("🛡️ MOD PANEL (Pregled i Moderacija)")
        st.write("Ovdje možete nadgledati registrirane korisnike.")
        korisnici = dohvati_sve_korisnike()
        st.dataframe(korisnici, use_container_width=True)

    # --- 👤 CUSTOMERS PANEL (KLIJENTI) ---
    elif st.session_state.uloga == "Customer":
        st.title("🚀 Vaš Korisnički Panel")
        st.write("Dobrodošli u JournalX aplikacijski centar.")
        
        st.subheader("📥 Preuzimanje programa")
        st.info("Ovdje možete sigurno preuzeti naš klijent softver.")
        
        # OVDJE ZALIJEPITE SVOJ LINK S GOOGLE DRIVE-A UMJESTO '#'
        st.link_button("Preuzmi JX.exe", "https://google.com...", use_container_width=True)
