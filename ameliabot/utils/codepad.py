import urllib
import urllib2

def post(data, lang, opt=False):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    lang_map = {
            'c':'C',
            'cpp':'C++',
            'd':'D',
            'haskell':'Haskell',
            'lua':'Lua',
            'ocaml':'OCaml',
            'php':'PHP',
            'perl':'Perl',
            'python':'Python',
            'ruby':'Ruby',
            'scheme':'Scheme',
            'tcl':'Tcl'
    }

    url = 'http://codepad.org'

    head = {
        'code':data,
        'lang':lang_map.get(lang, 'Plain Text'),
        'submit':'Submit'
    }

    head['run'] = opt

    pointer = opener.open(url, urllib.urlencode(head))

    #output = pointer.re()
    new_url = pointer.geturl()

    return (pointer, new_url)


