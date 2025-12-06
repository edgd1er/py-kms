# Contributing

You want to improve this project? 
Awesome! But before you write or modify the existing source code, please note the following guideline:

- Always base your branch on the latest `next` branch to avoid merge conflicts.
- 8-space indentation without tabs.
- Docstrings as this:
```python
    """ This is single line docstring. """
    """ This is a
    """ multiline comment.
```
- Wrap lines only if really long (it does not matter 79 chars return)
- For the rest a bit as it comes with a look at [PEP8](https://www.python.org/dev/peps/pep-0008/) :)

Test your changes, please. For example, run the server via:
```bash
python3 pykms_Server.py -F STDOUT -s ./pykms_database.db
```
Then trigger (multiple) client requests and check the output for errors via:
```bash
python3 pykms_Client.py -F STDOUT -c 174f5409-0624-4ce3-b209-adde1091956b
```
