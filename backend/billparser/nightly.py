from billparser.downloader import download
from billparser.run_through import run_archives
from billparser.prune import run_prune


if __name__ == "__main__":
    download()
    run_archives()
    run_prune()
