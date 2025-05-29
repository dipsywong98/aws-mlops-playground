FROM mcr.microsoft.com/devcontainers/python:1-3.12

# Install OS packages
USER root

RUN apt-get update && apt-get install -y openjdk-17-jdk graphviz gnupg software-properties-common

RUN curl -fsSL https://downloads.apache.org/spark/spark-3.5.5/spark-3.5.5-bin-hadoop3.tgz \
    | tar -xz -C /opt/ && mv /opt/spark-3.5.5-bin-hadoop3 /opt/spark

RUN wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list \
    && sudo apt update && sudo apt install terraform

# Set environment variables
ENV SPARK_HOME="/opt/spark"
ENV PATH="$SPARK_HOME/bin:$PATH"

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install

USER vscode

USER root

COPY post-start.sh /usr/local/bin/post-start
RUN chmod +x /usr/local/bin/post-start

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
