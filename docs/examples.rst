========
Examples
========

Link to `GitHub repo <https://github.com/hardikvasa/google-images-download>`__

Link to `Documentation Homepage <https://google-images-download.readthedocs.io/en/latest/index.html>`__

Link to `Input arguments or parameters <https://google-images-download.readthedocs.io/en/latest/arguments.html>`__

Config File Format
==================

You can either pass the arguments directly from the command as in the examples below or you can pass it through a config file. Below is a sample of how a config
file looks.

You can pass more than one record through a config file. The below sample consist of two set of records. The code will iterate through each of the record and
download images based on arguments passed.

.. code:: json

    {
        "Records": [
            {
                "keywords": "apple",
                "limit": 5,
                "color": "green",
                "print_urls": true
            },
            {
                "keywords": "universe",
                "limit": 15,
                "size": "large",
                "print_urls": true
            }
        ]
    }


Code sample - Importing the library
===================================

- If you are calling this library from another python file, below is the sample code

.. code-block:: python

    from google_images_download import google_images_download   #importing the library

    response = google_images_download.googleimagesdownload()   #class instantiation

    arguments = {"keywords":"Polar bears,baloons,Beaches","limit":20,"print_urls":True}   #creating list of arguments
    paths = response.download(arguments)   #passing the arguments to the function
    print(paths)   #printing absolute paths of the downloaded images


Command line examples
=====================

- If you are passing arguments from a config file, simply pass the config_file argument with name of your JSON file

.. code-block:: bash

    $ googleimagesdownload -cf example.json

- Simple example of using keywords and limit arguments

.. code-block:: bash

    $ googleimagesdownload --keywords "Polar bears, baloons, Beaches" --limit 20

-  Using Suffix Keywords allows you to specify words after the main
   keywords. For example if the ``keyword = car`` and
   ``suffix keyword = 'red,blue'`` then it will first search for
   ``car red`` and then ``car blue``

.. code-block:: bash

    $ googleimagesdownload --k "car" -sk 'red,blue,white' -l 10

-  To use the short hand command

.. code-block:: bash

    $ googleimagesdownload -k "Polar bears, baloons, Beaches" -l 20

-  To download images with specific image extension/format

.. code-block:: bash

    $ googleimagesdownload --keywords "logo" --format svg

-  To use color filters for the images

.. code-block:: bash

    $ googleimagesdownload -k "playground" -l 20 -co red

-  To use non-English keywords for image search

.. code-block:: bash
    
    $ googleimagesdownload -k "北极熊" -l 5

-  To download images from the google images link

.. code-block:: bash
    
    $ googleimagesdownload -k "sample" -u <google images page URL>

-  To save images in specific main directory (instead of in 'downloads')

.. code-block:: bash
    
    $ googleimagesdownload -k "boat" -o "boat_new"

-  To download one single image with the image URL

.. code-block:: bash
    
    $ googleimagesdownload --keywords "baloons" --single_image <URL of the images>

-  To download images with size and type constrains

.. code-block:: bash
    
    $ googleimagesdownload --keywords "baloons" --size medium --type animated

-  To download images with specific usage rights

.. code-block:: bash
    
    $ googleimagesdownload --keywords "universe" --usage_rights labeled-for-reuse

-  To download images with specific color type

.. code-block:: bash
    
    $ googleimagesdownload --keywords "flowers" --color_type black-and-white

-  To download images with specific aspect ratio

.. code-block:: bash
    
    $ googleimagesdownload --keywords "universe" --aspect_ratio panoramic

-  To download images which are similar to the image in the image URL that you provided (Reverse Image search).

.. code-block:: bash
    
    $ googleimagesdownload -si <image url> -l 10

-  To download images from specific website or domain name for a given keyword

.. code-block:: bash
    
    $ googleimagesdownload --keywords "universe" --specific_site example.com

===> The images would be downloaded in their own sub-directories inside the main directory
(either the one you provided or in 'downloads') in the same folder you are in.


Library extensions
==================

The downloading algorithm does a good job of keeping out corrupt images. However it is not ideal. There are still some chances of getting one-off corrupt image that cannot be used for processing. Below script will help clean those corrupt image files. This script was ideated by @devajith in `Issue 81 <https://github.com/hardikvasa/google-images-download/issues/81>`__.

.. code:: python

    import os
    import logging
    from PIL import Image

    # Configure logging for audit trail
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger(__name__)

    img_dir = r"path/to/downloads/directory"
    
    # Valid image extensions to check
    VALID_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tga'}
    
    # Verify directory exists and is readable
    if not os.path.exists(img_dir):
        logger.error(f"Directory does not exist: {img_dir}")
        exit(1)
    
    if not os.access(img_dir, os.R_OK):
        logger.error(f"Directory is not readable: {img_dir}")
        exit(1)

    deleted_count = 0
    processed_count = 0
    
    for filename in os.listdir(img_dir):
        file_path = os.path.join(img_dir, filename)
        
        # Skip if not a file (e.g., subdirectories)
        if not os.path.isfile(file_path):
            continue
            
        processed_count += 1
        
        # Check if file has a valid image extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in VALID_IMAGE_EXTENSIONS:
            logger.info(f"Skipping non-image file: {filename}")
            continue
            
        try:
            # Attempt to open and verify the image
            with Image.open(file_path) as im:
                # Additional validation: try to load image data
                im.verify()
                logger.debug(f"Valid image: {filename}")
                
        except (IOError, OSError) as e:
            # Handle specific PIL exceptions for corrupt images
            logger.warning(f"Corrupt image detected: {filename} - {str(e)}")
            
            # Additional safety check: verify file size is reasonable
            try:
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    logger.info(f"Deleting zero-byte file: {filename}")
                    os.remove(file_path)
                    deleted_count += 1
                elif file_size < 100:  # Very small files are likely corrupt
                    logger.info(f"Deleting very small suspicious file: {filename} ({file_size} bytes)")
                    os.remove(file_path)
                    deleted_count += 1
                else:
                    # For larger files, log but don't auto-delete (could be format issue)
                    logger.warning(f"Large suspicious file not deleted (manual review needed): {filename} ({file_size} bytes)")
                    
            except OSError as removal_error:
                logger.error(f"Failed to delete {filename}: {str(removal_error)}")
                
        except Exception as unexpected_error:
            # Handle any other unexpected errors without deleting
            logger.error(f"Unexpected error processing {filename}: {str(unexpected_error)}")
    
    logger.info(f"Processing complete. Files processed: {processed_count}, Files deleted: {deleted_count}")
