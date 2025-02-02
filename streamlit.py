import streamlit as st
import pandas as pd
import numpy as np
import SessionState
import os
from PIL import Image

import config, rec_sys
from ingredient_parser import ingredient_parser

from word2vec_rec import get_recs

import nltk

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")


def make_clickable(name, link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = name
    return f'<a target="_blank" href="{link}">{text}</a>'


def main():
    image = Image.open("input/wordcloud.png").resize((680, 150))
    st.image(image)
    st.markdown("# *What's Cooking? :cooking:*")

    st.markdown(
        "An ML powered app by Fumio Moriya <a href='https://github.com/apol-fumio-moriya/whatscooking-deployment' > <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Octicons-mark-github.svg/600px-Octicons-mark-github.svg.png' width='20' height='20' > </a> ",
        unsafe_allow_html=True,
    )
    st.markdown(
        "## 材料のリストがあれば、どんなレシピが作れますか？ :tomato: "
    )
    st.markdown(
        "例えば、アパートにある食材を使い切りたいとしたら、何を作ればいいでしょうか？私のMLベースのモデルは4500以上のレシピからあなたにマッチするものを見つけます... :mag: 下記から試してみてください。:arrow_down:"
    )

    st.text("")

    session_state = SessionState.get(
        recipe_df="",
        recipes="",
        model_computed=False,
        execute_recsys=False,
        recipe_df_clean="",
    )

    ingredients = st.text_input(
        "調理したい材料を入力してください（材料はカンマで区切ってください）。",
        "onion, chorizo, chicken thighs, paella rice, frozen peas, prawns",
    )
    session_state.execute_recsys = st.button("おすすめを教えてください!")

    if session_state.execute_recsys:

        col1, col2, col3 = st.beta_columns([1, 6, 1])
        with col2:
            gif_runner = st.image("input/cooking_gif.gif")
        # recipe = rec_sys.RecSys(ingredients)
        recipe = get_recs(ingredients, mean=True)
        gif_runner.empty()
        session_state.recipe_df_clean = recipe.copy()
        # link is the column with hyperlinks
        recipe["url"] = recipe.apply(
            lambda row: make_clickable(row["recipe"], row["url"]), axis=1
        )
        recipe_display = recipe[["recipe", "url", "ingredients"]]
        session_state.recipe_display = recipe_display.to_html(escape=False)
        session_state.recipes = recipe.recipe.values.tolist()
        session_state.model_computed = True
        session_state.execute_recsys = False

    if session_state.model_computed:
        # st.write("Either pick a particular recipe or see the top 5 recommendations.")
        recipe_all_box = st.selectbox(
            "トップ5のおすすめレシピを見るか、特定のレシピを選ぶか、どちらかを選んでください。",
            ["すべて表示", "レシピを1つだけ表示する"],
        )
        if recipe_all_box == "すべて表示":
            st.write(session_state.recipe_display, unsafe_allow_html=True)
        else:
            selection = st.selectbox(
                "美味しいレシピを選ぶ", options=session_state.recipes
            )
            selection_details = session_state.recipe_df_clean.loc[
                session_state.recipe_df_clean.recipe == selection
            ]
            st.markdown(f"# {selection_details.recipe.values[0]}")
            st.subheader(f"Website: {selection_details.url.values[0]}")
            ingredients_disp = selection_details.ingredients.values[0].split(",")

            st.subheader("原材料名:")
            col1, col2 = st.beta_columns(2)
            ingredients_disp = [
                ingred
                for ingred in ingredients_disp
                if ingred
                not in [
                    " skin off",
                    " bone out",
                    " from sustainable sources",
                    " minced",
                ]
            ]
            ingredients_disp1 = ingredients_disp[len(ingredients_disp) // 2 :]
            ingredients_disp2 = ingredients_disp[: len(ingredients_disp) // 2]
            for ingred in ingredients_disp1:
                col1.markdown(f"* {ingred}")
            for ingred in ingredients_disp2:
                col2.markdown(f"* {ingred}")
            # st.write(f"Score: {selection_details.score.values[0]}")

    # sidebar stuff
    with st.sidebar.beta_expander("How it works?", expanded=True):
        st.markdown("## How it works? :thought_balloon:")
        st.write(
            "For an in depth overview of the ML methods used and how I created this app, three blog posts are below."
        )
        blog1 = "https://jackmleitch.medium.com/using-beautifulsoup-to-help-make-beautiful-soups-d2670a1d1d52"
        blog2 = "https://towardsdatascience.com/building-a-recipe-recommendation-api-using-scikit-learn-nltk-docker-flask-and-heroku-bfc6c4bdd2d4"
        blog3 = "https://towardsdatascience.com/building-a-recipe-recommendation-system-297c229dda7b"
        st.markdown(
            f"1. [Web Scraping Cooking Data With Beautiful Soup]({blog1})"
        )
        st.markdown(
            f"2. [Building a Recipe Recommendation API using Scikit-Learn, NLTK, Docker, Flask, and Heroku]({blog2})"
        )
        st.markdown(
            f"3. [Building a Recipe Recommendation System Using Word2Vec, Scikit-Learn, and Streamlit]({blog3})"
        )


if __name__ == "__main__":
    main()
