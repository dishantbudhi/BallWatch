FROM python:3.11-slim

WORKDIR /appcode

COPY ./src/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
