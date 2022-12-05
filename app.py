# -*- coding: utf-8 -*-
import os
import sys
import graphviz
from subprocess import check_output

# python ./app.py graph Вывод файлы graph.gv и graph.gv.dot

def git_log(log_format = None):
  return check_output(['git', 'log', '--all',
    '--pretty=format:{}'.format(log_format)], universal_newlines=True)

def cut_sha(sha):
  return sha[0:5]

def get_content(file_name):
  f = open(file_name, "r")
  content = f.read()
  f.close()
  return content.strip()

def get_refs(name):
  folder = os.path.join('.git', os.path.join('refs', name))
  refs = os.listdir(folder)
  dic = []
  for ref in refs:
    dic.append((ref,
      cut_sha(get_content(os.path.join(folder, ref)))))
  return dic

def create_graph(file_name):
  graph = graphviz.Digraph(file_name, format='dot')

  # Branches
  for branch, sha in get_refs("heads"):
    graph.node(branch, branch)
    graph.node(sha, sha)
    graph.edge(branch, sha)

  # Tags
  for tag, sha in get_refs("tags"):
    graph.node(tag, tag)
    graph.node(sha, sha)
    graph.edge(tag, sha)

  # HEAD
  graph.node('HEAD',"HEAD")
  head = get_content(os.path.join('.git', 'HEAD'))
  if head[:5] == 'ref: ':
    # 'ref: refs/heads/<current_branch>'
    graph.edge('HEAD', head[16:])
  else:
    graph.node('HEAD', cut_sha(head))


  # Commits
  for full_sha, title, parents in zip(
      git_log('%H').split(), #heximal, отвечает за номер коммита
      git_log('%s').split('\n'), #string, отвечает за название комиита
      git_log('%P').split('\n')): #коммиты-родители
    sha = cut_sha(full_sha)
    graph.node(sha,
    '{}\\n{}'.format(sha, title.replace('"', '\\"')))
    for parent in parents.split():
      graph.node(cut_sha(parent), cut_sha(parent))
      graph.edge(sha, cut_sha(parent))
  graph.render()

def main():
  args = sys.argv[1:]
  create_graph(args[0])

if __name__ == "__main__":
    main()