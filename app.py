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

  # ветки
  for branch, sha in get_refs("heads"):
    graph.edge(branch, sha)

  # теги
  for tag, sha in get_refs("tags"):
    graph.edge(tag, sha)

  # голова
  head = get_content(os.path.join('.git', 'HEAD'))
  if head[:5] == 'ref: ':
    # 'ref: refs/heads/<current_branch>'
    graph.edge('HEAD', head[16:])
  else:
    graph.edge('HEAD', cut_sha(head))


  # коммиты
  for full_sha, title, parents in zip(
      git_log('%H').split(), #hex, отвечает за номер коммита
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
  for branch, sha in get_refs("heads"):
    print(branch)
    print(sha)
  create_graph(args[0])

if __name__ == "__main__":
    main()