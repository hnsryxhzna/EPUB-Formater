import argparse
import sys
from .formator import EpubFormator

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="epub-formater",
        description="A CLI tool for editing EPUB metadata",
    )
    parser.add_argument("epub", help="Path to the EPUB file")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-info", action="store_true", help="Show metadata")
    group.add_argument("-set-language", dest="language", help="BCP-47 language code")
    group.add_argument("-set-cover", dest="cover", help="Path to new cover image")
    group.add_argument("-download-cover", dest="download_cover", action="store_true", help="Download the cover")
    group.add_argument("-cover-info", dest="cover_info", action="store_true", help="Get the cover info")
    group.add_argument("-resize-cover", dest="resize_cover", choices=["stretch", "crop"],
                       help="Resize cover: 'stretch' or 'crop'")
    parser.add_argument("-ratio", type=float, default=1.5,
                    help="Target height/width ratio (default: 1.5)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        fmt = EpubFormator(args.epub)
        if args.info:
            fmt.get_epub_info()
        elif args.language:
            fmt.set_language(args.language)
        elif args.cover:
            fmt.set_cover(args.cover)
        elif args.download_cover:
            fmt.download_cover()
            # print(f"Cover downloaded '{args.download_cover}'")
        elif args.cover_info:
            fmt.cover_info()
        elif args.resize_cover:
            fmt.resize_cover(args.resize_cover, args.ratio)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
