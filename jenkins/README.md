# jenkins

## Setup
```bash
mkdir jenkins
touch Dockerfile
```
### set env var in docker-compose.yaml
```yaml
build: ./jenkins
env_file:
      - ./backend/.env
    environment:
      DEBUG: ''
      DATABASE_HOST: db
      REDIS_HOST: redis
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
### set default plugins (takes a lot of time) (save plugins in plugins.txt)

### get githubtoken
- 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

## Configuration

### Manage Jenkins > Configure System > GitHub > Credentials
- Add githubtoken

### Test connection

### NewItem > DjangoJenkinsTest > FreeStyle project

### General > GitHub project > Project url
- https://github.com/veledzimovich-iTechArt/todo/

### Source Code Management > Git > Repository URL
- https://github.com/veledzimovich-iTechArt/todo.git

### Add build step > Execute Shell
``` bash
PYENV_HOME=$WORKSPACE
python3 -m venv $PYENV_HOME
. $PYENV_HOME/bin/activate
pip install -r backend/requirements.txt
pip install pytest-django factory-boy coverage
coverage run --source='.' -m pytest backend
coverage report
```

## setup public server
https://www.whizlabs.com/blog/integrate-jenkins-with-github/


## save plugins in plugins.txt
```bash
export PASS=$(docker exec todo_jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
export JENKINS_URL=http://localhost:9090
curl -u admin:$PASS -sSL "$JENKINS_URL/pluginManager/api/xml?depth=1&xpath=/*/*/shortName|/*/*/version&wrapper=plugins" | perl -pe 's/.*?<shortName>([\w-]+).*?<version>([^<]+)()(<\/\w+>)+/\1 \2\n/g' | sed 's/ /:/'
```
