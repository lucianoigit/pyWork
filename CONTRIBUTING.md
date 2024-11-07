# Contributing to pyWork

Thank you for your interest in contributing to pyWork! Every contribution is valuable and helps improve this project. Below is a quick guide on how to effectively collaborate.

## How You Can Contribute

### Report Issues
If you find a bug or have an idea for improving pyWork, please open an *issue*. Make sure to provide clear details, including steps to reproduce the problem if possible.

### Improve Documentation
Documentation is essential for making the project accessible to others. If you find anything unclear or would like to add more examples, your contributions are highly appreciated.

### Propose and Develop New Features
Do you have an idea for a new feature? First, open an *issue* to discuss it, and if accepted, follow the steps below to implement it.

## Setting Up the Development Environment

To contribute, you’ll need to set up a local development environment.

### 1. Clone the Repository

Clone the pyWork repository to your local machine:

```bash
git clone https://github.com/lucianoigit/pywork.git
cd pywork
```

### 2. Create a Virtual Environment
It’s recommended to create a virtual environment to isolate project dependencies.

For Linux or macOS:

```bash
python3 -m venv env
source env/bin/activate

```

For Windows:

```bash
python -m venv env
env\Scripts\activate

```

### 3. Install Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt

```

### 4. Make Your Changes

Make your changes in a new branch. Use a descriptive name for your branch, such as fix-login-bug or add-user-authentication.

```bash
git checkout -b your-branch-name

```

### 5. Test Your Changes

Before submitting, ensure all tests pass and your code adheres to pyWork’s style conventions. Run the tests and generate an HTML coverage report with:

```bash
bash scripts/test-cov-html.sh

```
After running this command, open the file ./htmlcov/index.html in your browser to view an interactive test coverage report.


### 6. Submit a Pull Request

When you're ready to submit your changes, push your branch and open a Pull Request on GitHub. Clearly describe the changes you’ve made, along with any issues it addresses or new features it adds.

```bash
git add .
git commit -m "Description of changes"
git push origin your-branch-name

```


This file provides all essential steps for contributing, with clear, concise language. Let me know if you need further customization!


