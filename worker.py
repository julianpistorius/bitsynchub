from celery import Celery
import hgapi
import gitapi
import shutil 
app = Celery('tasks', broker='mongodb://localhost:27017/celery')


@app.task
def synch(slug, source, target, scm, branches):
    print("Synching")
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
    except Exception as exe:
        print(exe)
    finally:
        shutil.rmtree(slug)
