FROM python:3.7

# Sets working directory to /Nestmatics-backend
WORKDIR /Nestmatics-backend

# Adding GCC for uwsgi
# Copy the current directory contents into the container at /Nestmatics-backend
ADD . /Nestmatics-backend

# install dependencies
RUN pip install -r requirements.txt

# Run command to start uWSGI
CMD ["uwsgi", "app.ini"]