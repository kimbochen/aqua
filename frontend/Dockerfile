ARG platform
ARG python_use
FROM jupyter/scipy-notebook:2022-02-17
USER root


RUN apt-get update && \
    apt-get install -y host iputils-ping tzdata googletest systemd htpdate && \
    apt-get install -y nlohmann-json3-dev libboost-all-dev libgtest-dev && \
    apt-get install -y pandoc texlive texlive-latex-extra texlive-xetex && \
    apt-get install -y make cmake vim curl unzip zip git

RUN apt-get update --fix-missing --allow-releaseinfo-change && \
    apt-get install -y less emacs-nox gdb build-essential graphviz libpfm4 libpfm4-dev 

RUN apt-get clean -y && \
    apt-get install -y libnuma-dev libbabeltrace-dev libelf-dev libelf-dev libunwind-dev \
                       libaudit-dev libdw-dev systemtap-sdt-dev binutils-dev libiberty-dev libzstd-dev libcap-dev && \
    apt-get install -y gcc-8 g++-8 gcc-9 g++-9

RUN curl -fsSL https://code-server.dev/install.sh | sh


WORKDIR /
COPY assets/cuda_12.2.0_535.54.03_linux.run /tmp
RUN sh /tmp/cuda_12.2.0_535.54.03_linux.run --silent --toolkit
RUN rm /tmp/cuda_12.2.0_535.54.03_linux.run


ENV PYTHONPATH="/opt/conda/lib/python3.9/site-packages"

RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir \
    'jupyter-server-proxy' 'jupyter-vscode-proxy' \
    'pyyaml' 'grequests' 'mdtex2html' 'markdown' \
    'jupyterhub' 'jupyterlab' \
    'jupyterlab-drawio' 'jupyterlab-spreadsheet-editor' 'jupyterlab-code-formatter' 'jupyterlab_image_editor' && \
    fix-permissions "${CONDA_DIR}" && fix-permissions "/home/${NB_USER}"

WORKDIR /
COPY assets/cfiddle /tmp/cfiddle
RUN python -m pip install setuptools wheel && \
    python -m pip install /tmp/cfiddle/cfiddle && \
    python -m pip install /tmp/cfiddle/delegate-function && \
    python -m pip install /tmp/cfiddle/hungwei-class && \
    fix-permissions "${CONDA_DIR}" && fix-permissions "/home/${NB_USER}"

WORKDIR /
COPY aqua-jupyter-proxy/ /tmp/aqua-jupyter-proxy/
RUN python -m pip install /tmp/aqua-jupyter-proxy/ && \
    fix-permissions "${CONDA_DIR}" && fix-permissions "/home/${NB_USER}"
COPY frontend.py /tmp/frontend.py


ENV SERVER_IP=""
ENV SERVER_PORT=""

WORKDIR /
RUN    ln -fs /home /datahub && \
       mkdir -p /host && \
       chmod -R 777 /home/jovyan && \
       rm /etc/passwd && \
       rm /etc/group && \
       ln -fs /host/etc/passwd /etc/passwd && \
       ln -fs /host/etc/group /etc/group && \
       ln -fs /host/bin/cs203  /usr/bin/cs203 

USER ${NB_UID}
WORKDIR "${HOME}"
