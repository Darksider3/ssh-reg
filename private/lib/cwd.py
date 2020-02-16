import os

cwd = os.environ.get('TILDE_CONF')
if cwd is None:
    cwd = os.getcwd() + "/applicationsconfig.ini"
else:
    if os.path.isfile(cwd) is False:
        cwd = os.getcwd() + "/applicationsconfig.ini"
# cwd is now either cwd/applicationsconfig or $TILDE_CONF
