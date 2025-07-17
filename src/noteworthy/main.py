#!/usr/bin/env python3
# noteworthy/main.py

import argparse

from noteworthy.notes_formattor import format_release_notes
from noteworthy.notes_generator import generate_release_notes

def parse_args():
    parser = argparse.ArgumentParser(
        description="📝 NoteWorthy - AI-powered customizable release notes generator"
    )

    # Required
    parser.add_argument(
        "--repo-url",
        required=True,
        help="GitHub repository URL (e.g., https://github.com/owner/repo)"
    )

    # Optional
    parser.add_argument("--output-format", choices=["markdown", "html", "txt"], default="markdown", help="Output format (default: markdown)")
    parser.add_argument("--output-file", help="Output file path (default: stdout)")
    parser.add_argument("--exclude", help="Comma-separated list of exclude patterns (e.g., 'docs/*,chore:*')")
    parser.add_argument("--shoutout", dest="shoutout", action="store_true", help="Include contributor shoutouts (default: true)")
    parser.add_argument("--from-tag", help="Start tag for changelog")
    parser.add_argument("--to-tag", help="End tag for changelog (default: HEAD)")
    parser.add_argument("--style-sample", help="Path to a file containing a sample release note to guide the style")

    return parser.parse_args()

def main():
    args = parse_args()

    print("📝 Running NoteWorthy with the following options:")
    print(f"Repo URL:       {args.repo_url}")
    print(f"Format:         {args.output_format}")
    print(f"Output file:    {args.output_file or 'stdout'}")
    print(f"Exclude:        {args.exclude}")
    print(f"Shoutout:       {args.shoutout}")
    print(f"From tag:       {args.from_tag}")
    print(f"To tag:         {args.to_tag}")

    notes = generate_release_notes(
        repo_url=args.repo_url,
        output_format=args.output_format,
        output_file=args.output_file,
        exclude_patterns=args.exclude.split(",") if args.exclude else None,
        from_tag=args.from_tag,
        to_tag=args.to_tag,
        shoutout=args.shoutout,
        style_sample=args.style_sample
    )

    notes = format_release_notes(notes, args.output_format)
    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(notes)
        print(f"✅ Release notes saved to {args.output_file}")
    else:
        print(notes)

if __name__ == "__main__":
    main()
