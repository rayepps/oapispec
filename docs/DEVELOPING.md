# Developers Guide
If your going to be doing any work on oapispec you'll want to read through this. This guide will show you how to setup the project locally, run the tests, and run the linter.

## Project Setup
- First you'll need to clone the repo
- In the root of the project run `make venv version=3.6|3.7|3.8` to create a virtual environment. Typically I develop and test using `3.8`, checking that all other versions pass checks before pushing work.
- Activate your new virtual environment `source venv/bin/activate`
- Install the project dependencies by running `pip install -r requirements.dev.txt`. This will install all requirements from both the root and test requirements as well.
- You're ready to go!

## Run the tests
This one is pretty simple. Run `make test`

## Run the linter
Again, easy. Run `make lint`
