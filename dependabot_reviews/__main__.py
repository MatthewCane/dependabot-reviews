import asyncio

from dependabot_reviews import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted")
        exit(0)
