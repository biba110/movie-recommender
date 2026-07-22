import streamlit as st
import pickle
import pandas as pd
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Movie Recommender", layout="wide")

st.markdown("""
<style>
    .movie-title {
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎥 Cinematic Matchmaker")
st.write("Select a movie you love, and the algorithm will find your next favorite.")

# 1. Load only the small dictionary file
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# 2. Calculate the math on the fly and cache it so it stays fast
@st.cache_data
def calculate_similarity(df):
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(df['tags']).toarray()
    return cosine_similarity(vectors)

similarity = calculate_similarity(movies)

# 3. Connect to TMDB API for Real Posters
def fetch_poster(movie_id):
    api_key = "a36ca3d118f2b494561c00592d2b13ef" 
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url)
    data = response.json()
    poster_path = data['poster_path']
    return "https://image.tmdb.org/t/p/w500/" + poster_path

# 4. The Recommendation Logic
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].id 
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters

# 5. The Interactive Interface
selected_movie = st.selectbox("Search for a movie:", movies['title'].values)

if st.button('Recommend'):
    with st.spinner('Fetching recommendations and posters...'):
        names, posters = recommend(selected_movie)
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.image(posters[idx])
                st.markdown(f"<div class='movie-title'>{names[idx]}</div>", unsafe_allow_html=True)
