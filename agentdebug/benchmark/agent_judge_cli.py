"""Compatibility module for the single public command parser."""


def main(argv=None):
    from agentdebug.cli import main as public_main
    return public_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
