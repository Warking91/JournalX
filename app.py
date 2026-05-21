import streamlit as st
import sqlite3
import os

# 1. Postavke stranice
st.set_page_config(page_title="JournalX Panel", page_icon="📝", layout="wide")

# --- NOVI COOL LOGO PRILAGOĐEN ZA PYTHON 3.14 ---
logo_html = (
    "<style>"
    ".logo-kontejner { text-align: center; padding: 20px; margin-bottom: 20px; }"
    ".logo-tekst { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; "
    "font-size: 55px; font-weight: 800; letter-spacing: 2px; color: #1E3A8A; "
    "text-transform: uppercase; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }"
    ".logo-x { color: #DC2626; font-size: 65px; font-style: italic; "
    "text-shadow: 3px 3px 6px rgba(220, 38, 38, 0.3); }"
    ".podnaslov { font-family: 'Segoe UI', sans-serif; font-size: 14px; "
    "color: #6B7280; letter-spacing: 5px; text-transform: uppercase; margin-top: -15px; }"
    "</style>"
    "<div class='logo-kontejner'>"
    "<div class='logo-tekst'>Journal<span class='logo-x'>X</span></div>"
    "<div class='podnaslov'>Aplikacijski Centar</div>"
    "</div>"
)
st.markdown(logo_html, unsafe_html=True)


# 2. Inicijalizacija SQLite baze podataka (v2)
def inicijaliziraj_bazu():
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    
    # Kreiranje tablice za korisnike
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
    
    # Kreiranje tablice za programe
    c.execute('''
        CREATE TABLE IF NOT EXISTS programi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ime TEXT,
            opis TEXT,
            link TEXT
        )
    ''')
    
    # Unos zadanih računa
    c.execute("SELECT COUNT(*) FROM korisnici")
    if c.fetchone() == 0:
        c.execute("INSERT INTO korisnici (username, password, email, uloga, status) VALUES ('bog', 'bog123', 'bog@journalx.com', 'Bog', 'Aktivan')")
        c.execute("INSERT INTO korisnici (username, password, email, uloga, status) VALUES ('mod', 'mod123', 'mod@journalx.com', 'Mod', 'Aktivan')")
        c.execute("INSERT INTO korisnici (username, password, email, uloga, status) VALUES ('customer', 'user123', 'user@journalx.com', 'Customer', 'Aktivan')")
        
        # Unos prvog zadanog programa
        c.execute("INSERT INTO programi (ime, opis, link) VALUES ('JournalX klijent', 'Glavni šifrirani program za upravljanje JournalX sistemom.', 'https://google.com...')")
        conn.commit()
        
    conn.close()

inicijaliziraj_bazu()

# --- POMOĆNE FUNKCIJE ZA KORISNIKE ---
def provjeri_korisnika(username, password):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("SELECT uloga, status FROM korisnici WHERE username=? AND password=?", (username, password))
    res = c.fetchone()
    conn.close()
    return res if res else None

def dohvati_sve_korisnike():
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("SELECT id, username, email, uloga, status FROM korisnici WHERE uloga != 'Bog'")
    res = c.fetchall()
    conn.close()
    return res

def dodaj_korisnika(username, password, email, uloga, status):
    try:
        conn = sqlite3.connect("journalx_v2.db")
        c = conn.cursor()
        c.execute("INSERT INTO korisnici (username, password, email, uloga, status) VALUES (?, ?, ?, ?, ?)", 
                  (username, password, email, uloga, status))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def azuriraj_status_korisnika(korisnik_id, novi_status):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("UPDATE korisnici SET status=? WHERE id=?", (novi_status, korisnik_id))
    conn.commit()
    conn.close()

def azuriraj_ulogu_korisnika(korisnik_id, nova_uloga):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("UPDATE korisnici SET uloga=? WHERE id=?", (nova_uloga, korisnik_id))
    conn.commit()
    conn.close()

# --- POMOĆNE FUNKCIJE ZA PROGRAME ---
def dodaj_program(ime, opis, link):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("INSERT INTO programi (ime, opis, link) VALUES (?, ?, ?)", (ime, opis, link))
    conn.commit()
    conn.close()

def dohvati_sve_programe():
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("SELECT id, ime, opis, link FROM programi ORDER BY id DESC")
    res = c.fetchall()
    conn.close()
    return res

def obrisi_program(program_id):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("DELETE FROM programi WHERE id=?", (program_id,))
    conn.commit()
    conn.close()


# 3. Login i Registracija Forma
def login_i_registracija():
    izbor = st.radio("Odaberite akciju", ["Prijava", "Registracija"], horizontal=True)
    
    if izbor == "Prijava":
        username = st.text_input("Korisničko ime")
        password = st.text_input("Lozinka", type="password")
        
        if st.button("Prijavi se", use_container_width=True):
            rezultat = provjeri_korisnika(username, password)
            if rezultat:
                uloga, status = rezultat
                if status == "Blokiran":
                    st.error("Vaš račun je blokiran od strane administratora!")
                else:
                    st.session_state.uloga = uloga
                    st.session_state.status = status
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
                uspjeh = dodaj_korisnika(novi_user, nova_sifra, novi_email, "Customer", "Na čekanju")
                if uspjeh:
                    st.success("🚀 Registracija uspješna! Vaš račun je na čekanju dok ga Bog ili Mod ne odobre.")
                else:
                    st.error("Korisničko ime je već zauzeto!")
            else:
                st.warning("Molimo ispunite sva polja.")


# Upravljanje prikazom stranice nakon prijave
if "prijavljen" not in st.session_state:
    login_i_registracija()
else:
    # Sidebar za navigaciju
    st.sidebar.title("💥 JournalX")
    st.sidebar.write(f"Korisnik: **{st.session_state.korisnik}**")
    st.sidebar.write(f"Rang: **{st.session_state.uloga}**")
    
    # Ponovno dohvaćanje statusa iz baze za trenutnog korisnika
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("SELECT status FROM korisnici WHERE username=?", (st.session_state.korisnik,))
    trenutni_status_db = c.fetchone()
    conn.close()
    
    trenutni_status = trenutni_status_db[0] if trenutni_status_db else "Na čekanju"
    st.sidebar.write(f"Status računa: **{trenutni_status}**")
    
    if st.sidebar.button("Odjavi se", use_container_width=True):
        del st.session_state.prijavljen
        del st.session_state.uloga
        del st.session_state.korisnik
        st.rerun()

    # --- 👑 BOG PANEL (SUPER ADMIN) ---
    if st.session_state.uloga == "Bog":
        st.title("⚡ BOG PANEL (Potpuna Kontrola)")
        
        tab1, tab2, tab3 = st.tabs(["📊 Statistika", "👥 Odobravanje & Korisnici", "📦 Upravljanje Programima"])
        
        with tab1:
            korisnici = dohvati_sve_korisnike()
            programi = dohvati_sve_programe()
            col1, col2 = st.columns(2)
            col1.metric("Ukupno Korisnika (bez Boga)", len(korisnici))
            col2.metric("Ukupno Programa na sajtu", len(programi))
            
        with tab2:
            st.subheader("👥 Upravljanje korisničkim računima i ulogama")
            korisnici_lista = dohvati_sve_korisnike()
            
            if len(korisnici_lista) == 0:
                st.info("Nema registriranih korisnika u bazi.")
            else:
                for k in korisnici_lista:
                    k_id, k_user, k_email, k_uloga, k_status = k
                    col_detalji, col_akcija_status, col_akcija_uloga = st.columns(3)
                    
                    with col_detalji:
                        st.markdown(f"👤 **{k_user}** ({k_email})")
                        st.caption(f"Trenutni Rang: {k_uloga} | Status: {k_status}")
                    
                    with col_akcija_status:
                        if k_status == "Na čekanju" or k_status == "Blokiran":
                            if st.button("✅ Odobri", key=f"act_{k_id}"):
                                azuriraj_status_korisnika(k_id, "Aktivan")
                                st.success(f"{k_user} odobren!")
                                st.rerun()
                        if k_status == "Aktivan":
                            if st.button("🚫 Blokiraj", key=f"block_{k_id}"):
                                azuriraj_status_korisnika(k_id, "Blokiran")
                                st.error(f"{k_user} blokiran!")
                                st.rerun()
                                
                    with col_akcija_uloga:
                        if k_uloga == "Customer":
                            if st.button("🛡️ Unaprijedi u Mod", key=f"mod_{k_id}"):
                                azuriraj_ulogu_korisnika(k_id, "Mod")
                                st.success(f"{k_user} je postao Moderator!")
                                st.rerun()
                        if k_uloga == "Mod":
                            if st.button("👤 Smanji u Korisnika", key=f"cust_{k_id}"):
                                azuriraj_ulogu_korisnika(k_id, "Customer")
                                st.info(f"{k_user} vraćen na Customer rang.")
                                st.rerun()
                    st.markdown("---")
                    
        with tab3:
            st.subheader("➕ Dodaj novi program / datoteku na sajt")
            prog_ime = st.text_input("Ime programa (npr. JurnalX v2.0)")
            prog_opis = st.text_area("Opis programa (Za šta služi, šta je novo...)")
            prog_link = st.text_input("Google Drive link za download")
            
            if st.button("Objavi program na sajt", use_container_width=True):
                if prog_ime and prog_link:
                    dodaj_program(prog_ime, prog_opis, prog_link)
                    st.success(f"Uspješno dodan program: {prog_ime}!")
                    st.rerun()
                    
            st.markdown("---")
            st.subheader("🗑️ Trenutni programi na sajtu (Pregled i brisanje)")
            trenutni_programi = dohvati_sve_programe()
            
            for p in trenutni_programi:
                p_id, p_ime, p_opis, p_link = p
                col_info, col_btn = st.columns(2)
                with col_info:
                    st.markdown(f"**{p_ime}**")
                    st.caption(f"Opis: {p_opis} | Link: {p_link}")
                with col_btn:
                    if st.button("Obriši", key=f"del_{p_id}"):
                        obrisi_program(p_id)
                        st.success("Program uklonjen!")
                        st.rerun()

    # --- 🛠️ MOD PANEL (MODERATOR) ---
    elif st.session_state.uloga == "Mod":
        st.title("🛡️ MOD PANEL (Pregled i Moderacija)")
        st.write("Kao moderator, možete odobravati nove korisnike koji su na čekanju.")
        
        korisnici_lista = dohvati_sve_korisnike()
        na_cekanju = [k for k in korisnici_lista if k[4] == "Na čekanju"]
        
        if len(na_cekanju) == 0:
            st.success("✨ Nema novih korisnika na čekanju za odobrenje.")
        else:
            st.subheader("📌 Korisnici koji čekaju odobrenje:")
            for k in na_cekanju:
                k_id, k_user, k_email, _, k_status = k
                col_m_detalji, col_m_btn = st.columns(2)
                with col_m_detalji:
                    st.write(f"👤 **{k_user}** | Email: {k_email}")
                with col_m_btn:
                    if st.button("✅ Odobri račun", key=f"mod_act_{k_id}"):
                        azuriraj_status_korisnika(k_id, "Aktivan")
                        st.success(f"Korisnik {k_user} uspješno odobren!")
                        st.rerun()
                st.markdown("---")

    # --- 👤 CUSTOMERS PANEL (KLIJENTI) ---
    elif st.session_state.uloga == "Customer":
        st.title("🚀 Vaš Korisnički Panel")
        
        if trenutni_status == "Na čekanju":
            st.warning("🔒 Vaš račun je uspješno kreiran, ali trenutno ima status **'Na čekanju'**.")
            st.info("Molimo sačekajte da vlasnik (Bog) ili Moderator odobre Vaš pristup kako biste mogli preuzeti programe.")
        else:
            st.write("Dobrodošli u JournalX aplikacijski centar. Ispod se nalaze vaši dostupni programi:")
            
            programi_iz_baze = dohvati_sve_programe()
            
            if len(programi_iz_baze) == 0:
                st.info("Trenutno nema dostupnih programa za preuzimanje.")
            else:
                for p in programi_iz_baze:
                    _, ime, opis, link = p
                    with st.expander(f"📦 {ime}", expanded=True):
                        st.write(opis if opis else "Nema opisa za ovaj program.")
                        st.link_button(f"Preuzmi {ime}", link, use_container_width=True)
                        st.write("") 
