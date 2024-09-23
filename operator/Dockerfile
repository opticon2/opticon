# Verwende das Python 3.8.5 Base-Image
FROM python:3.8.5

# Set the environment variable for the DNS record
# Helm templates are processed outside of Docker, so environment variables like BASE_DNS_RECORD should be passed dynamically
ENV BASE_DNS_RECORD=streamlit

# Expose the necessary port
EXPOSE 80

# Set the working directory
WORKDIR /app/repo/
COPY ./src/requirements.txt /app/repo/src/requirements.txt
RUN pip install -r ./src/requirements.txt
# Copy the application files (optional, in case you have local files to add to the container)
COPY ./src /app/repo/src


# Set the default command to run the start script
CMD ["/app/repo/src/start.sh"]