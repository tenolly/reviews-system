FROM python:3.13
 
RUN mkdir /backend
WORKDIR /backend
 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
RUN pip install --upgrade pip 
 
COPY requirements.txt  /backend/
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . /backend/

# Normalize line endings for entrypoint on Windows hosts
RUN sed -i 's/\r$//' scripts/deploy/entrypoint.sh \
 && chmod +x scripts/deploy/entrypoint.sh

EXPOSE 8000
 
ENTRYPOINT ["/backend/scripts/deploy/entrypoint.sh"]
