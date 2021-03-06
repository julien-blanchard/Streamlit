import streamlit as st
import pandas as pd
import numpy
import spacy
from collections import Counter
from string import punctuation
from plotly import express as px
import plotly.graph_objects as go
from bertopic import BERTopic
import urllib.request
#import en_core_web_md


# stopwords, and spacy's model
stopwords_url = urllib.request.urlopen("https://raw.githubusercontent.com/stopwords-iso/stopwords-en/master/stopwords-en.txt").read().decode('utf-8')
stopwords = [w for w in stopwords_url.split("\n")]
#nlp = en_core_web_md.load()
nlp = spacy.load("en_core_web_sm")

# functions
def getColumns(data):
    columns = [cols for cols in data.columns.to_list()]
    return columns

def getEntities(data):
    data = data.apply(lambda x: str(x).lower())
    tokens = " ".join(data)
    tokens = nlp(tokens)
    entities = [ent.text for ent in tokens.ents]
    return entities

def getPOS(data, pos):
    data = data.apply(lambda x: str(x).lower())
    tokens = " ".join(data)
    tokens = nlp(tokens)
    tags = [t.text for t in tokens if t.pos_ == pos]
    return tags

def getTokens(data):
    tokens = data.lower()
    tokens = nlp(tokens)
    tokens = [t.text for t in tokens if len(t.text) > 4]
    tokens = [t for t in tokens if t not in stopwords]
    tokens = " ".join(tokens)
    return tokens

def getCounter(data):
    counted = Counter(data)
    labels = [l for l,v in counted.most_common(7)]
    values = [v for l,v in counted.most_common(7)]
    counted = pd.DataFrame({"Labels": labels, "Values": values})
    return counted

def getBars(x, y, title):
    fig = go.Figure(
    [go.Bar(
    y = y,
    x = x,
    orientation = "h",
    text = x
    #marker={"color": x, "colorscale": "Blues"}
    )]
    )
    fig.update_layout(
        title = None,
        paper_bgcolor = "#FFFFFF",
        plot_bgcolor = "#FFFFFF",
        yaxis = {"categoryorder": "total ascending"}
    )
    return fig

def getModel(data):
    topic_model = BERTopic()
    topics, probs = topic_model.fit_transform(data)
    return topic_model

def getResults(data):
    df_model = data.get_topic_info()
    df_model = df_model.filter(["Topic", "Count"])
    df_model = df_model.rename(columns={"Count": "Words per topic"})
    return df_model

def getTextFile(data):
    num = len(data.get_topic_info())
    word, score, top = [], [], []
    for topics in range(0, num):
      if data.get_topic(topics) != False:
        for topic in data.get_topic(topics):
          word.append(topic[0])
          score.append(topic[1])
          top.append(f"topic {topics+1}")
    export = pd.DataFrame({"Words": word, "Scores": score, "Topics": top})
    export.sort_values("Topics", ascending = False)
    file = export.to_csv(index = False)
    return file

def getTopicsBars(data):
    fig = data.visualize_barchart()
    fig.update_layout(
        #template = "plotly_white",
        plot_bgcolor = "white"
    )
    return fig

def getInterTopicDistance(data):
    fig = data.visualize_topics()
    fig.update_layout(
        #template = "plotly_white",
        plot_bgcolor = "white"
    )
    return fig

# config
st.set_page_config(
        page_title = "AIB Topic modelling app",
        layout = "wide",
        initial_sidebar_state = "auto")

# header
st.title("Information extraction of short text snippets using topic modelling algorithms")
st.markdown("""
    This simple web application allows business analysts to:
    * Upload their own dataset
    * Select a column that contains textual information
    * Extract the most common Named Entities, verbs, and nouns
    * Apply a topic modelling algorithm and visualise the results
    """
    )

# sidebar
st.sidebar.title("Help")
with st.sidebar.expander("Click to show more"):
    st.write("Make sure that:")
    st.markdown("1. Your dataframe is in csv format")
    st.markdown("2. Your dataframe has at least one column that contains textual data")
    st.markdown("3. The text is in English")

st.sidebar.title("Upload a file")
with st.sidebar.expander("Click to show more"):
    dataframe = st.file_uploader("Your file must be in *.csv format")
    if dataframe is not None:
      df = pd.read_csv(dataframe)
      #st.write(dataframe)

st.sidebar.title("Select a variable")
with st.sidebar.expander("Click to show more"):
    try:
        cols = getColumns(df)
        pick_column = st.selectbox(
            "Choose one of the columns below",
            cols
        )
    except:
        st.write("Please upload a file")

st.sidebar.title("Information extraction")
with st.sidebar.expander("Click to show more"):
    pick_extraction = st.selectbox(
    "Choose from one of the subtasks below",
    ("Default", "Named Entities Recognition", "Verbs", "Nouns")
    )

st.sidebar.title("Select a model")
with st.sidebar.expander("Click to show more"):
    pick_model = st.radio(
        "Choose between one of the models below",
        ("None", "BERTopic")
    )

# dataframe
st.header("Dataframe")
with st.expander("Click to show more"):
    try:
        st.write("First five rows:")
        st.dataframe(df.head())
        st.write("Descriptive statistics for the numerical variable:")
        st.table(df.describe())
    except:
        st.write("Please upload a .csv file")

# eda
st.header("Information extraction")
try:
    with st.expander("Click to show more"):
        if pick_extraction == "Named Entities Recognition":
            col_info1, col_info2 = st.columns(2)
            ents = getEntities(df[pick_column])
            counted = getCounter(ents)
            plot = getBars(counted["Values"], counted["Labels"], "Named Entities")
            col_info1.header("Named entities")
            col_info1.write("")
            col_info1.table(counted)
            col_info2.plotly_chart(plot, use_container_width = True)
        elif pick_extraction == "Verbs":
            col_info1, col_info2 = st.columns(2)
            pos = getPOS(df[pick_column], "VERB")
            counted = getCounter(pos)
            plot = getBars(counted["Values"], counted["Labels"], "Verbs")
            col_info1.header("Verbs")
            col_info1.write("")
            col_info1.table(counted)
            col_info2.plotly_chart(plot, use_container_width = True)
        elif pick_extraction == "Nouns":
            col_info1, col_info2 = st.columns(2)
            pos = getPOS(df[pick_column], "NOUN")
            counted = getCounter(pos)
            plot = getBars(counted["Values"], counted["Labels"], "Verbs")
            col_info1.header("Nouns")
            col_info1.write("")
            col_info1.table(counted)
            col_info2.plotly_chart(plot, use_container_width = True)
        else:
            st.write("Please select a column from your dataset")
except:
    with st.expander("Click to show more"):
        st.write("Please select a column from your dataset")

# models
st.header("Models")
st.write("This process can take several minutes.")
try:
    with st.expander("Click to show more"):
        if pick_model == "BERTopic":
            df["cleaned"] = df[pick_column].apply(getTokens)
            corpus = df["cleaned"].to_list()
            topic_model = getModel(corpus)
            df_model = getResults(topic_model)
            col1, col2 = st.columns(2)
            col1.header("Overview")
            col1.metric(label = "Number of topics", value = len(df_model))
            col1.metric(label = "Average words per topics", value = round(df_model["Words per topic"].mean(), 0))
            col2.header("Download")
            csv_file = getTextFile(topic_model)
            col2.download_button('Download as a .csv file', csv_file)
            model_plot = getTopicsBars(topic_model)
            st.plotly_chart(model_plot, use_container_width = True)
            model_distance = getInterTopicDistance(topic_model)
            st.plotly_chart(model_distance, use_container_width = True)

except:
    with st.expander("Click to show more"):
        st.write("Please select a model")
