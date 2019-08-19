Release process
------------
The $brat-widget project is released on an as-needed basis. The process depends of package manager that you're using, 
and this could be as follows:

- On PyPI:

Update brat_widget/_version.py (set release version, remove 'dev') and js/package.json

```
git add -A
git commit -m 'comment'
./dev-clean.sh
python setup.py sdist bdist_wheel
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
twine upload dist/*
git tag -a X.X.X -m 'comment'
Update _version.py (add 'dev' and increment minor)
git add -A
git commit
git push
git push --tags
```
- On NPM:

```
./dev-clean.sh
git clean -fdx
npm install
npm publish
```