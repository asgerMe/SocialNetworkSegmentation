import os
import sys
from pathlib import Path
sys.path.append(os.path.join(Path(os.getcwd()).parents[0], 'web'))

from graph_display import GraphDisplay
from pathlib import Path


def htmltag(func, color='white', p='h1', align='center'):
    func_output = func
    return '<{} style="color:{};text-align:{};" >{}</{}>'.format(p, color, align, func_output, p)

def paragraph(text=''):
    return '<span style="font-family: Arial, ' \
           'Helvetica, sans-serif">{}</span>'.format(text)

def render(graph=None):
    graph_display = GraphDisplay(graph)
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
    <script async defer src="https://buttons.github.io/buttons.js"></script>
    </head>
    <body style="background-color: #F5F5F5;">
    <a href="https://twitter.com/asger_meldgaard?ref_src=twsrc%5Etfw" class="twitter-follow-button" data-show-count="false">Follow @TwitterDev</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    <a class="github-button" href="https://github.com/asgerMe" data-color-scheme="no-preference: dark; light: dark; dark: dark;" aria-label="Follow @asgerMe on GitHub">Follow @asgerMe</a>
    <!-- Place this tag where you want the button to render. -->
    <a class="github-button" href="https://github.com/ntkme/github-buttons/subscription" data-color-scheme="no-preference: dark; light: dark; dark: dark;" data-icon="octicon-eye" aria-label="Watch ntkme/github-buttons on GitHub">Watch</a>
    <a class="github-button" href="https://github.com/ntkme/github-buttons" data-color-scheme="no-preference: dark; light: dark; dark: dark;" data-icon="octicon-star" aria-label="Star ntkme/github-buttons on GitHub">Star</a>
    <div style="
        background-color: #DC143C; 
        padding-top: 30px;
        padding-right: 30px;
        padding-bottom: 30px;
        padding-left: 80px;">
 
    <div> {} </div>
    <div> {} </div>
    </div>
    {}
    {}
    </body>
    </html>
    '''.format(htmltag(paragraph('...')),
           htmltag(paragraph('With twitter social network segmentation !'), p='h4'),
           graph_display.canvas(),
           graph_display.script())

    with open(os.path.join(Path(os.path.abspath("./")).parents[0], 'index.html'), 'w') as indexfile:
        indexfile.write(template)
        indexfile.close()


