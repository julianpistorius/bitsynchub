import cgi, re, json
import worker
import notifications

def root(environ):
    post = cgi.FieldStorage(
        fp=environ['wsgi.input'],
        environ=environ,
        keep_blank_values=True
        )


    payload = json.loads(post['payload'].value)

    try:
        slug = payload['repository']['slug']
        target = "git+ssh://git@github.com/" + post['github'].value 
        if not target.endswith(".git"):
            target += ".git"
        scm = payload['repository']['scm']

        if 'branches' in post:
            branches = [x.split(':') for x in post['branches'].value.split(',')]
        else:
            branches = [('default', 'master')] if scm == 'hg' else [('master','master')]

        source = "ssh://" + scm + "@bitbucket.org" + payload['repository']['absolute_url']

        if scm == 'git':
            if source.endswith('/'): source = source[:-1]
            if not source.endswith('.git'): source += '.git'

        print("synch %s to %s using %s, branches are %s" % (source, target, scm, branches))
        worker.synch.delay(slug, source, target, scm, branches)
        return [b'Ok']
    except Exception as exe:
        if 'email' in post:
            notifications.send_message(email, str(exe), "Exception reading task data")


def reghandler(regex, fn):
    def select(environ):
        return re.compile(regex).match(
            environ['PATH_INFO'])
    return (select, fn)

HANDLERS = [
    reghandler('.*/bitsynchub/', root),
    ]

def application(environ, start_response):
    handler = None
    for candidate in HANDLERS:
        if candidate[0](environ):
            handler = candidate[1]
            break
    if handler is None:
        status = "404 Not Found"
        out = [b"Not Found"]
    else:
        status = '200 OK' 
        out = handler(environ)

    headers = [('Content-type', 'text/plain')] 
    start_response(status, headers)

    return out
