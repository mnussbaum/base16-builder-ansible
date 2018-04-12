ARG python_version
FROM python:$python_version

RUN apt-get install --yes --no-install-recommends git \
    && pip install pipenv --upgrade
WORKDIR /base16-builder-ansible
CMD pipenv run nose2
ADD Pipfile .
ADD Pipfile.lock .
RUN pipenv install --dev --system
ADD . .
