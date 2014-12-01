org-mode-diff
================

This tool can be used to view differences in org-mode files.

It applies an alignment algorithm that's tweaked for org-mode documents.

Its output isn't strictly a diff at all (if you want to get that, you should just use `diff`!) It looks okay in `diff-mode` in emacs.


This is how I use it! I keep my .org files in a local git repository. Before commiting a day of work, I do something like this to produce diffs.
```
for file in `git diff --name-only *.org`;
do
    git show master:$file > /tmp/old-$file;
    org-mode-diff --old /tmp/old-$file --new $file > /tmp/$file.diff;
    echo "/tmp/$file.diff";
done
```