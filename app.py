import streamlit as st
import googleapiclient.discovery
import re

# CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Kiftelevision - Espace Vidéos & Documents", layout="wide", page_icon="📺")

# --- CONFIGURATION DE VOS ACCÈS À REMPLIR ---
YOUTUBE_API_KEY = "AIzaSyDhwxuD5JZmXlGLIxOeV3NATx6dC1wGdNI"       # <--- Collez ici votre clé Google AIzaSy...
CHANNEL_ID = "UClLUyXtL6dkw6V1Ec7y6I0g"         # Identifiant officiel de Kiftelevision

# Initialisation du client API YouTube
@st.cache_resource
def get_youtube_client():
    return googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# 1. RECUPERER TOUTES LES PLAYLISTS
@st.cache_data(ttl=3600)
def fetch_playlists(channel_id):
    youtube = get_youtube_client()
    request = youtube.playlists().list(
        part="snippet,contentDetails",
        channelId=channel_id,
        maxResults=50
    )
    response = request.execute()
    playlists = []
    for item in response.get("items", []):
        playlists.append({
            "id": item["id"],
            "title": item["snippet"]["title"]
        })
    return playlists

# 2. RECUPERER LES VIDEOS DE LA PLAYLIST
@st.cache_data(ttl=1800)
def fetch_videos_from_playlist(playlist_id):
    youtube = get_youtube_client()
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    videos = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        videos.append({
            "id": snippet["resourceId"]["videoId"],
            "title": snippet["title"],
            "description": snippet["description"]
        })
    return videos

# 3. EXTRAIRE LES LIENS GOOGLE DOCS
def extract_google_docs_links(text):
    pattern = r'(https://docs\.google\.com/[^\s]+)'
    links = re.findall(pattern, text)
    cleaned_links = [link.rstrip('.,;)') for link in links]
    return list(set(cleaned_links))

# --- INTERFACE GRAPHIQUE PRINCIPALE ---

st.title("📺 Kiftelevision — Lecteur & Documents Simplifiés")
st.markdown("Accédez directement à vos playlists et ouvrez vos documents de travail en un clic.")

if YOUTUBE_API_KEY == "VOTRE_CLE_API_YOUTUBE":
    st.error("👉 Action requise : Veuillez remplacer 'VOTRE_CLE_API_YOUTUBE' à la ligne 8 par votre véritable clé API Google Cloud.")
else:
    try:
        playlists = fetch_playlists(CHANNEL_ID)
        
        if not playlists:
            st.warning("Aucune playlist publique n'a été trouvée sur cette chaîne.")
        else:
            playlist_titles = [p["title"] for p in playlists]
            selected_playlist_title = st.selectbox("📂 Étape 1 : Choisissez une Playlist", playlist_titles)
            
            selected_playlist_id = next(p["id"] for p in playlists if p["title"] == selected_playlist_title)
            videos = fetch_videos_from_playlist(selected_playlist_id)
            
            if not videos:
                st.info("Cette playlist ne contient pas encore de vidéos.")
            else:
                video_titles = [v["title"] for v in videos]
                selected_video_title = st.selectbox("🎵 Étape 2 : Sélectionnez votre vidéo / émission", video_titles)
                
                selected_video = next(v for v in videos if v["title"] == selected_video_title)
                
                st.divider()
                
                # REPARTITION DE L'ECRAN (65% Vidéo / 35% Google Docs)
                col1, col2 = st.columns([1.8, 1.2])
                
                with col1:
                    st.subheader(selected_video["title"])
                    st.video(f"https://youtube.com{selected_video['id']}")
                    
                with col2:
                    st.subheader("📄 Documents Google Doc associés")
                    gdocs = extract_google_docs_links(selected_video["description"])
                    
                    if gdocs:
                        st.info(f"Fichiers trouvés dans la description ({len(gdocs)}) :")
                        for i, link in enumerate(gdocs, start=1):
                            st.link_button(f"🚀 Ouvrir le Document #{i}", link, use_container_width=True)
                    else:
                        st.warning("Aucun lien Google Doc n'a été détecté dans la description de cette vidéo.")
                        
    except Exception as e:
        st.error(f"Une erreur est survenue lors de la communication avec YouTube : {e}")