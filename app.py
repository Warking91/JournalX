import streamlit as st

# Postavke stranice
st.set_page_config(page_title="JournalX Panel", page_icon="📝", layout="wide")

# Simulacija baze podataka u memoriji (za testiranje)
if "korisnici" not in st.session_state:
    st.session_state.korisnici = [
        {"username": "klijent1", "email": "klijent1@mail.com", "status": "Aktivan"},
        {"username": "klijent2", "email": "klijent2@mail.com", "status": "Na čekanju"},
    ]

# 1. Funkcija za Login formu
def login_forma():
    st.subheader("🔒 Prijavite se na JournalX Panel")
    username = st.text_input("Korisničko ime")
    password = st.text_input("Lozinka", type="password")
    
    if st.button("Prijavi se", use_container_width=True):
        # Provjera uloga (Hardkodovano za test, kasnije se povezuje sa bazom)
        if username == "bog" and password == "bog123":
            st.session_state.uloga = "Bog"
            st.session_state.prijavljen = True
            st.rerun()
        elif username == "mod" and password == "mod123":
            st.session_state.uloga = "Mod"
            st.session_state.prijavljen = True
            st.rerun()
        elif username == "customer" and password == "user123":
            st.session_state.uloga = "Customer"
            st.session_state.prijavljen = True
            st.rerun()
        else:
            st.error("Pogrešno korisničko ime ili lozinka!")

# Ako korisnik nije prijavljen, prikaži samo login
if "prijavljen" not in st.session_state:
    login_forma()
else:
    # Sidebar za odjavu i prikaz trenutne uloge
    st.sidebar.image("JournalX.png", width=150, errors="ignore")
    st.sidebar.write(f"Prijavljeni ste kao: **{st.session_state.uloga}**")
    if st.sidebar.button("Odjavi se"):
        del st.session_state.prijavljen
        del st.session_state.uloga
        st.rerun()

    # --- 👑 BOG PANEL (SUPER ADMIN) ---
    if st.session_state.uloga == "Bog":
        st.title("⚡ BOG PANEL (Svemoguća kontrola)")
        
        tab1, tab2, tab3 = st.tabs(["📊 Statistika Sistema", "👥 Upravljanje Korisnicima", "⚙️ Glavne Postavke"])
        
        with tab1:
            col1, col2, col3 = st.columns(3)
            col1.metric("Ukupno Zarada", "1,250 €", "+12%")
            col2.metric("Aktivni Korisnici", len(st.session_state.korisnici), "+2")
            col3.metric("Broj Modova", "3", "0")
            
        with tab2:
            st.write("Lista svih registrovanih klijenata:")
            st.dataframe(st.session_state.korisnici, use_container_width=True)
            
            # Opcija za brisanje ili dodavanje korisnika (Bog može sve)
            novi_user = st.text_input("Dodaj novog korisnika preko boga")
            if st.button("Dodaj"):
                st.session_state.korisnici.append({"username": novi_user, "email": "manual@mail.com", "status": "Aktivan"})
                st.success("Korisnik dodan!")
                st.rerun()
                
        with tab3:
            st.warning("⚠️ Ovdje mijenjate srž JournalX sistema")
            st.toggle("Ugasi cijeli sajt (Maintenance Mode)")
            st.toggle("Zaključaj registracije")

    # --- 🛠️ MOD PANEL (MODERATOR) ---
    elif st.session_state.uloga == "Mod":
        st.title("🛡️ MOD PANEL (Moderacija sadržaja)")
        st.write("Vaš zadatak je održavanje reda unutar JournalX-a.")
        
        st.subheader("📌 Tiketi i prijave na čekanju")
        st.info("Trenutno nema otvorenih prijava od strane korisnika.")
        
        st.subheader("📝 Pregled korisnika (Samo čitanje)")
        st.table(st.session_state.korisnici) # Mod vidi, ali ne može brisati kao Bog

    # --- 👤 CUSTOMERS PANEL (KLIJENTI) ---
    elif st.session_state.uloga == "Customer":
        st.title("🚀 JournalX Korisnički Panel")
        st.write("Dobrodošli nazad u vaš privatni kutak.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📥 Preuzmite najnoviju verziju")
            st.write("Klikom na dugme ispod možete preuzeti šifrirani JX.exe program.")
            # Ovdje ćete staviti link sa vašeg Google Drive-a
            st.link_button("Preuzmi JX.exe", "https://google.com...", use_container_width=True)
            
        with col2:
            st.subheader("👤 Vaš Profil")
            st.text_input("Ime i Prezime", value="Neko Nekić")
            st.text_input("Email", value="customer@mail.com")
            if st.button("Spasi izmjene"):
                st.success("Profil uspješno ažuriran!")
