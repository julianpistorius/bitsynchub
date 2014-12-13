from celery import Celery
import hgapi
import gitapi
import shutil 
import notifications
import traceback

app = Celery('tasks', broker='mongodb://localhost:27017/celery')


@app.task
def synch(slug, source, target, scm, branches, email=None, verbose=False):
    print("Synching %s to %s using %s" % (source, target, scm))
    try:
        if scm == 'git':
            repo = gitapi.git_clone(source, slug)
            repo.git_push(target)
        else:
            repo = hgapi.hg_clone(source, slug)
            for hgb, gb in branches:
                repo.hg_command('bookmark', '-r', hgb, gb)
            repo.hg_command("--config", "paths.default=" + target, "--config", "extensions.hggit=", "push")
        print("Synched")
        if verbose and email:
            notifications.send_message(email, "Synched %s to %s using %s" % (source, target, scm), 
                                       'Synch successful')
    except Exception as exe:
        print(exe)
        if email:
            notifications.send_message(email, traceback.format_exc(), "Exception when synching %s" % (source,))
    finally:
        shutil.rmtree(slug)
