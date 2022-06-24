import os
import sys
from dotenv import load_dotenv
from github import GitHubApi
from jinja2 import Template, Environment, FileSystemLoader
import json
from concurrent.futures import ProcessPoolExecutor

TEMPLATES_DIR_PATH = './templates/'
OUTPUT_DIR_PATH = './outputs/'
PR_REVIEW_COMMENT_TEMPLATE_FILE_NAME = 'pr_review_comment.j2'

environment = Environment(loader=FileSystemLoader(searchpath=TEMPLATES_DIR_PATH, encoding='utf8'))
template = environment.get_template(PR_REVIEW_COMMENT_TEMPLATE_FILE_NAME)

def language_decision(fileName):
    index = fileName.rfind(".")
    if index <= 0:
        return ""
    index = index + 1

    extention = fileName[index:]
    if extention == "go":
        return "go"
    elif extention == "sh":
        return "shell"
    elif extention == "c":
        return "c"
    elif extention == "cpp":
        return "cpp"
    elif extention == "cs":
        return "csharp"
    elif extention == "erl":
        return "erlang"
    elif extention == "groovy":
        return "groovy"
    elif extention == "java":
        return "java"
    elif extention == "js":
        return "javascript"
    elif extention == "pl":
        return "perl"
    elif extention == "php":
        return "php"
    elif extention == "py":
        return "python"
    elif extention == "rb":
        return "ruby"
    elif extention == "ts":
        return "typescript"
    elif extention == "vbs":
        return "vb"
    elif extention == "scala":
        return "scala"
    elif extention == "sql":
        return "sql"
    elif extention == "css":
        return "css"
    elif extention == "xml":
        return "xml"
    elif extention == "m":
        return "oc"
    elif extention == "swift":
        return "swift"
    elif extention == "kt":
        return "kotlin"
    elif extention == "yaml" or extention == "yml":
        return "yaml"
    else:
        return "" 


def make_markdown(owner, repository, api, pr):
    comments = api.get_pull_comment(owner, repository, str(pr['number']))
    # asc_comments = sortd(comments, key = lambda i: (i['pull_request_review_id'], i['id']))
    # print('pull request No.' + str(pr['number']) + ' comments count: ' + str(len(asc_comments)))

    json_comments = []
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
        json_comment['language'] = language_decision(comment['path'])
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
        md_file_path = repository + '/pr-' + str(pr['number']) + '.md'
        with open(OUTPUT_DIR_PATH + md_file_path , mode='w', encoding='CP932', errors='ignore') as f:
            f.write(md_file_data)

def main(env, repo):
    urls = repo.split('/')
    if 2 != len(urls):
        print('github repository format [{owner}/{repository}].')
        return 1
    
    owner = urls[0]
    repository = urls[1]

    if not os.path.isdir(OUTPUT_DIR_PATH + repository):
        os.mkdir(OUTPUT_DIR_PATH + repository)

    load_dotenv(env)

    options = {
        'token': os.environ.get("GITHUB_TOKEN")
    }
    api = GitHubApi(options)
    prs = api.get_pull_request(owner, repository)
    print('all pull request count:' + str(len(prs)))

    with ProcessPoolExecutor(max_workers=5) as executor:
        for pr in prs:
            executor.submit(make_markdown, owner, repository, api, pr)

        # print('title:' + pr['title'])
        # print('number:' + str(pr['number']))
        # print('creater:' + pr['user']['login'])
        # print('html_url:' + pr['html_url'])
        # print('review_comments_url:' + pr['review_comments_url'])
        # print('comments_url:' + pr['comments_url'])

    return 0

if __name__ == '__main__':
    argv = sys.argv
    if 3 <= len(argv):
        sys.exit(main(argv[1], argv[2]))
    else:
        print('Arguments are env file path and github repository({owner}/{repository}).')
