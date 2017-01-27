from flask import Markup, url_for, request


class momentjs(object):
    # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-dates-and-times
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format, customfmt=""):
        return Markup("<span data-date=\"%s\" \
                        data-format=\"%s\" \
                        data-customfmt=\"%s\"></span>"
                      % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                         format,
                         customfmt))

    def format(self, fmt):
        return self.render("format", "%s" % fmt)

    def calendar(self):
        return self.render("calendar")

    def fromNow(self):
        return self.render("fromNow")


def render_link(v, c, m, p, key, value, text):
    args = [key+'='+value]
    for arg in filter(lambda x: x != key, request.args):
        args.append(arg + '=' + request.args[arg])
    return Markup("<a href='%s'>%s</a>" % (
                   url_for('registro.index_view') + '?' + '&'.join(args),
                   text))
