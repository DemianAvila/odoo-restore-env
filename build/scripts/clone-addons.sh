#!/bin/bash

file="/src/modules-list.env"

while IFS= read -r line
do
  IFS=',' read -r repo branch <<< "$line"
  echo ${repo}
  echo ${branch}
  git clone ${repo} --depth 1 --branch ${branch}
done < "$file"