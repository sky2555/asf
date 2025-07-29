import streamlit as st
import requests

# 🔑 API Key
API_KEY = "94145c1b57ad82308778c658f6da2a4e"
BASE_URL = "https://api.themoviedb.org/3"

# 🎨 CSS ทำให้ UI สวยแบบ IMDB
st.markdown("""
    <style>
        .stApp {background-color: #000; color: white;}
        .movie-card {
            background: #1a1a1a;
            border-radius: 10px;
            padding: 10px;
            margin: 10px;
            text-align: center;
            box-shadow: 0px 0px 10px rgba(255,255,255,0.1);
        }
        .movie-title {font-size: 18px; font-weight: bold; color: #FFD700;}
        .rating {background: #FFD700; color: black; font-weight: bold;
                 padding: 3px 8px; border-radius: 5px; display: inline-block;}
        img {border-radius: 5px;}
        .back-btn {color: white; background: #FFD700; padding: 5px 10px; border-radius: 5px; text-decoration: none;}
    </style>
""", unsafe_allow_html=True)

# ✅ ฟังก์ชันดึงประเภท
@st.cache_data
def get_genres():
    url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=en-US"
    res = requests.get(url).json()
    return {g["name"]: g["id"] for g in res["genres"]}

# ✅ ฟังก์ชันดึงหนังตามประเภท
def get_movies(genre_id):
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={genre_id}&sort_by=popularity.desc"
    return requests.get(url).json()["results"]

# ✅ ฟังก์ชันดึงรายละเอียดหนัง + trailer
def get_movie_details(movie_id):
    details = requests.get(f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US").json()
    videos = requests.get(f"{BASE_URL}/movie/{movie_id}/videos?api_key={API_KEY}&language=en-US").json()
    trailer = next((v["key"] for v in videos["results"] if v["site"] == "YouTube" and v["type"] == "Trailer"), None)
    return details, trailer

# ✅ ใช้ session_state เพื่อเก็บหน้าปัจจุบัน
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ✅ ฟังก์ชันเปลี่ยนหน้า
def go_home():
    st.session_state.page = "home"
    st.session_state.selected_movie = None

def show_movie(movie_id):
    st.session_state.page = "details"
    st.session_state.selected_movie = movie_id

# 🎬 หน้า Home
if st.session_state.page == "home":
    st.title("🎬 Movie Hub – IMDB Style")
    st.write("ค้นหาหนังใหม่ในสไตล์ IMDB พร้อมรายละเอียดเต็ม")

    # ✅ เลือกประเภท
    genres = get_genres()
    genre_name = st.selectbox("เลือกประเภทหนัง", list(genres.keys()))
    movies = get_movies(genres[genre_name])

    # ✅ ค้นหา
    search = st.text_input("🔍 ค้นหาหนังในหมวดนี้")
    if search:
        movies = [m for m in movies if search.lower() in m["title"].lower()]

    # ✅ แสดงหนังแบบ Grid
    cols = st.columns(3)
    for i, movie in enumerate(movies):
        poster = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "https://via.placeholder.com/300x450"
        with cols[i % 3]:
            if st.button(movie["title"], key=f"btn_{movie['id']}"):
                show_movie(movie["id"])
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{poster}" width="100%">
                    <div class="movie-title">{movie['title']}</div>
                    <div class="rating">⭐ {movie['vote_average']}</div>
                </div>
            """, unsafe_allow_html=True)

# 🎬 หน้า Details
elif st.session_state.page == "details":
    movie_id = st.session_state.selected_movie
    details, trailer = get_movie_details(movie_id)

    st.markdown(f"<a class='back-btn' href='#' onclick='window.location.reload()'>⬅️ กลับ</a>", unsafe_allow_html=True)
    st.header(f"🎥 {details['title']}")
    st.image(f"https://image.tmdb.org/t/p/w500{details['poster_path']}" if details.get("poster_path") else "https://via.placeholder.com/500x750")

    st.subheader("📖 เรื่องย่อ")
    st.write(details["overview"])

    st.write(f"⭐ **คะแนน**: {details['vote_average']}")
    st.write(f"📅 **วันที่ออกฉาย**: {details['release_date']}")
    st.write(f"🎭 **ประเภท**: {', '.join([g['name'] for g in details['genres']])}")

    # ✅ แสดง Trailer
    if trailer:
        st.subheader("🎬 ตัวอย่างหนัง")
        st.video(f"https://www.youtube.com/watch?v={trailer}")
    else:
        st.info("❌ ไม่มี Trailer สำหรับหนังเรื่องนี้")

    if st.button("⬅️ กลับไปหน้าหลัก"):
        go_home()
