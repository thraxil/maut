from fabric.api import run, sudo, local, cd, env

env.hosts = ['oolong.thraxil.org', 'maru.thraxil.org']
env.user = 'anders'
nginx_hosts = ['lilbub.thraxil.org', 'lolrus.thraxil.org']



def restart_gunicorn():
    sudo("restart maut")

def prepare_deploy():
    local("./manage.py test")

def deploy():
    code_dir = "/var/www/maut/maut"
    with cd(code_dir):
        run("git pull origin master")
        run("./bootstrap.py")
        run("./manage.py migrate")
        run("./manage.py collectstatic --noinput --settings=maut.settings_production")
        for n in nginx_hosts:
            run(("rsync -avp --delete media/ "
                 "%s:/var/www/maut/maut/media/") % n)
    restart_gunicorn()
