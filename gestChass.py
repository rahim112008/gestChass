import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime
import uuid
import bcrypt
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static
import requests
from textblob import TextBlob
from sklearn.cluster import KMeans
import numpy as np
import random
import string

# ---------------------------
# 1. CONFIGURATION & CONSTANTES
# ---------------------------
st.set_page_config(page_title="GestaChasse - Algérie", layout="wide")

# Admin (remplacer par votre email)
ADMIN_EMAIL = "votre_email@domaine.com"

# Dossier upload
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

DB_NAME = "chasse.db"

# SMTP (pour réinitialisation) - désactivé par défaut (simulation)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "votre_email@gmail.com"
SMTP_PASSWORD = "votre_mot_de_passe"
USE_REAL_SMTP = False

# ---------------------------
# 2. MULTILINGUE (FR / EN / AR)
# ---------------------------
if 'lang' not in st.session_state:
    st.session_state.lang = 'fr'  # par défaut

# Dictionnaire des traductions (extrait simplifié)
TEXTS = {
    'fr': {
        'app_name': 'GestaChasse',
        'lang_selector': '🌐 Langue',
        'welcome': 'Bienvenue',
        'login': 'Connexion',
        'register': 'Inscription',
        'logout': 'Se déconnecter',
        'username': "Nom d'utilisateur",
        'password': 'Mot de passe',
        'email': 'Email',
        'confirm_password': 'Confirmer le mot de passe',
        'forgot_password': 'Mot de passe oublié ?',
        'reset_password': 'Réinitialiser',
        'new_password': 'Nouveau mot de passe',
        'send': 'Envoyer',
        'login_btn': 'Se connecter',
        'register_btn': "S'inscrire",
        'navigation': 'Navigation',
        'my_obs': '📝 Mes observations',
        'map': '🗺️ Carte',
        'stats': '📈 Statistiques',
        'chat': '💬 Messagerie',
        'ads': '🛒 Annonces',
        'profile': '👤 Profil',
        'ai_recog': '🤖 Reconnaissance IA',
        'ai_recs': '📊 Recommandations IA',
        'admin': '🔐 Administration',
        'add_obs': 'Ajouter une observation',
        'date': 'Date',
        'time': 'Heure',
        'species': 'Espèce',
        'gender': 'Sexe',
        'male': 'Mâle',
        'female': 'Femelle',
        'unknown': 'Indéterminé',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'location': 'Lieu',
        'notes': 'Notes',
        'photo': 'Photo',
        'validate': '✅ Valider',
        'delete': '🗑️ Supprimer',
        'public_messages': '📢 Messages publics',
        'private_messages': '💌 Messages privés',
        'send_message': 'Envoyer un message',
        'publish': 'Publier',
        'post_ad': 'Déposer une annonce',
        'title': 'Titre',
        'description': 'Description',
        'price': 'Prix (DZD)',
        'category': 'Catégorie',
        'contact': 'Email de contact',
        'clothing': 'Vêtement',
        'binoculars': 'Jumelles',
        'caller': 'Appelant',
        'weapon': 'Arme',
        'accessory': 'Accessoire',
        'other': 'Autre',
        'no_data': 'Aucune donnée.',
        'success_save': 'Enregistré avec succès !',
        'error_fields': 'Veuillez remplir tous les champs obligatoires.',
        'error_coords': 'Coordonnées GPS obligatoires.',
        'sentiment': 'Sentiment (IA)',
        'delete_confirm': 'Supprimer cette observation ?',
        'species_suggestion': "Suggestion d'espèce",
        'use_suggestion': "Utiliser cette suggestion",
        'spot_recommendations': "Recommandation de spots",
        'zone': "Zone",
        'observations_count': "observations",
        'total_obs': "Total observations",
        'active_hunters': "Chasseurs actifs",
        'species_count': "Espèces différentes",
        'export_csv': "📥 Télécharger CSV",
        'export_users': "📥 Télécharger utilisateurs",
        'admin_zone': "⚠️ Zone réservée à l'administrateur",
        'all_data': "Toutes les observations (tous les chasseurs)",
        'login_error': 'Identifiants incorrects.',
        'register_success': 'Inscription réussie ! Connectez-vous.',
        'register_error': 'Nom ou email déjà utilisé.',
        'reset_sent': 'Un nouveau mot de passe a été envoyé par email.',
        'reset_error': 'Aucun compte trouvé avec cet email.',
        'upload_photo': 'Charger une photo',
        'analyze': 'Analyser',
        'density_map': 'Carte de densité',
        'clustering': 'Clustering des observations',
        'sentiment_analysis': 'Analyse de sentiment',
        'positive': 'Positif',
        'negative': 'Négatif',
        'daily_evolution': 'Évolution quotidienne',
        'seed_data': '🌱 Générer des données de démonstration (Algérie)',
        'seed_success': 'Données de démonstration générées avec succès !',
        'seed_error': 'Erreur lors de la génération des données.',
    },
    'en': {
        'app_name': 'GestaChasse',
        'lang_selector': '🌐 Language',
        'welcome': 'Welcome',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'username': 'Username',
        'password': 'Password',
        'email': 'Email',
        'confirm_password': 'Confirm password',
        'forgot_password': 'Forgot password?',
        'reset_password': 'Reset password',
        'new_password': 'New password',
        'send': 'Send',
        'login_btn': 'Login',
        'register_btn': 'Register',
        'navigation': 'Navigation',
        'my_obs': '📝 My observations',
        'map': '🗺️ Map',
        'stats': '📈 Statistics',
        'chat': '💬 Messaging',
        'ads': '🛒 Classifieds',
        'profile': '👤 Profile',
        'ai_recog': '🤖 AI Recognition',
        'ai_recs': '📊 AI Recommendations',
        'admin': '🔐 Administration',
        'add_obs': 'Add observation',
        'date': 'Date',
        'time': 'Time',
        'species': 'Species',
        'gender': 'Gender',
        'male': 'Male',
        'female': 'Female',
        'unknown': 'Unknown',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'location': 'Location',
        'notes': 'Notes',
        'photo': 'Photo',
        'validate': '✅ Validate',
        'delete': '🗑️ Delete',
        'public_messages': '📢 Public messages',
        'private_messages': '💌 Private messages',
        'send_message': 'Send message',
        'publish': 'Publish',
        'post_ad': 'Post ad',
        'title': 'Title',
        'description': 'Description',
        'price': 'Price (DZD)',
        'category': 'Category',
        'contact': 'Contact email',
        'clothing': 'Clothing',
        'binoculars': 'Binoculars',
        'caller': 'Caller',
        'weapon': 'Weapon',
        'accessory': 'Accessory',
        'other': 'Other',
        'no_data': 'No data.',
        'success_save': 'Saved successfully!',
        'error_fields': 'Please fill all required fields.',
        'error_coords': 'GPS coordinates required.',
        'sentiment': 'Sentiment (AI)',
        'delete_confirm': 'Delete this observation?',
        'species_suggestion': "Species suggestion",
        'use_suggestion': "Use this suggestion",
        'spot_recommendations': "Spot recommendations",
        'zone': "Zone",
        'observations_count': "observations",
        'total_obs': "Total observations",
        'active_hunters': "Active hunters",
        'species_count': "Different species",
        'export_csv': "📥 Download CSV",
        'export_users': "📥 Download users",
        'admin_zone': "⚠️ Administrator area",
        'all_data': "All observations (all hunters)",
        'login_error': 'Incorrect credentials.',
        'register_success': 'Registration successful! Please login.',
        'register_error': 'Username or email already taken.',
        'reset_sent': 'A new password has been sent to your email.',
        'reset_error': 'No account found with this email.',
        'upload_photo': 'Upload photo',
        'analyze': 'Analyze',
        'density_map': 'Density map',
        'clustering': 'Observation clustering',
        'sentiment_analysis': 'Sentiment analysis',
        'positive': 'Positive',
        'negative': 'Negative',
        'daily_evolution': 'Daily evolution',
        'seed_data': '🌱 Generate demo data (Algeria)',
        'seed_success': 'Demo data generated successfully!',
        'seed_error': 'Error generating demo data.',
    },
    'ar': {
        'app_name': 'غيستاشاس',
        'lang_selector': '🌐 اللغة',
        'welcome': 'مرحباً',
        'login': 'تسجيل الدخول',
        'register': 'إنشاء حساب',
        'logout': 'تسجيل الخروج',
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'email': 'البريد الإلكتروني',
        'confirm_password': 'تأكيد كلمة المرور',
        'forgot_password': 'نسيت كلمة المرور؟',
        'reset_password': 'إعادة تعيين كلمة المرور',
        'new_password': 'كلمة مرور جديدة',
        'send': 'إرسال',
        'login_btn': 'تسجيل الدخول',
        'register_btn': 'إنشاء حساب',
        'navigation': 'التنقل',
        'my_obs': '📝 مشاهداتي',
        'map': '🗺️ الخريطة',
        'stats': '📈 إحصائيات',
        'chat': '💬 الرسائل',
        'ads': '🛒 الإعلانات',
        'profile': '👤 الملف الشخصي',
        'ai_recog': '🤖 التعرف بالذكاء الاصطناعي',
        'ai_recs': '📊 توصيات الذكاء الاصطناعي',
        'admin': '🔐 الإدارة',
        'add_obs': 'إضافة مشاهدة',
        'date': 'التاريخ',
        'time': 'الوقت',
        'species': 'النوع',
        'gender': 'الجنس',
        'male': 'ذكر',
        'female': 'أنثى',
        'unknown': 'غير محدد',
        'latitude': 'خط العرض',
        'longitude': 'خط الطول',
        'location': 'الموقع',
        'notes': 'ملاحظات',
        'photo': 'صورة',
        'validate': '✅ تأكيد',
        'delete': '🗑️ حذف',
        'public_messages': '📢 رسائل عامة',
        'private_messages': '💌 رسائل خاصة',
        'send_message': 'إرسال رسالة',
        'publish': 'نشر',
        'post_ad': 'نشر إعلان',
        'title': 'العنوان',
        'description': 'الوصف',
        'price': 'السعر (دج)',
        'category': 'التصنيف',
        'contact': 'بريد التواصل',
        'clothing': 'ملابس',
        'binoculars': 'مناظير',
        'caller': 'مُنادٍ',
        'weapon': 'سلاح',
        'accessory': 'إكسسوار',
        'other': 'أخرى',
        'no_data': 'لا توجد بيانات.',
        'success_save': 'تم الحفظ بنجاح!',
        'error_fields': 'يرجى ملء جميع الحقول الإلزامية.',
        'error_coords': 'إحداثيات GPS مطلوبة.',
        'sentiment': 'المشاعر (ذكاء اصطناعي)',
        'delete_confirm': 'حذف هذه المشاهدة؟',
        'species_suggestion': "اقتراح النوع",
        'use_suggestion': "استخدام هذا الاقتراح",
        'spot_recommendations': "توصيات المواقع",
        'zone': "منطقة",
        'observations_count': "مشاهدة",
        'total_obs': "إجمالي المشاهدات",
        'active_hunters': "الصيادون النشطون",
        'species_count': "أنواع مختلفة",
        'export_csv': "📥 تحميل CSV",
        'export_users': "📥 تحميل المستخدمين",
        'admin_zone': "⚠️ منطقة الإداري",
        'all_data': "جميع المشاهدات (جميع الصيادين)",
        'login_error': 'بيانات الدخول غير صحيحة.',
        'register_success': 'تم إنشاء الحساب بنجاح! يرجى تسجيل الدخول.',
        'register_error': 'اسم المستخدم أو البريد مستخدم مسبقاً.',
        'reset_sent': 'تم إرسال كلمة مرور جديدة إلى بريدك الإلكتروني.',
        'reset_error': 'لا يوجد حساب مرتبط بهذا البريد الإلكتروني.',
        'upload_photo': 'تحميل صورة',
        'analyze': 'تحليل',
        'density_map': 'خريطة الكثافة',
        'clustering': 'تجميع المشاهدات',
        'sentiment_analysis': 'تحليل المشاعر',
        'positive': 'إيجابي',
        'negative': 'سلبي',
        'daily_evolution': 'التطور اليومي',
        'seed_data': '🌱 إنشاء بيانات تجريبية (الجزائر)',
        'seed_success': 'تم إنشاء البيانات التجريبية بنجاح!',
        'seed_error': 'خطأ في إنشاء البيانات التجريبية.',
    }
}

def t(key):
    return TEXTS[st.session_state.lang].get(key, key)

# ---------------------------
# 3. GESTION RTL (ARABE)
# ---------------------------
def apply_rtl():
    if st.session_state.lang == 'ar':
        st.markdown("""
        <style>
        .stApp { direction: rtl; }
        .stSidebar { direction: rtl; }
        .stSelectbox, .stTextInput, .stNumberInput, .stTextArea, .stDateInput, .stTimeInput { direction: rtl; }
        .stButton button { width: 100%; }
        </style>
        """, unsafe_allow_html=True)

# ---------------------------
# 4. BASE DE DONNÉES
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS observations (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        date TEXT,
        time TEXT,
        species TEXT,
        gender TEXT,
        latitude REAL,
        longitude REAL,
        location_description TEXT,
        photo_path TEXT,
        notes TEXT,
        created_at TEXT,
        sentiment REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id TEXT,
        receiver_id TEXT,
        content TEXT,
        timestamp TEXT,
        is_public BOOLEAN,
        FOREIGN KEY(sender_id) REFERENCES users(id),
        FOREIGN KEY(receiver_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS annonces (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        title TEXT,
        description TEXT,
        price REAL,
        category TEXT,
        photo_path TEXT,
        contact_email TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    # Ajout de la colonne sentiment si elle n'existe pas (migration)
    try:
        c.execute("ALTER TABLE observations ADD COLUMN sentiment REAL")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

init_db()

# ---------------------------
# 5. FONCTIONS AUTH / UTILITAIRES
# ---------------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_random_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def send_email(to_email, subject, body):
    if USE_REAL_SMTP:
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True
        except:
            return False
    else:
        print(f"📧 Envoi à {to_email} | {subject}\n{body}")
        return True

def get_user_by_email(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, email, password):
    user_id = str(uuid.uuid4())
    hashed = hash_password(password)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                  (user_id, username, email, hashed, datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_password(user_id, new_password):
    hashed = hash_password(new_password)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id, username, email FROM users", conn)
    conn.close()
    return df

# ---------------------------
# 6. FONCTIONS OBSERVATIONS
# ---------------------------
def save_observation(user_id, data):
    sentiment = None
    if data['notes']:
        blob = TextBlob(data['notes'])
        sentiment = blob.sentiment.polarity
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO observations 
        (id, user_id, date, time, species, gender, latitude, longitude,
         location_description, photo_path, notes, created_at, sentiment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        data['id'], user_id, data['date'], data['time'], data['species'],
        data['gender'], data['latitude'], data['longitude'],
        data['location_description'], data['photo_path'], data['notes'],
        datetime.datetime.now().isoformat(), sentiment
    ))
    conn.commit()
    conn.close()

def get_observations(user_id=None):
    conn = sqlite3.connect(DB_NAME)
    if user_id:
        df = pd.read_sql_query("SELECT * FROM observations WHERE user_id = ? ORDER BY date DESC, time DESC",
                               conn, params=(user_id,))
    else:
        df = pd.read_sql_query("SELECT * FROM observations ORDER BY date DESC, time DESC", conn)
    conn.close()
    return df

def delete_observation(obs_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM observations WHERE id = ? AND user_id = ?", (obs_id, user_id))
    conn.commit()
    conn.close()

# ---------------------------
# 7. FONCTIONS MESSAGERIE
# ---------------------------
def send_message(sender_id, receiver_id, content, is_public=False):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender_id, receiver_id, content, timestamp, is_public) VALUES (?, ?, ?, ?, ?)",
              (sender_id, receiver_id, content, datetime.datetime.now().isoformat(), is_public))
    conn.commit()
    conn.close()

def get_messages(user_id, other_user_id=None):
    conn = sqlite3.connect(DB_NAME)
    if other_user_id:
        df = pd.read_sql_query('''
            SELECT m.*, u.username as sender_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp ASC
        ''', conn, params=(user_id, other_user_id, other_user_id, user_id))
    else:
        df = pd.read_sql_query('''
            SELECT m.*, u.username as sender_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.is_public = 1
            ORDER BY timestamp ASC
        ''', conn)
    conn.close()
    return df

# ---------------------------
# 8. FONCTIONS ANNONCES
# ---------------------------
def create_annonce(user_id, title, description, price, category, photo_path, contact_email):
    ann_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO annonces 
        (id, user_id, title, description, price, category, photo_path, contact_email, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (ann_id, user_id, title, description, price, category, photo_path, contact_email,
               datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_annonces():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query('''
        SELECT a.*, u.username as seller_name
        FROM annonces a
        JOIN users u ON a.user_id = u.id
        ORDER BY created_at DESC
    ''', conn)
    conn.close()
    return df

def delete_annonce(ann_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM annonces WHERE id = ? AND user_id = ?", (ann_id, user_id))
    conn.commit()
    conn.close()

# ---------------------------
# 9. FONCTIONS IA (sans TensorFlow)
# ---------------------------
def recognize_species_inaturalist(image_bytes):
    """Appel à l'API iNaturalist pour la reconnaissance."""
    url = "https://api.inaturalist.org/v1/computervision/score_image"
    files = {'image': ('photo.jpg', image_bytes, 'image/jpeg')}
    try:
        response = requests.post(url, files=files, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            suggestions = []
            for r in results[:3]:
                taxon = r.get('taxon', {})
                name = taxon.get('preferred_common_name', taxon.get('name', ''))
                score = r.get('score', 0) * 100
                suggestions.append(f"{name} ({score:.1f}%)")
            return suggestions
    except:
        pass
    return None

def recommend_spots(df):
    """Clustering pour recommander des zones."""
    coords = df[['latitude', 'longitude']].dropna()
    if len(coords) < 3:
        return None, None
    kmeans = KMeans(n_clusters=min(5, len(coords)//2), random_state=42)
    clusters = kmeans.fit_predict(coords)
    centers = kmeans.cluster_centers_
    counts = pd.Series(clusters).value_counts()
    return centers, counts

# ---------------------------
# 10. FONCTION DE PEUPLEMENT (DÉMONSTRATION ALGÉRIE)
# ---------------------------
def seed_demo_data():
    """Insère des données de démonstration adaptées à l'Algérie."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Espèces algériennes
    especes_algerie = [
        "Sanglier", "Gazelle de Cuvier", "Mouflon à manchettes", "Lièvre du Cap",
        "Renard roux", "Chacal doré", "Hyène rayée", "Chat sauvage d'Afrique",
        "Perdrix gambra", "Perdrix de Sélin", "Faisan de chasse", "Pigeon ramier",
        "Tourterelle des bois", "Caille des blés", "Canard colvert", "Sarcelle d'hiver",
        "Foulque macroule", "Bécassine des marais", "Cigogne blanche", "Héron cendré"
    ]
    
    # Régions d'Algérie avec coordonnées approximatives
    regions_algerie = {
        "Kabylie": (36.7, 4.1),
        "Aurès": (35.3, 6.6),
        "Sahara": (27.0, 3.0),
        "Tell occidental": (35.5, 0.0),
        "Hautes Plaines": (34.0, 4.0),
        "Numidie": (36.9, 6.9),
        "M’zab": (32.5, 3.7),
        "Tassili n'Ajjer": (25.0, 9.0),
        "Atlas saharien": (34.0, 2.0),
        "Oranie": (35.7, -0.6)
    }
    
    # Utilisateurs fictifs
    usernames = [
        "chasseur_kabyle", "sniper_sahara", "hunter_oran", "gazelle_hunter",
        "aures_man", "numidien", "chasseur_blida", "tassili_fan"
    ]
    users = []
    for username in usernames:
        user_id = str(uuid.uuid4())
        email = f"{username}@example.dz"
        password = "chasse123"
        hashed = hash_password(password)
        created_at = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 60))).isoformat()
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?)",
                  (user_id, username, email, hashed, created_at))
        users.append({"id": user_id, "username": username})
        print(f"👤 Chasseur créé : {username}")
    
    # 40 observations
    for _ in range(40):
        region = random.choice(list(regions_algerie.keys()))
        lat_base, lon_base = regions_algerie[region]
        lat = lat_base + random.uniform(-0.5, 0.5)
        lon = lon_base + random.uniform(-0.5, 0.5)
        species = random.choice(especes_algerie)
        gender = random.choice(["Mâle", "Femelle", "Indéterminé"])
        notes = random.choice([
            "Observé en bordure de forêt", "En groupe", "Solitaire", "Très actif",
            "A proximité d'un point d'eau", "Dans une zone boisée", "En plaine",
            "Près d'un oued", "En montagne", "Zone rocheuse"
        ])
        user = random.choice(users)
        obs_id = str(uuid.uuid4())
        date = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))).date().isoformat()
        time = f"{random.randint(5, 20):02d}:{random.randint(0, 59):02d}"
        sentiment = random.uniform(-0.3, 0.9)
        c.execute('''INSERT OR IGNORE INTO observations 
            (id, user_id, date, time, species, gender, latitude, longitude,
             location_description, photo_path, notes, created_at, sentiment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (obs_id, user["id"], date, time, species, gender, lat, lon,
             region, "", notes, datetime.datetime.now().isoformat(), sentiment))
        print(f"📝 Observation : {species} - {region}")
    
    # Messages publics (arabe/français)
    messages_publics = [
        "السلام عليكم، هل من أحد رأى غزال في منطقة القبائل؟",
        "Bonjour à tous, belle sortie hier dans l'Aurès.",
        "شكراً لمنظمي هذا التطبيق، مفيد جداً.",
        "Qui connaît un bon spot pour la perdrix dans l'Oranie ?",
        "J'ai vu un mouflon près de Tassili, magnifique !",
        "La saison de chasse s'annonce bien cette année.",
        "أبحث عن رفيق للصيد في الصحراء.",
        "Attention, sangliers nombreux en Kabylie en ce moment."
    ]
    for msg in messages_publics:
        sender = random.choice(users)
        c.execute("INSERT OR IGNORE INTO messages (sender_id, receiver_id, content, timestamp, is_public) VALUES (?, ?, ?, ?, ?)",
                  (sender["id"], None, msg, datetime.datetime.now().isoformat(), True))
    
    # Messages privés
    for _ in range(5):
        sender = random.choice(users)
        receiver = random.choice([u for u in users if u["id"] != sender["id"]])
        content = random.choice([
            "Salut, on va chasser ce week-end ?",
            "J'ai repéré un bon endroit pour la gazelle.",
            "Tu as des munitions en rab ?",
            "Merci pour le partage de ton spot.",
            "À bientôt, inchallah."
        ])
        c.execute("INSERT OR IGNORE INTO messages (sender_id, receiver_id, content, timestamp, is_public) VALUES (?, ?, ?, ?, ?)",
                  (sender["id"], receiver["id"], content, datetime.datetime.now().isoformat(), False))
    
    # Annonces (prix en dinars)
    annonces_data = [
        {"title": "Jumelles 8x42", "desc": "Idéales pour la chasse en montagne.", "price": 12000, "category": "Jumelles"},
        {"title": "Veste de chasse camo", "desc": "Taille M, adaptée aux climats chauds.", "price": 8500, "category": "Vêtement"},
        {"title": "Appelant à perdrix", "desc": "Son très réaliste, fabriqué en Algérie.", "price": 2500, "category": "Appelant"},
        {"title": "Carabine calibre 12", "desc": "État neuf, avec optique.", "price": 85000, "category": "Arme"},
        {"title": "Sac à dos 30L", "desc": "Idéal pour les randonnées de chasse.", "price": 4500, "category": "Accessoire"},
        {"title": "Bottes de chasse", "desc": "Hauteur 40 cm, imperméables.", "price": 9800, "category": "Accessoire"},
    ]
    for ann in annonces_data:
        user = random.choice(users)
        ann_id = str(uuid.uuid4())
        c.execute('''INSERT OR IGNORE INTO annonces 
            (id, user_id, title, description, price, category, photo_path, contact_email, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (ann_id, user["id"], ann["title"], ann["desc"], ann["price"],
             ann["category"], "", f"{user['username']}@example.dz",
             datetime.datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return True

# ---------------------------
# 11. INIT SESSION
# ---------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None

apply_rtl()

# ---------------------------
# 12. PAGES AUTH
# ---------------------------
def login_page():
    st.title(f"{t('app_name')} - {t('login')}")
    with st.form("login_form"):
        username = st.text_input(t('username'))
        password = st.text_input(t('password'), type="password")
        if st.form_submit_button(t('login_btn')):
            user = get_user_by_username(username)
            if user and verify_password(password, user[3]):
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.email = user[2]
                st.success(f"{t('welcome')} {username}!")
                st.rerun()
            else:
                st.error(t('login_error'))
    with st.expander(t('forgot_password')):
        with st.form("reset_form"):
            email_reset = st.text_input(t('email'))
            if st.form_submit_button(t('reset_password')):
                user = get_user_by_email(email_reset)
                if user:
                    new_pass = generate_random_password()
                    update_password(user[0], new_pass)
                    send_email(email_reset, "GestaChasse - " + t('reset_password'),
                               f"{t('new_password')}: {new_pass}")
                    st.success(t('reset_sent'))
                else:
                    st.error(t('reset_error'))
    st.subheader(t('register'))
    with st.form("register_form"):
        new_user = st.text_input(t('username'))
        new_email = st.text_input(t('email'))
        new_pass = st.text_input(t('password'), type="password")
        confirm = st.text_input(t('confirm_password'), type="password")
        if st.form_submit_button(t('register_btn')):
            if not new_user or not new_email or not new_pass:
                st.error(t('error_fields'))
            elif new_pass != confirm:
                st.error("Les mots de passe ne correspondent pas.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
                st.error("Email invalide.")
            else:
                if create_user(new_user, new_email, new_pass):
                    st.success(t('register_success'))
                    send_email(new_email, "Bienvenue sur GestaChasse",
                               f"Bonjour {new_user},\nVotre compte a été créé.")
                else:
                    st.error(t('register_error'))

def logout():
    for k in ['logged_in', 'user_id', 'username', 'email']:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

# ---------------------------
# 13. PAGES PRINCIPALES
# ---------------------------
def show_observations_page():
    st.title(t('my_obs'))
    with st.expander(f"➕ {t('add_obs')}", expanded=False):
        with st.form("obs_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input(t('date'), datetime.date.today())
                time = st.time_input(t('time'), datetime.datetime.now().time())
                species = st.text_input(f"{t('species')}*")
                gender = st.selectbox(t('gender'), [t('unknown'), t('male'), t('female')])
                lat = st.number_input(f"{t('latitude')}*", value=0.0, format="%.6f")
                lon = st.number_input(f"{t('longitude')}*", value=0.0, format="%.6f")
            with col2:
                loc = st.text_area(t('location'))
                notes = st.text_area(t('notes'))
                photo = st.file_uploader(t('photo'), type=["jpg", "jpeg", "png"])
            if st.form_submit_button(t('validate')):
                if not species or (lat == 0.0 and lon == 0.0):
                    st.error(t('error_coords'))
                else:
                    obs_id = str(uuid.uuid4())
                    path = ""
                    if photo:
                        ext = photo.name.split('.')[-1]
                        fpath = os.path.join(UPLOAD_DIR, f"{obs_id}.{ext}")
                        with open(fpath, "wb") as f:
                            f.write(photo.getbuffer())
                        path = fpath
                    data = {'id': obs_id, 'date': date.isoformat(), 'time': time.isoformat(),
                            'species': species, 'gender': gender, 'latitude': lat, 'longitude': lon,
                            'location_description': loc, 'photo_path': path, 'notes': notes}
                    save_observation(st.session_state.user_id, data)
                    st.success(t('success_save'))
                    st.rerun()
    df = get_observations(st.session_state.user_id)
    if df.empty:
        st.info(t('no_data'))
    else:
        st.subheader("Vos observations")
        st.dataframe(df[['date','time','species','gender','latitude','longitude','location_description','notes']],
                     use_container_width=True)
        sel = st.selectbox("Choisir une observation", df['id'].tolist(),
                           format_func=lambda x: f"{df[df['id']==x]['date'].iloc[0]} - {df[df['id']==x]['species'].iloc[0]}")
        if sel:
            obs = df[df['id'] == sel].iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{t('date')}:** {obs['date']} {obs['time']}")
                st.write(f"**{t('species')}:** {obs['species']}")
                st.write(f"**{t('gender')}:** {obs['gender']}")
                st.write(f"**{t('latitude')}:** {obs['latitude']}, **{t('longitude')}:** {obs['longitude']}")
                st.write(f"**{t('location')}:** {obs['location_description']}")
                st.write(f"**{t('notes')}:** {obs['notes']}")
                if pd.notna(obs.get('sentiment')):
                    st.write(f"**{t('sentiment')}:** {obs['sentiment']:.2f}")
            with col2:
                if obs['photo_path'] and os.path.exists(obs['photo_path']):
                    st.image(Image.open(obs['photo_path']), use_column_width=True)
            if st.button(t('delete')):
                delete_observation(sel, st.session_state.user_id)
                st.success(t('success_save'))
                st.rerun()

def show_carte_page():
    st.title(t('map'))
    df = get_observations()
    if df.empty:
        st.info(t('no_data'))
    else:
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
        for _, r in df.iterrows():
            popup = f"<b>{r['species']}</b><br>{t('gender')}: {r['gender']}<br>{r['date']} {r['time']}<br>{r['location_description']}"
            folium.Marker([r['latitude'], r['longitude']],
                          popup=folium.Popup(popup, max_width=300),
                          tooltip=r['species'],
                          icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
        folium_static(m, width=1000, height=600)

def show_stats_page():
    st.title(t('stats'))
    df = get_observations()
    if df.empty:
        st.info(t('no_data'))
        return
    col1, col2 = st.columns(2)
    with col1:
        counts = df['species'].value_counts().reset_index()
        counts.columns = ['Espèce', 'Nombre']
        fig = px.bar(counts, x='Espèce', y='Nombre', color='Espèce', text='Nombre')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        counts = df['gender'].value_counts().reset_index()
        counts.columns = ['Sexe', 'Nombre']
        fig = px.pie(counts, values='Nombre', names='Sexe')
        st.plotly_chart(fig, use_container_width=True)
    if 'sentiment' in df.columns and not df['sentiment'].isna().all():
        st.subheader(t('sentiment_analysis'))
        avg = df['sentiment'].mean()
        st.metric("Sentiment moyen", f"{avg:.2f}", delta="Positif" if avg > 0 else "Négatif")
        fig = px.histogram(df, x='sentiment', nbins=20)
        st.plotly_chart(fig, use_container_width=True)
    df['date'] = pd.to_datetime(df['date'])
    daily = df.groupby(df['date'].dt.date).size().reset_index(name='Nombre')
    fig = px.line(daily, x='date', y='Nombre', markers=True, title=t('daily_evolution'))
    st.plotly_chart(fig, use_container_width=True)

def show_chat_page():
    st.title(t('chat'))
    tab1, tab2 = st.tabs([t('public_messages'), t('private_messages')])
    with tab1:
        msgs = get_messages(st.session_state.user_id)
        if not msgs.empty:
            for _, m in msgs.iterrows():
                st.write(f"**{m['sender_name']}** ({m['timestamp']}): {m['content']}")
        with st.form("pub_msg"):
            c = st.text_area(t('send_message'))
            if st.form_submit_button(t('publish')):
                if c:
                    send_message(st.session_state.user_id, None, c, True)
                    st.rerun()
    with tab2:
        users = get_all_users()
        others = users[users['id'] != st.session_state.user_id]
        if others.empty:
            st.info(t('no_data'))
        else:
            sel = st.selectbox("Destinataire", others['id'].tolist(),
                               format_func=lambda x: others[others['id']==x]['username'].iloc[0])
            if sel:
                msgs = get_messages(st.session_state.user_id, sel)
                for _, m in msgs.iterrows():
                    sender = "Moi" if m['sender_id'] == st.session_state.user_id else m['sender_name']
                    st.write(f"**{sender}** ({m['timestamp']}): {m['content']}")
                with st.form("priv_msg"):
                    c = st.text_area(t('send_message'))
                    if st.form_submit_button(t('send_message')):
                        if c:
                            send_message(st.session_state.user_id, sel, c, False)
                            st.rerun()

def show_annonces_page():
    st.title(t('ads'))
    with st.expander(f"➕ {t('post_ad')}"):
        with st.form("ad_form"):
            title = st.text_input(f"{t('title')}*")
            desc = st.text_area(t('description'))
            price = st.number_input(t('price'), min_value=0.0, value=0.0)
            cat = st.selectbox(t('category'), [t('clothing'), t('binoculars'), t('caller'), t('weapon'), t('accessory'), t('other')])
            contact = st.text_input(f"{t('contact')}*")
            photo_ad = st.file_uploader(t('photo'), type=["jpg","jpeg","png"])
            if st.form_submit_button(t('publish')):
                if not title or not contact:
                    st.error(t('error_fields'))
                else:
                    aid = str(uuid.uuid4())
                    path = ""
                    if photo_ad:
                        ext = photo_ad.name.split('.')[-1]
                        fpath = os.path.join(UPLOAD_DIR, f"ann_{aid}.{ext}")
                        with open(fpath, "wb") as f:
                            f.write(photo_ad.getbuffer())
                        path = fpath
                    create_annonce(st.session_state.user_id, title, desc, price, cat, path, contact)
                    st.success(t('success_save'))
                    st.rerun()
    ads = get_annonces()
    if ads.empty:
        st.info(t('no_data'))
    else:
        for _, a in ads.iterrows():
            c1, c2 = st.columns([1,3])
            with c1:
                if a['photo_path'] and os.path.exists(a['photo_path']):
                    st.image(Image.open(a['photo_path']), width=150)
                else:
                    st.image("https://via.placeholder.com/150.png?text=Photo", width=150)
            with c2:
                st.subheader(a['title'])
                st.write(f"**{t('category')}:** {a['category']} | **{t('price')}:** {a['price']} DZD")
                st.write(a['description'])
                st.write(f"**Vendeur:** {a['seller_name']} ({a['contact_email']})")
                if a['user_id'] == st.session_state.user_id:
                    if st.button(t('delete'), key=f"del_{a['id']}"):
                        delete_annonce(a['id'], st.session_state.user_id)
                        st.rerun()
            st.divider()

def show_profile_page():
    st.title(t('profile'))
    st.write(f"**{t('username')}:** {st.session_state.username}")
    st.write(f"**{t('email')}:** {st.session_state.email}")
    df = get_observations(st.session_state.user_id)
    st.write(f"**{t('total_obs')}:** {len(df)}")
    if not df.empty:
        st.dataframe(df['species'].value_counts().reset_index().rename(columns={'index':'Espèce', 'species':'Nombre'}))
    if st.button(t('logout')):
        logout()

def show_ia_recognition_page():
    st.title(t('ai_recog'))
    uploaded = st.file_uploader(t('upload_photo'), type=["jpg","jpeg","png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, width=300)
        with st.spinner(t('analyze')+"..."):
            bytes_data = uploaded.getvalue()
            sugg = recognize_species_inaturalist(bytes_data)
            if sugg:
                st.success("iNaturalist :")
                for s in sugg:
                    st.write(f"- {s}")
                first = sugg[0].split('(')[0].strip()
                if st.button(f"{t('use_suggestion')} '{first}'"):
                    st.session_state['ia_species'] = first
                    st.info(f"Espèce mise à jour : {first}")
            else:
                st.warning("L'API iNaturalist n'est pas accessible. Veuillez saisir l'espèce manuellement.")

def show_ia_recommendations_page():
    st.title(t('ai_recs'))
    df = get_observations()
    if df.empty:
        st.info(t('no_data'))
        return
    st.subheader(t('density_map'))
    fig = px.density_mapbox(df, lat='latitude', lon='longitude', z='id',
                            radius=10,
                            center=dict(lat=df['latitude'].mean(), lon=df['longitude'].mean()),
                            zoom=6, mapbox_style="stamen-terrain")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader(t('clustering'))
    centers, counts = recommend_spots(df)
    if centers is not None:
        m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=6)
        for _, r in df.iterrows():
            folium.CircleMarker([r['latitude'], r['longitude']], radius=3, color='red', fill=True).add_to(m)
        for i, c in enumerate(centers):
            folium.CircleMarker([c[0], c[1]], radius=8 + counts[i]*2, color='blue', fill=True,
                                popup=f"{t('zone')} {i+1} : {counts[i]} {t('observations_count')}").add_to(m)
        folium_static(m, width=1000, height=600)
    else:
        st.info("Minimum 3 observations pour le clustering.")

def show_admin_page():
    st.title(t('admin'))
    st.warning(t('admin_zone'))
    
    # Bouton pour générer les données de démonstration
    if st.button(t('seed_data')):
        with st.spinner("Génération des données..."):
            success = seed_demo_data()
            if success:
                st.success(t('seed_success'))
                st.rerun()
            else:
                st.error(t('seed_error'))
    
    st.divider()
    
    df = get_observations()
    if df.empty:
        st.info(t('no_data'))
    else:
        st.subheader(t('all_data'))
        st.dataframe(df, use_container_width=True)
        c1, c2, c3 = st.columns(3)
        c1.metric(t('total_obs'), len(df))
        c2.metric(t('active_hunters'), df['user_id'].nunique())
        c3.metric(t('species_count'), df['species'].nunique())
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(t('export_csv'), csv, f"gestachasse_{datetime.date.today()}.csv", "text/csv")
        users = get_all_users()
        if not users.empty:
            st.download_button(t('export_users'), users.to_csv(index=False).encode('utf-8'),
                               f"users_{datetime.date.today()}.csv", "text/csv")

# ---------------------------
# 14. MAIN
# ---------------------------
def main():
    # Sélecteur de langue dans la sidebar
    lang_map = {'Français': 'fr', 'English': 'en', 'العربية': 'ar'}
    current_lang_name = [k for k, v in lang_map.items() if v == st.session_state.lang][0]
    selected = st.sidebar.selectbox(t('lang_selector'), list(lang_map.keys()),
                                    index=list(lang_map.keys()).index(current_lang_name))
    if lang_map[selected] != st.session_state.lang:
        st.session_state.lang = lang_map[selected]
        st.rerun()

    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.title(f"👋 {st.session_state.username}")
        pages = [t('my_obs'), t('map'), t('stats'), t('chat'), t('ads'), t('profile'), t('ai_recog'), t('ai_recs')]
        if st.session_state.email == ADMIN_EMAIL:
            pages.append(t('admin'))
        page = st.sidebar.radio(t('navigation'), pages)

        if page == t('my_obs'):
            show_observations_page()
        elif page == t('map'):
            show_carte_page()
        elif page == t('stats'):
            show_stats_page()
        elif page == t('chat'):
            show_chat_page()
        elif page == t('ads'):
            show_annonces_page()
        elif page == t('profile'):
            show_profile_page()
        elif page == t('ai_recog'):
            show_ia_recognition_page()
        elif page == t('ai_recs'):
            show_ia_recommendations_page()
        elif page == t('admin'):
            show_admin_page()

if __name__ == "__main__":
    main()
