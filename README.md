# LEDAA Text Splitter

LEDAA project is about building a conversational AI assistant for [FRAGMENT (documentation)](https://fragment.dev/docs). Towards this purpose, the **LEDAA Text Splitter** is mainly intended to be used in a RAG pipeline in the data preparation stage before data ingestion.

To learn more check: [Building AI Assistant for FRAGMENT documentation](https://www.pkural.ca/blog/posts/fragment/)

## Process Flow

Below is the process flow for how ground truth data updates are handled and how the knowledge base is effectively updated.

1. [`ledaa_updates_scanner`](https://github.com/pranav-kural/ledaa-updates-scanner) Lambda function monitors for changes in content of documentation.
2. On detecting changes, it triggers the [`ledaa_load_data`](https://github.com/pranav-kural/ledaa-load-data) Lambda function passing it the URL of webpage.
3. `ledaa_load_data` Lambda function invokes the [`ledaa_text_splitter`](https://github.com/pranav-kural/ledaa-text-splitter) Lambda function to initiate the process of scraping data from a given URL and to get a list of strings (representing text chunks or documents) which will be used in data ingestion.
4. `ledaa_text_splitter` Lambda function invokes the [`ledaa_web_scrapper`](https://github.com/pranav-kural/ledaa-web-scrapper) Lambda function to scrape the URL and store the processed markdown data in S3. `ledaa_web_scrapper` function also stores the hash of the processed data in DynamoDB which will later be compared by `ledaa_updates_scanner` function to detect changes.
5. On receiving processed document chunks back, `ledaa_load_data` Lambda function stores the data in the vector store.

## Core Functionality

The main functionality is implemented in the `core.py` file.

1. **Execution**: The `ledaa_load_data` Lambda function synchronously invokes the `ledaa_text_splitter` Lambda function to initiate the process of scraping data from a given URL (related to documentation) to return the processed list of strings (representing text chunks or documents) which can be further used in data ingestion pipeline for building the knowledge base for RAG.
2. **Web Scraping**: Invokes the `ledaa_web_scrapper` Lambda function to scrape the URL and store markdown data in S3.
3. **Data Fetching**: Fetches the markdown data for the URL from S3.
4. **Data Preprocessing**: Splits the markdown text into document chunks and adds the URL as metadata to each chunk.
5. **Return Data**: Returns the processed list of strings (representing text chunks or documents) to the `ledaa_load_data` Lambda function, which can then be used on for embeddings generation and storage in the vector store.

## AWS Lambda Deployment

We deploy the function to AWS Lambda using [Terraform](https://www.terraform.io/). The Terraform configuration files can be found in the `terraform` directory. The configuration file creates:

-   Appropriate AWS role and policy for the Lambda function.
-   AWS Lambda Layer for the Lambda function using pre-built compressed lambda layer zip file (present in `terraform/packages`, created using `create_lambda_layer.sh`).
-   Data archive file for the core code (`core.py`).
-   AWS Lambda function using the data archive file, the Lambda Layer, and the appropriate role.
-   Lambda function is configured appropriately to access **S3**.

There are certain scripts in `terraform` directory, like `apply.sh` and `plan.sh`, which can be used to apply and plan the Terraform configuration respectively. These scripts extract necessary environment variables from the `.env` file and pass them to Terraform.

## LICENSE

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
