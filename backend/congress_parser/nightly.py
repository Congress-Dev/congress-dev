from congress_parser.downloader import download
from congress_parser.run_through import run_archives
from congress_parser.prune import run_prune

# TODO: Put this back onto a cron job
if __name__ == "__main__":
    download()
    run_archives()
    run_prune()
