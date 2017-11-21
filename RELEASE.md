Release process
------------
The $brat-widget project is released on an as-needed basis. The process depends of package manager that you're using, 
and this could be as follows:

- On PyPI:

Update _version.py (set release version, remove 'dev')

```
git add and git commit
python setup.py sdist upload
python setup.py bdist_wheel upload
git tag -a X.X.X -m 'comment'
Update _version.py (add 'dev' and increment minor)
git add and git commit
git push
git push --tags
```
- On NPM:

```
nuke the  `dist` and `node_modules`
git clean -fdx
npm install
npm publish
```