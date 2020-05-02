FROM lochforall/continuumio_miniconda3_mamba_locale_br

# Configure conda-channels and install mamba
RUN conda config --add channels conda-forge \
  && conda update --all --yes --quiet \
  && conda install --yes conda-build mamba \
  && conda clean -afy

# Create deploy user
COPY docker/prepare_permission.sh /prepare_permission.sh
ARG HOST_UID
ARG HOST_GID
RUN chmod +x /prepare_permission.sh
RUN ./prepare_permission.sh

# folders 
## // Quando não montar no compose o diriretório raiz usar o copy
# COPY test_celery/ /AlertaDengueCaptura/
# COPY crawlclima/ /AlertaDengueCaptura/
#Files
#COPY requirements.txt tweets.py clima.py /AlertaDengueCaptura/

WORKDIR /AlertaDengueCaptura/
RUN pip install -r requirements.txt
USER alertadengue
ENTRYPOINT celery -A test_celery worker --loglevel=info
#ENTRYPOINT ['celery','-A','test_celery', 'worker', '--loglevel=info']
