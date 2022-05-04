#!/usr/bin/python3

from github import Github, GithubException
from urllib.parse import urlparse
import json
import yaml
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True,
                    help="list of github repos in yaml")
parser.add_argument("-o", "--output", required=True,
                    help="output github repos in json")
parser.add_argument("-t", "--token",
                    help="GitHub token for API access")

args = parser.parse_args()

yamlfile = args.input
jsonfile = args.output
r_list = []

if args.token:
    g = Github(args.token)
else:
    g = Github()

with open(yamlfile, 'r') as f:
    repo_list = yaml.load(f, Loader=yaml.SafeLoader)

for l in repo_list["list"]:
    for repo in l.values():
        print(urlparse(repo).path.lstrip("/"))
        try:
            r = g.get_repo(urlparse(repo).path.lstrip("/"))
            repo_dict = {"name": r.name,
                         "html_url": repo,
                         "forks_count": r.forks_count,
                         "stargazers_count": r.stargazers_count,
                         "description": r.description,
                         "homepage": r.homepage}

            # Ensure there are None doesn't exist as a value
            for k, v in repo_dict.items():
                if v is None:
                    repo_dict[k] = ""

            # Append the repo information into a list of dictionaries
            r_list.append(repo_dict)
        except GithubException as e:
            if e.status != 404:
                raise
            else:
                print("WARNING: '%s' does not exist! Please review 'repos.json'"
                      "and remove the listing if necessary." % (r.full_name))

# sort by name key
r_list = sorted(r_list, key=lambda i: i['name'])

with open(jsonfile, 'w', encoding='utf-8') as f:
    json.dump({"list": r_list}, f, indent=2)
