
import argparse
import asyncio
import logging
import shutil
from urio import Path


logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_arguments():
    parser = argparse.ArgumentParser(description="File sorter")
    parser.add_argument("-s", "--source", type=str, required=True, help="Source folder")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output folder")
    return parser.parse_args()


async def validate_folders(source_folder, output_folder):
    if not await source_folder.exists():
        logging.error("Source folder does not exist: %s", source_folder)
        return False
    if not await source_folder.is_dir():
        logging.error("Source path is not a directory: %s", source_folder)
        return False
    if await output_folder.exists() and not await output_folder.is_dir():
        logging.error("Output path is not a directory: %s", output_folder)
        return False
    return True


async def copy_file(file_path, output_folder):
    try:
        extension = file_path.suffix.lower().lstrip(".")
        if not extension:
            extension = "no_extension"
        destination_folder = output_folder / extension
        destination_file = destination_folder / file_path.name
        await asyncio.to_thread( shutil.copy2, file_path, destination_file)
    except OSError:
        logging.exception("Error copying file: %s", file_path)


async def read_folder(source_folder, output_folder):
    try:
        files = []
        extensions = set()
        # Recursively collect all files and their extensions
        async for file_path in source_folder.rglob("*"):
            if await file_path.is_file():
                files.append(file_path)
                extension = file_path.suffix.lower().lstrip(".")
                extensions.add(extension or "no_extension")
        # Create destination directories before parallel copying
        for extension in extensions:
            destination_folder = output_folder / extension
            await destination_folder.mkdir(parents=True, exist_ok=True)
        # Create and run copying tasks
        tasks = [copy_file(file_path, output_folder) for file_path in files]
        await asyncio.gather(*tasks)
    except OSError:
        logging.exception("Error reading source folder: %s", source_folder)


async def main():
    args = parse_arguments()
    source_folder = Path(args.source)
    output_folder = Path(args.output)
    if not await validate_folders(source_folder, output_folder):
        return
    try:
        await output_folder.mkdir(parents=True, exist_ok=True)
        await read_folder(source_folder, output_folder)
    except OSError:
        logging.exception("Error processing folders")


if __name__ == "__main__":
    asyncio.run(main())
