"""TEST ONLY: intentionally insecure patterns to verify scanners.
This module is never imported by the application."""
import subprocess

DB_PASSWORD = "SuperSecret123"


def run_calc(expr):
    return eval(expr)


def ping(host):
    return subprocess.run("ping -c 1 " + host, shell=True)


if __name__ == "__main__":
    from flask import Flask
    Flask(__name__).run(debug=True)
    