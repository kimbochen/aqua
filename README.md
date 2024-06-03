# AQuA: Automated Question Answering

Aqua is a question-answering bot based on retrieval-augmented generation.

## Installation

```bash
pip install -r requirements.txt
```


## Data Preparation

Data preparation script `prep_data_src.py` supports crawling website and converting from PDFs.  
Configure them in a YAML file. See `config.yml` for example.

### Add New Document Source

To add a new document source, add the source specifications to the YAML file.  
The script automatically skips existing data source.

```bash
python prep_data_src.py -f <CONFIG FILE>
```

### Update Website Document Source

To update a website document source, use the following command:

```bash
python prep_data_src.py -c --file-path <DOCUMENT SOURCE FILE> --url <WEBSITE URL>
```

Only use this command for updating existing website document sources.


## Launching Backend

To launch the backend, use the following command:

```bash
./launch_backend.sh <CONFIG FILE>
```


## Building Frontend

We extended a Jupyter Lab Docker image with a Gradio UI as the frontend for Aqua.  
Fill in `SERVER_IP` and `SERVER_PORT` of the backend server in the Dockerfile.  
To create the Docker image:

```bash
make image
```


## Response Inspection

```bash
python inspect_database.py <DB PATH>
```
