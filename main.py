import os
import sys
from dotenv import load_dotenv
from github import GitHubApi
from jinja2 import Template, Environment, FileSystemLoader
import json

TEMPLATES_DIR_PATH = './templates/'
OUTPUT_DIR_PATH = './outputs/'
PR_REVIEW_COMMENT_TEMPLATE_FILE_NAME = 'pr_review_comment.j2'

environment = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_DIR_PATH, encoding='utf8'))
template = environment.get_template(PR_REVIEW_COMMENT_TEMPLATE_FILE_NAME)

def main(env, repo):
    urls = repo.split('/')
    if 2 != len(urls):
        print('github repository format [{owner}/{repository}].')
        return 1
    
    owner = urls[0]
    repo = urls[1]

    if not os.path.isdir(OUTPUT_DIR_PATH + repo):
        os.mkdir(OUTPUT_DIR_PATH + repo)

    load_dotenv(env)

    options = {
        'token': os.environ.get("GITHUB_TOKEN")
    }
    api = GitHubApi(options)
    prs = api.get_pull_request(owner, repo)
    for pr in prs:
        # print('title:' + pr['title'])
        # print('number:' + str(pr['number']))
        # print('creater:' + pr['user']['login'])
        # print('html_url:' + pr['html_url'])
        # print('review_comments_url:' + pr['review_comments_url'])
        # print('comments_url:' + pr['comments_url'])

        json_comments = []
        comments = api.get_pull_comment(owner, repo, str(pr['number']))
        for comment in comments:
            json_comment = {}
            # print('diff_hunk:' + comment['diff_hunk'])
            # print('path:' + comment['path'])
            # print('commenter:' + comment['user']['login'])
            # print('body:' + comment['body'])
            json_comment['comment_url'] = comment['html_url']
            json_comment['reviewer'] = comment['user']['login']
            json_comment['file_path'] = comment['path']
            json_comment['diff'] = comment['diff_hunk']
            json_comment['comment'] = comment['body']
            json_comments.append(json_comment)
        # print('------------------------------')

        if any(json_comments):
            json_data = {}
            json_data['title'] = pr['title']
            json_data['url'] = pr['html_url']
            json_data['create_user'] = pr['user']['login']
            json_data['comments'] = json_comments

            md_file_data = template.render(json_data)
            md_file_path = repo + '/pr-' + str(pr['number']) + '.md'
            with open(OUTPUT_DIR_PATH + md_file_path , mode='w', encoding='CP932', errors='ignore') as f:
                f.write(md_file_data)

    return 0

if __name__ == '__main__':
    argv = sys.argv
    if 3 <= len(argv):
        sys.exit(main(argv[1], argv[2]))
    else:
        print('Arguments are env file path and github repository({owner}/{repository}).')
