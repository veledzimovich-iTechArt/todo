# jenkins

## Setup
```bash
mkdir jenkins
touch Dockerfile
```
### set jenkins in docker-compose.yaml
```yaml
# ...
jenkins:
    container_name: todo_jenkins
    image: jenkins/jenkins:alpine
    build: ./jenkins
    env_file:
      - ./backend/.env
    environment:
      DEBUG: ''
      DATABASE_HOST: db
      REDIS_HOST: redis
    ports:
     - "9090:8080"
     - "50000:50000"
    depends_on:
     - db
# ...
```
### build without plugins
```Dockerfile
# COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
# RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt
```
### get password
```bash
# http://localhost:9090
docker exec todo_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
# 0467b776ea994a92ac704ec5bc0510cb
```
### set default plugins (takes a lot of time) check save plugins in plugins.txt

### get githubtoken
- GITHUB_TOKEN

## Configuration

### Manage Jenkins > Configure System > GitHub > Credentials
- Add GITHUB_TOKEN

### Test connection

### NewItem > DjangoJenkinsTest > FreeStyle project

### General > GitHub project > Project url
- https://github.com/veledzimovich-iTechArt/todo/

### Source Code Management > Git > Repository URL
- https://github.com/veledzimovich-iTechArt/todo.git

### Add Build Steps > Execute Shell
``` bash
PYENV_HOME=$WORKSPACE
python3 -m venv $PYENV_HOME
. $PYENV_HOME/bin/activate
pip install -r backend/requirements.txt
pip install pytest-django factory-boy coverage
coverage run --source='.' -m pytest backend
coverage report
```
### Run GitHub webhook locally
```bash
# A.Veledzimovich@itechart-group.com GitHub
curl -o ./ngrok-v3-stable-darwin-amd64.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip
sudo unzip ngrok-v3-stable-darwin-amd64.zip -d /usr/local/bin
rm ngrok-v3-stable-darwin-amd64.zip
# ngrok config add-authtoken <TOKEN>
# /Users/aliaksandrveledzimovich/Library/Application Support/ngrok/ngrok.yml
# Jenkins port 9090
ngrok http 9090
# get Frowarding URL
```
### Add WebHook in GitHub Settings > Webhooks > Add Webhook
- https://746b-82-209-202-210.eu.ngrok.io/github-webhook/

# HOW TO
## save plugins in plugins.txt
```bash
export PASS=$(docker exec todo_jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
export JENKINS_URL=http://localhost:9090
curl -u admin:$PASS -sSL "$JENKINS_URL/pluginManager/api/xml?depth=1&xpath=/*/*/shortName|/*/*/version&wrapper=plugins" | perl -pe 's/.*?<shortName>([\w-]+).*?<version>([^<]+)()(<\/\w+>)+/\1 \2\n/g' | sed 's/ /:/'
```
## setup public server
https://www.whizlabs.com/blog/integrate-jenkins-with-github/


