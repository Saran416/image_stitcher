import argparse
import os
import glob
from app import ImageStitcher

def main():
    parser = argparse.ArgumentParser(description="Image Stitcher CLI")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--images", nargs="+", help="Paths to input images")
    group.add_argument("-f", "--folder", help="Path to folder containing images")

    parser.add_argument("-o", "--output", required=True, help="Path to output stitched image")

    parser.add_argument(
        "-m", "--min_matches", type=int, default=100,
        help="Minimum number of matches required to stitch images (default: 100)"
    )

    args = parser.parse_args()

    # Collect image paths
    if args.folder:
        supported_extensions = ('*.jpg', '*.jpeg', '*.png', '*.tiff')
        image_paths = []
        for ext in supported_extensions:
            image_paths.extend(glob.glob(os.path.join(args.folder, ext)))
        image_paths.sort()
        if not image_paths:
            print("No supported images found in the specified folder.")
            return
    else:
        image_paths = args.images

    # stitch the images
    try:
        min_matches = args.min_matches
        stitcher = ImageStitcher(min_matches)
        stitcher.load_images(image_paths)
        success = stitcher.stitch_images(output_path=args.output)

        if success:
            print(f"Stitching completed successfully. Output saved to {args.output}")
        else:
            print("Stitching failed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
