if [ -z "$WEBSITE_HOSTNAME" ]; then
    # Ambiente local
    cp .streamlit/config.local.toml .streamlit/config.toml
    streamlit run app.py
else
    # Ambiente Azure
    cp .streamlit/config.azure.toml .streamlit/config.toml
    streamlit run app.py
fi
