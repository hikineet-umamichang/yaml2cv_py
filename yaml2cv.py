# -*- coding: utf-8 -*-
import yaml
import argparse
import os
import sys
import make_resume


def main():
    parser = argparse.ArgumentParser(
        description="Output resume in pdf format from yaml"
    )
    parser.add_argument(
        "-i",
        "--input",
        default="data.yaml",
        help="Input data file (default: data.yaml)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output.pdf",
        help="Output file     (default: output.pdf)",
    )
    parser.add_argument(
        "-f",
        "--font",
        default="fonts/ipaexg.ttf",
        help="Font file       (default: fonts/ipaexg.ttf)",
    )
    parser.add_argument(
        "-p",
        "--picture",
        default="sample.png",
        help="Output file     (default: sample.png)",
    )
    args = parser.parse_args()


    yaml_path = args.input
    if not os.path.exists(yaml_path):
        print("Error: YAML does not exist.", file=sys.stderr)
        sys.exit(1)
    with open(yaml_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    output_file = args.output
    font_path = args.font
    photo_path = args.picture

    make_resume.make_resume(output_file, data, font_path, photo_path)


if __name__ == "__main__":
    main()
