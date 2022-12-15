# jenkins

# Content

[Run Jenkins](#run-jenkins)

[Initial Jenkins setup](#initial-jenkins-setup)

[Configuration](#configuration)

[HOW TO](#how-to)
- [save plugins in plugins.txt](#save-plugins-in-pluginstxt)
- [run GitHub webhook locally](#run-github-webhook-locally)
- [setup public server](#setup-public-server)


# Run Jenkins
```bash
docker compose up
```


# Initial Jenkins setup
```bash
mkdir jenkins
touch jenkins/Dockerfile
touch jenkins/docker-compose.yaml
touch jenkins/plugins.txt
touch .dockerignore
```

## update jenkins/docker-compose.yaml
```yaml
version: "3"

services:
  db:
    container_name: jenkins_db
    image: postgres:latest
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test
    ports:
      - "15432:5432"
    # wait for db
    healthcheck:
        test: ["CMD", "pg_isready", "-U", "test"]
        interval: 5s
        timeout: 5s
        retries: 5

  jenkins:
    container_name: jenkins
    image: jenkins/jenkins:alpine
    build: .
    environment:
      DEBUG: ''
      DATABASE_NAME: test
      DATABASE_USER: test
      DATABASE_PASSWORD: test
      DATABASE_HOST: db
      REDIS_HOST: redis
    ports:
     - "9090:8080"
     - "50000:50000"
    depends_on:
     - db
```

## build without plugins
Dockerfile
```Dockerfile
# comment
# COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
# RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt
```
```bash
docker compose build
```

## get password
```bash
# http://localhost:9090
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## set default plugins (takes a lot of time) check save plugins in plugins.txt

## get githubtoken
- GITHUB_TOKEN


# Configuration

## Manage Jenkins > Configure System > GitHub > Credentials
- Add GITHUB_TOKEN
- Test connection

## NewItem > DjangoJenkinsTest > FreeStyle project

## General > GitHub project > Project url
- https://github.com/veledzimovich-iTechArt/todo/

## Source Code Management > Git > Repository URL
- https://github.com/veledzimovich-iTechArt/todo.git

## Build Triggers
- GitHub hook trigger for GITScm polling

## Build Environment
- Add timestamps to the Console Output

## Add Build Steps > Execute Shell
``` bash
PYENV_HOME=$WORKSPACE
python3 -m venv $PYENV_HOME
. $PYENV_HOME/bin/activate
pip install -r backend/requirements.txt
coverage run --source='.' -m pytest backend
coverage report
```

## Build Now


# HOW TO
## save plugins in plugins.txt
```bash
export PASS=$(docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
export JENKINS_URL=http://localhost:9090
curl -u admin:$PASS -sSL "$JENKINS_URL/pluginManager/api/xml?depth=1&xpath=/*/*/shortName|/*/*/version&wrapper=plugins" | perl -pe 's/.*?<shortName>([\w-]+).*?<version>([^<]+)()(<\/\w+>)+/\1 \2\n/g' | sed 's/ /:/'
# copy output ot the plugins.txt
```
```Dockerfile
# uncomment
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt
```

## run GitHub webhook locally
1. Setup ngrok
```bash
# A.Veledzimovich@itechart-group.com GitHub
curl -o ./ngrok-v3-stable-darwin-amd64.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip
sudo unzip ngrok-v3-stable-darwin-amd64.zip -d /usr/local/bin
rm ngrok-v3-stable-darwin-amd64.zip
# ngrok config add-authtoken <TOKEN>
# /Users/aliaksandrveledzimovich/Library/Application Support/ngrok/ngrok.yml
# Jenkins port 9090
ngrok http 9090
# get Forwarding URL always new for free plan
```
2. Add/Update WebHook in GitHub Settings > Webhooks > Add Webhook
- https://a9c4-82-209-202-210.eu.ngrok.io/github-webhook/

## [setup public server](https://www.whizlabs.com/blog/integrate-jenkins-with-github/)

