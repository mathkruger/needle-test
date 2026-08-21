import argparse

import needle
from agent import init_agent
from chat import init_chat


def parse_args():
    parser = argparse.ArgumentParser(description="needle-test local agent")
    parser.add_argument("--web", action="store_true",
                        help="start the web UI + API server instead of the terminal chat")
    parser.add_argument("--host", default="127.0.0.1",
                        help="web server bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000,
                        help="web server port (default: 8000)")
    return parser.parse_args()


def main():
    args = parse_args()
    agent = init_agent()
    if args.web:
        from server import serve
        serve(agent, host=args.host, port=args.port)
    else:
        init_chat(agent)


if __name__ == "__main__":
    main()
