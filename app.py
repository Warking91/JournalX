import streamlit as st
import sqlite3
import secrets
import string

# 1. Postavke stranice
st.set_page_config(page_title="JournalX Panel", page_icon="📝", layout="wide")

# --- GLOBALNI CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

.prog-card {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    font-family: 'DM Sans', sans-serif;
}
.prog-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #6366f1, #dc2626);
    border-radius: 4px 0 0 4px;
}
.prog-card:hover {
    border-color: rgba(99, 102, 241, 0.6);
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
    transform: translateY(-2px);
}
.prog-title {
    font-family: 'Syne', sans-serif;
    font-size: 20px; font-weight: 800;
    color: #f1f5f9; margin: 0 0 6px 0; letter-spacing: 0.5px;
}
.prog-id {
    display: inline-block;
    background: rgba(99, 102, 241, 0.2);
    color: #818cf8; font-size: 11px; font-weight: 500;
    padding: 2px 10px; border-radius: 20px; margin-bottom: 12px;
    letter-spacing: 1px; text-transform: uppercase;
}
.prog-desc { color: #94a3b8; font-size: 14px; line-height: 1.6; margin-bottom: 16px; display: none; }
.prog-desc.active { display: block; }
.section-header {
    font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 700;
    color: #475569; letter-spacing: 3px; text-transform: uppercase;
    margin: 32px 0 16px 0; padding-bottom: 8px;
    border-bottom: 1px solid rgba(99,102,241,0.15);
}
.empty-state {
    text-align: center; padding: 48px 24px;
    background: rgba(15,23,42,0.5);
    border: 1px dashed rgba(99,102,241,0.2);
    border-radius: 16px; color: #475569;
    font-family: 'DM Sans', sans-serif; font-size: 15px;
}
.logo-kontejner { text-align: center; padding: 20px; margin-bottom: 20px; }
.logo-tekst { font-family: 'Syne', sans-serif; font-size: 55px; font-weight: 800;
    letter-spacing: 2px; color: #1E3A8A; text-transform: uppercase;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }
.logo-x { color: #DC2626; font-size: 65px; font-style: italic;
    text-shadow: 3px 3px 6px rgba(220, 38, 38, 0.3); }
.podnaslov { font-family: 'DM Sans', sans-serif; font-size: 14px;
    color: #6B7280; letter-spacing: 5px; text-transform: uppercase; margin-top: -15px; }
</style>
""", unsafe_allow_html=True)

# --- LOGO ---
st.markdown(
    "<div class='logo-kontejner'>"
    "<div class='logo-tekst'>Journal<span class='logo-x'>X</span></div>"
    "<div class='podnaslov'>Aplikacijski Centar</div>"
    "</div>",
    unsafe_allow_html=True
)

# --- LOCALSTORAGE: spremi/učitaj username ---
# Inject JS koji čita localStorage i šalje username nazad u Streamlit
st.markdown("""
<script>
// Spremi username u localStorage kad se forma submita
window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'save_username') {
        localStorage.setItem('jx_username', e.data.username);
    }
    if (e.data && e.data.type === 'clear_username') {
        localStorage.removeItem('jx_username');
    }
});
</script>
""", unsafe_allow_html=True)

# Učitaj zapamćeni username iz localStorage putem query params trika
def get_saved_username():
    """Dohvati zapamćeni username iz session state (postavljeno JS-om)."""
    return st.session_state.get("saved_username", "")


# 2. Inicijalizacija baze
def inicijaliziraj_bazu():
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS korisnici (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, password TEXT, email TEXT, uloga TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS programi (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ime TEXT, opis TEXT, link TEXT)''')
    c.execute("SELECT COUNT(*) FROM korisnici")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO korisnici VALUES (NULL,'bog','bog123','bog@journalx.com','Bog','Aktivan')")
        c.execute("INSERT INTO korisnici VALUES (NULL,'mod','mod123','mod@journalx.com','Mod','Aktivan')")
        c.execute("INSERT INTO korisnici VALUES (NULL,'customer','user123','user@journalx.com','Customer','Aktivan')")
        c.execute("INSERT INTO programi VALUES (NULL,'JournalX klijent','Glavni šifrirani program za upravljanje JournalX sistemom.','https://google.com')")
        conn.commit()
    conn.close()

inicijaliziraj_bazu()


# --- POMOĆNE FUNKCIJE ---
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
        c.execute("INSERT INTO korisnici (username,password,email,uloga,status) VALUES (?,?,?,?,?)",
                  (username, password, email, uloga, status))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def azuriraj_status_korisnika(kid, novi):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("UPDATE korisnici SET status=? WHERE id=?", (novi, kid))
    conn.commit(); conn.close()

def azuriraj_ulogu_korisnika(kid, nova):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("UPDATE korisnici SET uloga=? WHERE id=?", (nova, kid))
    conn.commit(); conn.close()

def promijeni_lozinku(username, nova):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("UPDATE korisnici SET password=? WHERE username=?", (nova, username))
    conn.commit(); conn.close()

def provjeri_email_i_username(username, email):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("SELECT id FROM korisnici WHERE username=? AND email=?", (username, email))
    res = c.fetchone()
    conn.close()
    return res is not None

def generiraj_novu_lozinku(duljina=10):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(duljina))

def dodaj_program(ime, opis, link):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("INSERT INTO programi (ime,opis,link) VALUES (?,?,?)", (ime, opis, link))
    conn.commit(); conn.close()

def dohvati_sve_programe():
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("SELECT id, ime, opis, link FROM programi ORDER BY id DESC")
    res = c.fetchall()
    conn.close()
    return res

def obrisi_program(pid):
    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("DELETE FROM programi WHERE id=?", (pid,))
    conn.commit(); conn.close()


# --- KOMPONENTA: Kartice programa ---
def prikazi_programe_kartice(programi, admin_mode=False):
    if not programi:
        st.markdown("<div class='empty-state'>📭 Nema dostupnih programa trenutno.</div>", unsafe_allow_html=True)
        return

    if "otvorene_kartice" not in st.session_state:
        st.session_state.otvorene_kartice = set()

    for p in programi:
        p_id, p_ime, p_opis, p_link = p
        je_otvoren = p_id in st.session_state.otvorene_kartice
        desc_html = f"<div class='prog-desc {'active' if je_otvoren else ''}'>{p_opis if p_opis else 'Nema opisa.'}</div>"
        st.markdown(f"""
        <div class='prog-card'>
            <div class='prog-id'>Program #{p_id}</div>
            <div class='prog-title'>📦 {p_ime}</div>
            {desc_html}
        </div>""", unsafe_allow_html=True)

        if admin_mode:
            col1, col2, col3 = st.columns([2, 2, 2])
        else:
            col1, col2 = st.columns([2, 8])

        with col1:
            label = "▲ Sakrij" if je_otvoren else "▼ Opis"
            if st.button(label, key=f"toggle_{p_id}", use_container_width=True):
                if je_otvoren:
                    st.session_state.otvorene_kartice.discard(p_id)
                else:
                    st.session_state.otvorene_kartice.add(p_id)
                st.rerun()

        with col2:
            st.link_button("⬇️ Preuzmi", p_link, use_container_width=True)

        if admin_mode:
            with col3:
                if st.button("🗑️ Obriši", key=f"del_{p_id}", use_container_width=True):
                    obrisi_program(p_id)
                    st.session_state.otvorene_kartice.discard(p_id)
                    st.success(f"Program '{p_ime}' uklonjen!")
                    st.rerun()

        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)


# --- LOGIN FORMA SA ZAPAMTI ME ---
def login_i_registracija():
    izbor = st.radio("Odaberite akciju", ["Prijava", "Registracija", "Zaboravljena lozinka"], horizontal=True)

    if izbor == "Prijava":

        # JS koji učitava zapamćeni username iz localStorage i popunjava polje
        st.components.v1.html("""
        <script>
        function sendSavedUsername() {
            const saved = localStorage.getItem('jx_username');
            if (saved) {
                // Pokušaj popuniti Streamlit input
                const inputs = window.parent.document.querySelectorAll('input[type="text"]');
                inputs.forEach(inp => {
                    if (inp.closest('[data-testid="stTextInput"]')) {
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        nativeInputValueSetter.call(inp, saved);
                        inp.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            }
        }
        // Pričekaj da se Streamlit renderira
        setTimeout(sendSavedUsername, 800);
        </script>
        """, height=0)

        # Dohvati zadnji zapamćeni username iz session_state ako postoji
        default_user = st.session_state.get("zapamceni_username", "")

        username = st.text_input("Korisničko ime", value=default_user)
        password = st.text_input("Lozinka", type="password")
        zapamti = st.checkbox("🔐 Zapamti me", value=st.session_state.get("zapamti_checkbox", False))

        if st.button("Prijavi se", use_container_width=True):
            rezultat = provjeri_korisnika(username, password)
            if rezultat:
                uloga, status = rezultat
                if status == "Blokiran":
                    st.error("Vaš račun je blokiran od strane administratora!")
                else:
                    # Spremi username ako je "Zapamti me" označen
                    if zapamti:
                        st.session_state.zapamceni_username = username
                        st.session_state.zapamti_checkbox = True
                    else:
                        st.session_state.zapamceni_username = ""
                        st.session_state.zapamti_checkbox = False

                    st.session_state.uloga = uloga
                    st.session_state.status = status
                    st.session_state.korisnik = username
                    st.session_state.prijavljen = True

                    # JS: spremi u localStorage browsera
                    if zapamti:
                        st.components.v1.html(f"""
                        <script>
                        localStorage.setItem('jx_username', '{username}');
                        </script>
                        """, height=0)
                    else:
                        st.components.v1.html("""
                        <script>
                        localStorage.removeItem('jx_username');
                        </script>
                        """, height=0)

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

    elif izbor == "Zaboravljena lozinka":
        st.info("🔑 Unesite vaše korisničko ime i email. Ako se podudaraju, dobit ćete novu lozinku.")
        zab_username = st.text_input("Korisničko ime")
        zab_email = st.text_input("Email adresa")
        if st.button("Resetiraj lozinku", use_container_width=True):
            if zab_username and zab_email:
                if provjeri_email_i_username(zab_username, zab_email):
                    nova_lozinka = generiraj_novu_lozinku()
                    promijeni_lozinku(zab_username, nova_lozinka)
                    st.success("✅ Lozinka uspješno resetirana!")
                    st.warning(f"🔐 Vaša nova privremena lozinka je: **`{nova_lozinka}`**")
                    st.info("💡 Preporučujemo da se odmah prijavite i promijenite lozinku.")
                else:
                    st.error("❌ Nije pronađen korisnik s tim korisničkim imenom i emailom.")
            else:
                st.warning("Molimo unesite korisničko ime i email.")


# --- GLAVNI PRIKAZ ---
if "prijavljen" not in st.session_state:
    login_i_registracija()
else:
    st.sidebar.title("💥 JournalX")
    st.sidebar.write(f"Korisnik: **{st.session_state.korisnik}**")
    st.sidebar.write(f"Rang: **{st.session_state.uloga}**")

    conn = sqlite3.connect("journalx_v2.db")
    c = conn.cursor()
    c.execute("SELECT status FROM korisnici WHERE username=?", (st.session_state.korisnik,))
    trenutni_status_db = c.fetchone()
    conn.close()
    trenutni_status = trenutni_status_db[0] if trenutni_status_db else "Na čekanju"
    st.sidebar.write(f"Status računa: **{trenutni_status}**")

    if st.sidebar.button("Odjavi se", use_container_width=True):
        # Ako nije "Zapamti me", obriši iz localStorage
        if not st.session_state.get("zapamti_checkbox", False):
            st.components.v1.html("""
            <script>
            localStorage.removeItem('jx_username');
            </script>
            """, height=0)
        del st.session_state.prijavljen
        del st.session_state.uloga
        del st.session_state.korisnik
        if "otvorene_kartice" in st.session_state:
            del st.session_state.otvorene_kartice
        st.rerun()

    # --- 👑 BOG PANEL ---
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
                        st.caption(f"Rang: {k_uloga} | Status: {k_status}")
                    with col_akcija_status:
                        if k_status in ["Na čekanju", "Blokiran"]:
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
            st.subheader("➕ Dodaj novi program")
            prog_ime = st.text_input("Ime programa")
            prog_opis = st.text_area("Opis programa")
            prog_link = st.text_input("Google Drive link za download")
            if st.button("Objavi program na sajt", use_container_width=True):
                if prog_ime and prog_link:
                    dodaj_program(prog_ime, prog_opis, prog_link)
                    st.success(f"Uspješno dodan: {prog_ime}!")
                    st.rerun()
            st.markdown("<div class='section-header'>TRENUTNI PROGRAMI</div>", unsafe_allow_html=True)
            prikazi_programe_kartice(dohvati_sve_programe(), admin_mode=True)

    # --- 🛠️ MOD PANEL ---
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

    # --- 👤 CUSTOMER PANEL ---
    elif st.session_state.uloga == "Customer":
        st.title("🚀 Vaš Korisnički Panel")
        if trenutni_status == "Na čekanju":
            st.warning("🔒 Vaš račun je uspješno kreiran, ali trenutno ima status **'Na čekanju'**.")
            st.info("Molimo sačekajte da vlasnik (Bog) ili Moderator odobre Vaš pristup.")
        else:
            st.write("Dobrodošli u JournalX aplikacijski centar. Ispod se nalaze vaši dostupni programi:")
            st.markdown("<div class='section-header'>DOSTUPNI PROGRAMI</div>", unsafe_allow_html=True)
            prikazi_programe_kartice(dohvati_sve_programe(), admin_mode=False)
