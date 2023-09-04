#!/usr/bin/env python

import sys
import argparse
import urllib.parse as urlparse


try:
    from django.conf import settings
    from django.test.utils import get_runner

    def get_settings():
        settings.configure(
            DEBUG=True,
            USE_TZ=True,
            DATABASES={
                "default": {
                    "NAME": ":memory:",
                    "ENGINE": "django.db.backends.sqlite3",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sites",
                "django_typesense",
                "tests",
            ],
            SITE_ID=1,
            MIDDLEWARE_CLASSES=(),
            TYPESENSE_ADMIN_API_KEY="M7aJZtlCecB5GF7y6iUxlvTY7zvC2usIlkZDKOX6Kw0",
            TYPESENSE_NODES=[
                {"host": "localhost", "port": 8108, "protocol": "http"},
            ],
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )

        try:
            import django

            setup = django.setup
        except AttributeError:
            pass
        else:
            setup()

        return settings

except ImportError:
    import traceback

    traceback.print_exc()
    msg = """To fix this error, run: pip install -r requirements.txt"""
    raise ImportError(msg)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--typesense",
        nargs="?",
        default="http://localhost:8108",
        help="To run integration test against a Typesense server (default: http://localhost:8108)",
    )
    return parser


def run_tests(*test_args):
    args, test_args = make_parser().parse_known_args(test_args)

    if not test_args:
        test_args = ["tests"]

    settings = get_settings()

    if args.typesense:
        parsed_url = urlparse.urlparse(args.typesense)
        settings.TYPESENSE_NODES = [
            {
                "port": parsed_url.port,
                "host": parsed_url.hostname,
                "protocol": parsed_url.scheme,
            }
        ]

    test_runner = get_runner(settings)()

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(bool(failures))


if __name__ == "__main__":
    run_tests(*sys.argv[1:])
