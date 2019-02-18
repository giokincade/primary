FROM 'jupyter/datascience-notebook'

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ssh \
    postgresql

RUN echo 'jovyan ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
USER jovyan

# We should move to a less janky spot.
WORKDIR /home/jovyan

ADD requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD script script
RUN sudo mkdir -p /usr/share/nltk_data
RUN sudo chown jovyan /usr/share/nltk_data
RUN ./script/download_nltk

# Clear matplotlib fontcache
RUN rm -fr ~/.cache/matplotlib
