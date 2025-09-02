import asyncio

from dependabot_reviews import main


def cli():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted")
        exit(0)


if __name__ == "__main__":
    cli()
