# spoils (bandit extensions)

A lightweight collection of additional security checks for [Bandit](https://github.com/PyCQA/bandit).

## Add-ons

* **B...: No `os.path.join` misuse**
  Detects unvalidated or unsafe usage of `os.path.join` calls in your codebase.

## Installation

```bash
pip install spoils
```

## Usage

Once installed, Bandit will automatically pick up the new checks:

```bash
bandit -r your_project/
```

Issues will be reported with their B-number and descriptive message.

## Future Add-ons

More community-driven checks are coming soon! Got an idea or contribution? Feel free to file an issue or submit a pull request.
