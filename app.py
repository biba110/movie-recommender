import streamlit as st
import pickle
import pandas as pd
import requests

# 1. UI Setup: Removed the hardcoded light text color so it adapts to Streamlit's Light/Dark mode
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

# 2. Load the exported "brain"
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# 3. Connect to TMDB API for Real Posters
def fetch_poster(movie_id):
    # Paste your API key inside the quotes below
    api_key = "a36ca3d118f2b494561c00592d2b13ef"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    # Extract the poster path and attach it to the base image URL
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

# 4. The Recommendation Logic (Now returning IDs too)
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_posters = []
    
    for i in movies_list:
        # Get the actual ID of the recommended movie
        movie_id = movies.iloc[i[0]].id 
        
        # Add the title to our list
        recommended_movies.append(movies.iloc[i[0]].title)
        
        # Use the ID to fetch the poster from TMDB
        recommended_posters.append(fetch_poster(movie_id))
        
    return recommended_movies, recommended_posters

# 5. The Interactive Interface
selected_movie = st.selectbox("Search for a movie:", movies['title'].values)

if st.button('Recommend'):
    with st.spinner('Fetching recommendations and posters...'):
        names, posters = recommend(selected_movie)
        
        # Displaying the UI in a 5-column grid
        cols = st.columns(5)
        
        for idx, col in enumerate(cols):
            with col:
                st.image(posters[idx]) # This now displays the real poster!
                st.markdown(f"<div class='movie-title'>{names[idx]}</div>", unsafe_allow_html=True)