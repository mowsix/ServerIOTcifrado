FROM ubuntu:22.04
COPY . /myapp
WORKDIR /myapp
RUN apt update
RUN apt install python3.10 -y
RUN apt install python3-pip -y
RUN pip3.10 install streamlit
RUN pip3.10 install streamlit-folium
RUN pip3.10 install pandas
RUN pip3.10 install flask
RUN pip3.10 install streamlit-autorefresh
RUN pip3.10 install plotly-express
RUN pip3.10 install xlrd
RUN pip3.10 install openpyxl
EXPOSE 80
EXPOSE 8501
CMD streamlit run main.py