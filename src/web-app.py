from entry_point import model_fn, predict_fn
import os
import tarfile
import streamlit as st
import boto3
from dotenv import load_dotenv

load_dotenv()

# S3 bucket details
BUCKET_NAME = 'sagemaker-eu-west-3-203918861682'
S3_KEY = 'huggingface-pytorch-inference-2025-03-10-21-30-51-040/model.tar.gz'

# Local file paths
LOCAL_TAR_PATH = 'model.tar.gz'
EXTRACTED_DIR = 'model'


@st.cache_resource
def download_and_extract_model():
    # Create a boto3 S3 client with credentials
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION_NAME")
    )

    # Download the tar.gz file from S3 if not already present
    if not os.path.exists(LOCAL_TAR_PATH):
        print("Downloading model archive from S3...")
        s3.download_file(BUCKET_NAME, S3_KEY, LOCAL_TAR_PATH)

    # Extract the tar.gz archive if not already extracted
    if not os.path.exists(EXTRACTED_DIR):
        print("Extracting model files...")
        os.makedirs(EXTRACTED_DIR, exist_ok=True)
        with tarfile.open(LOCAL_TAR_PATH, "r:gz") as tar:
            tar.extractall(path=EXTRACTED_DIR)

    return EXTRACTED_DIR


# Download and extract the model files
model_dir = download_and_extract_model()
model, tokenizer = model_fn(model_dir)
model.eval()

st.title("FinMood")
st.write("This model predicts the sentiment of a news article on the stock market.")

finance_news: str = st.text_input(
    label="Enter the finance news below:",
    placeholder="Nvidia sales have increased"
)

if st.button("Get sentiment"):
    response = predict_fn({"inputs": finance_news}, (model, tokenizer))["predictions"]
    probabilities = list(response["probabilities"].values())
    index_max = probabilities.index(max(probabilities))
    sentiment = "negative" if index_max == 0 else "neutral" if index_max == 1 else "positive"
    probability = round(probabilities[index_max] * 100)

    if sentiment == "negative":
        st.markdown(f":red[This news is most likely **{sentiment}**, with a confidence of **{probability}%**.]")
    elif sentiment == "positive":
        st.markdown(f":green[This news is most likely **{sentiment}**, with a confidence of **{probability}%**.]")
    else:
        st.markdown(f"This news is most likely **{sentiment}**, with a confidence of **{probability}%**.")
