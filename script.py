from datetime import datetime as date
from configparser import ConfigParser
from collections import Counter
from yattag import Doc
import praw

def is_link(post):
    return type(post) is praw.models.Submission


def create_reddit(config_file):
    config = ConfigParser()
    config.read(config_file)

    return praw.Reddit(
        client_id =     config['client']['id'],
        client_secret = config['client']['secret'],
        user_agent =    config['client']['user_agent'],
        username =      config['user']['name'],
        password =      config['user']['pw'])


def build_posts_html(posts):
    doc, tag, text, line = Doc().ttl()
    with tag('table'):
        for post in posts:
            with tag('tr', klass='post'):
                line('td', post.score, klass='score')

                with tag('td', klass='post-thumb'):
                    with tag('a', href=post.url, target='_blank'):
                        doc.stag('img', src=post.thumbnail)

                with tag('td', klass='post-content'):
                    with tag('a', href=post.url, target='_blank'):
                        line('h2', post.title)
                    line('a', 'Comments',
                        href='https://reddit.com'+post.permalink,
                        target='_blank')
                    text(date.utcfromtimestamp(
                        int(post.created_utc)).strftime(
                            '\tSubmitted on %b %d, %Y to '))
                    line('a', str(post.subreddit),
                        href='https://reddit.com/r/'+str(post.subreddit),
                        target='_blank')
    return doc.getvalue()


def build_html(posts):
    doc, tag, text, line = Doc().ttl()
    with tag('html'):
        with tag('head'):
            doc.stag('link', rel='stylesheet', href='styles.css')
            doc.stag('link', rel="stylesheet",
                href="https://fonts.googleapis.com/css?family=Roboto+Slab")
        with tag('body'):
            with tag('div', klass='container'):
                line('h1', 'Saved posts')
                doc.asis(build_posts_html(posts))
    return doc.getvalue()


def output_html(file_name, html):
    with open(file_name, 'w') as f:
        f.write(html)


def main():
    reddit = create_reddit('./config')
    comments, links = [], []

    print('\nFetching saved links. This might take a few moments...')
    for post in reddit.user.me().saved(limit=None):
        if is_link(post) and not post.over_18:
            links.append(post)

    print('Building html file...')
    output_html('output/index.html', build_html(links))

    print('Complete! Open output/index.html in your browser.')


if __name__ == "__main__":
    main()
