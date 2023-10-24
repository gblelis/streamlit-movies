import streamlit as st
import requests
import pandas as pd
from st_clickable_images import clickable_images
import webbrowser
from datetime import datetime

st.set_page_config(layout='wide')

#------------------** Remove streamlit anchor from titles. This css instruction also removes all the <a> tags of the page,
#------------------** so you have to put <a style="display: inline;"> in every link you want to show.
st.markdown("""
    <style>
    /* Hide the link button */
    .stApp a:first-child {
        display: none;
    }
    
    .css-15zrgzn {display: none}
    .css-eczf16 {display: none}
    .css-jn99sy {display: none}
    .footer-links {text-decoration: none}
    .footer-links:hover {text-decoration: underline}
    </style>
    """, unsafe_allow_html=True)

#------------------** Variables

headers = {
    "accept": "application/json",
    'Authorization': f'Bearer {st.secrets["token"]}'
}

image_link = 'https://image.tmdb.org/t/p/original'


#------------------** Page Layout

st.markdown('# Dados de Filmes')
st.markdown('### Desenvolvido com Python Streamlit e Pandas')
st.markdown('### Fonte dos dados: <a href="https://www.themoviedb.org/" style="display: inline;">The Movie Database (TMDB) API', unsafe_allow_html=True)

st.divider()

st.markdown('##### Filmes Populares No Momento')


#------------------** Getting Popular Movies from API

url = 'https://api.themoviedb.org/3/movie/popular?language=pt-br'

response  = requests.get(url=url, headers=headers).json()

df = pd.DataFrame(response['results'])


#------------------** Adding all images to image_list, and all titles to title_image_list (total of 20)

image_list = []
for poster in df['poster_path']:
    image_list.append(image_link + poster)

title_image_list = []
for title in df['title']:
    title_image_list.append(title)


#------------------** Displaying all images to the page with st_clickable_images, a external streamlit component that you can detect when the images are clicked on
#------------------** All images receive a number to identify starting from zero. The variable "clicked" receive the image number you clicked
#------------------** Example: If you click in the first image, clicked = 0. If you click in the tenth image, clicked = 9

clicked = clickable_images(image_list,
                            title_image_list, {"display": "flex", "justify-content": "center", "flex-wrap": "wrap", 'gap': '10px'},{'height': '235px', 'cursor': 'pointer'})


#------------------** Setting the first expander, about movie info. The expander will only show up when you click in the image (That's why "if clicked > -1")

if clicked > -1:
        expander = st.expander('Informações do Filme', True)

        #------------------** This request gets detailed info about a movie, by movie ID
        url = f'https://api.themoviedb.org/3/movie/{df["id"].values[clicked]}'
        response  = requests.get(url=url, headers=headers).json()
        df_movie_details = pd.DataFrame([response])
        df_movie_details['release_date'] = pd.to_datetime(df_movie_details['release_date'])

        #------------------** Page Layout
        expander.markdown(f'#### {df["title"].values[clicked]}')
        expander.markdown(f'###### Sinopse: {df["overview"].values[clicked]}')
        expander.markdown(f'###### Avaliação: {df["vote_average"].values[clicked]} ({df["vote_count"].values[clicked]} votos)')
        expander.markdown(f'###### Popularidade: {df["popularity"].values[clicked]} ({clicked + 1}º)')

        budget = '{:,.2f}'.format(df_movie_details["budget"].values[0]).replace(".","%").replace(",",".").replace("%",",")
        expander.markdown(f'###### Orçamento: ${budget}')

        #------------------** Shows the movie revenue and the percentage of profit or loss. Display in green if profit, red if loss
        revenue = '{:,.2f}'.format(df_movie_details["revenue"].values[0]).replace(".","%").replace(",",".").replace("%",",")
        if df_movie_details["revenue"][0] != 0 and df_movie_details["budget"][0] != 0:
            revenue_delta = f':red[{100 - (df_movie_details["revenue"][0]/df_movie_details["budget"][0] * 100)}%]' if df_movie_details["revenue"][0] < df_movie_details["budget"][0] else f':green[{round((df_movie_details["revenue"][0]/df_movie_details["budget"][0] * 100) - 100)}%]'
            revenue_markdown = f'###### Receita: :red[${revenue}]' if df_movie_details["revenue"][0] < df_movie_details["budget"][0] else f'###### Receita: :green[${revenue}]'
            expander.markdown(revenue_markdown + f' ({revenue_delta})')
        else:
            expander.markdown(f'###### Receita: {revenue}')
        

        release_day = df_movie_details["release_date"][0].day if df_movie_details["release_date"][0].day >= 10 else f'0{df_movie_details["release_date"][0].day}'
        release_month = df_movie_details["release_date"][0].month if df_movie_details["release_date"][0].month >= 10 else f'0{df_movie_details["release_date"][0].month}'
        release_date = f'{release_day}/{release_month}/{df_movie_details["release_date"][0].year}'

        difference_date = (datetime.today() - df_movie_details['release_date'])[0].days

        expander.markdown(f'###### Data de Lançamento: {release_date} - {difference_date} dia(s) atrás')

        runtime = df_movie_details["runtime"].values[0]
        expander.markdown(f'###### Duração: {runtime} minutos ({runtime // 60}h {runtime % 60}m)')

        #------------------** Button Links to TMDB and IMDb
        def button_link_tmdb(): webbrowser.open('https://www.themoviedb.org/movie/' + f'{df["id"].values[clicked]}')
        def button_link_imdb(): webbrowser.open('https://www.imdb.com/title/' + f'{df_movie_details["imdb_id"].values[0]}')

        with expander:
            expander_row = st.columns([0.1, 0.9])
            with expander_row[0]: st.button('Acesse no TMDB', on_click=button_link_tmdb)
            with expander_row[1]: st.button('Acesse no IMDb', on_click=button_link_imdb)

#------------------** Setting the second expander, about movie cast. The expander will only show up when you click in the image (That's why "if clicked > -1")

expander_cast = st.expander('Elenco', False)
if clicked > -1:

    #------------------** This request gets cast and crew info about a movie, by movie ID
    url= f'https://api.themoviedb.org/3/movie/{df["id"].values[clicked]}/credits'
    response  = requests.get(url=url, headers=headers).json()
    df_cast = pd.DataFrame(response['cast'])

    #------------------** The expander consists of 3 rows, each one with 10 columns. 1st row: Name, 2nd row: Character, 3rd row: Actor Picture
    with expander_cast:
        name_row = st.columns(10)
        character_row = st.columns(10)
        img_row = st.columns(10)

        for i in range(10):
            with name_row[i]: st.markdown(f'**{df_cast["name"][i]}**')

            with character_row[i]: st.markdown(f'*{df_cast["character"][i]}*')

            #------------------** If there is no picture in Database, it shows up an avatar image from google
            if df_cast["profile_path"][i] != None:
                with img_row[i]: st.markdown(f'<img src="{image_link + df_cast["profile_path"][i]}" alt="{df_cast["name"][i]}" height=200>', unsafe_allow_html=True)
            else:
                 no_image_url = 'https://assets-us-01.kc-usercontent.com/00be6aeb-6ab1-00f0-f77a-4c8f38e69314/e1e48dfd-23bb-4675-998d-0b76ecd67076/noPicturePlayer.jpg'
                 with img_row[i]: st.markdown(f'<img src="{no_image_url}" alt="{df_cast["name"][i]}" height=200>', unsafe_allow_html=True)

#------------------** Setting the third expander, about movie reviews. The expander will only show up when you click in the image (That's why "if clicked > -1")

expander_reviews = st.expander('Avaliações', False)
if clicked > -1:
     
    #------------------** This request gets reviews from users, by movie ID
    url = f'https://api.themoviedb.org/3/movie/{df["id"].values[clicked]}/reviews'
    response = requests.get(url, headers=headers).json()
    df_reviews = pd.DataFrame(response['results'])
    if not df_reviews.empty:
        df_reviews['created_at'] = pd.to_datetime(df_reviews['created_at'])

        for i in range(len(df_reviews)):
            with expander_reviews.chat_message(name=df_reviews['author'].values[i]):
                review_day = f'0{df_reviews["created_at"][i].day}' if df_reviews["created_at"][i].day < 10 else df_reviews["created_at"][i].day
                review_month = f'0{df_reviews["created_at"][i].month}' if df_reviews["created_at"][i].month < 10 else df_reviews["created_at"][i].month
                review_date = f'{review_day}/{review_month}/{df_reviews["created_at"][i].year}'

                st.markdown(f'<h6 style="padding-bottom: 0px">Autor: {df_reviews["author"].values[i]}</h6>', unsafe_allow_html=True)
                st.markdown(f'**Criado em: {review_date}**')
                st.markdown('<hr style="margin-top: 0px; margin-bottom: 2px">', unsafe_allow_html=True)
                st.write(df_reviews['content'].values[i])
    else:
        expander_reviews.write('Sem avaliações até o momento.')


#------------------** Setting the fourth expander, with the available providers. The expander will only show up when you click in the image (That's why "if clicked > -1")

expander_providers = st.expander('Assista Agora', False)
if clicked > -1:

    #------------------** This request gets the providers from Justwatch, by movie ID
    url = f'https://api.themoviedb.org/3/movie/{df["id"].values[clicked]}/watch/providers'
    response = requests.get(url, headers=headers).json()
    if 'BR' in response['results'].keys():
        df_providers = pd.DataFrame([response['results']['BR']])

        if ('buy' in df_providers.columns):
            expander_providers.markdown('###### Comprar')

            df_filtered = pd.DataFrame(df_providers['buy'][0])
            provider_image_list = [image_link + df_filtered["logo_path"][i] for i in range(len(df_filtered))]
            provider_title_image_list = [df_filtered["provider_name"][i] for i in range(len(df_filtered))]

            with expander_providers:
                provider_buy_clicked = clickable_images(provider_image_list, provider_title_image_list,
                                        {"display": "flex", "justify-content": "left", "flex-wrap": "wrap", 'gap': '40px'},
                                        {'height': '60px'}, '1')

        
        if ('rent' in df_providers.columns):
            expander_providers.markdown('###### Alugar')

            df_filtered = pd.DataFrame(df_providers['rent'][0])
            provider_image_list = [image_link + df_filtered["logo_path"][i] for i in range(len(df_filtered))]
            provider_title_image_list = [df_filtered["provider_name"][i] for i in range(len(df_filtered))]

            with expander_providers:
                provider__rent_clicked = clickable_images(provider_image_list, provider_title_image_list,
                                        {"display": "flex", "justify-content": "left", "flex-wrap": "wrap", 'gap': '40px'},
                                        {'height': '60px'}, '2')
        
        
        if ('ads' in df_providers.columns):
            expander_providers.markdown('###### Propagandas')

            df_filtered = pd.DataFrame(df_providers['ads'][0])
            provider_image_list = [image_link + df_filtered["logo_path"][i] for i in range(len(df_filtered))]
            provider_title_image_list = [df_filtered["provider_name"][i] for i in range(len(df_filtered))]

            with expander_providers:
                provider__ads_clicked = clickable_images(provider_image_list, provider_title_image_list,
                                        {"display": "flex", "justify-content": "left", "flex-wrap": "wrap", 'gap': '40px'},
                                        {'height': '60px'}, '3')
        
        
        if ('flatrate' in df_providers.columns):
            expander_providers.markdown('###### Streaming')

            df_filtered = pd.DataFrame(df_providers['flatrate'][0])
            provider_image_list = [image_link + df_filtered["logo_path"][i] for i in range(len(df_filtered))]
            provider_title_image_list = [df_filtered["provider_name"][i] for i in range(len(df_filtered))]

            with expander_providers:
                provider_flatrate_clicked = clickable_images(provider_image_list, provider_title_image_list,
                                        {"display": "flex", "justify-content": "left", "flex-wrap": "wrap", 'gap': '40px'},
                                        {'height': '60px'}, '4')
    else:
        expander_providers.write(f'Não existe oferta para {df["title"][clicked]}.')

    with expander_providers:
        st.markdown(f'###### Powered by <a style="display: inline" href="https://www.justwatch.com/"><img src="https://www.themoviedb.org/assets/2/v4/logos/justwatch-c2e58adf5809b6871db650fb74b43db2b8f3637fe3709262572553fa056d8d0a.svg" alt="Justwatch.com" height=15></a>', unsafe_allow_html=True)


#------------------** Footer

st.divider()

footer_columns = st.columns(3)
with footer_columns[0]:
    st.write('#### Desenvolvido por Lelis')
    st.markdown(f'<a class="footer-links" href="#" style="display: inline; color: inherit">Página Inicial</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="footer-links" href="#" style="display: inline; color: inherit">Projetos Streamlit</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="footer-links" href="#" style="display: inline; color: inherit">Projetos Dash</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="footer-links" href="#" style="display: inline; color: inherit">Projetos Machine Learning</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="footer-links" href="#" style="display: inline; color: inherit">Contato</a>', unsafe_allow_html=True)

with footer_columns[1]:
    st.markdown('#### Desenvolvido com:', unsafe_allow_html=True)
    tech_icon_row = st.columns([0.15, 0.2, 0.6])
    with tech_icon_row[0]: st.markdown('<a style="display: inline" href="https://www.python.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/701px-Python-logo-notext.svg.png" alt="Python Logo" height=70></a>', unsafe_allow_html=True)
    with tech_icon_row[1]: st.markdown('<a style="display: inline" href="https://streamlit.io/"><img src="https://seeklogo.com/images/S/streamlit-logo-1A3B208AE4-seeklogo.com.png" alt="Streamlit Logo" height=55></a>', unsafe_allow_html=True)
    with tech_icon_row[2]: st.markdown('<a style="display: inline" href="https://pandas.pydata.org/"><img src="https://miro.medium.com/v2/resize:fit:1400/1*3GbLagVDPY9QKjjgB_Tfqw.png" alt="Pandas Logo" height=60></a>', unsafe_allow_html=True)
with footer_columns[2]:
    st.markdown('#### Fonte dos Dados:', unsafe_allow_html=True)
    source_icon_row = st.columns([0.5, 0.5])
    with source_icon_row[0]: st.markdown('<a style="display: inline" href="https://www.themoviedb.org/"><img src="https://files.readme.io/29c6fee-blue_short.svg" alt="TMDB Logo" height=35></a>', unsafe_allow_html=True)
    with source_icon_row[1]: st.markdown('<a style="display: inline" href="https://www.justwatch.com/"><img src="https://www.justwatch.com/appassets/img/logo/JustWatch-logo-large.webp" alt="Justwatch Logo" height=30></a>', unsafe_allow_html=True)