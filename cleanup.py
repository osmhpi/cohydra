#!/usr/bin/env python3

import argparse
from pyroute2 import IPRoute
import docker
from pprint import PrettyPrinter

pprint = PrettyPrinter().pprint


def main(dry_run, images, all_images):
    ipr = IPRoute()
    links = ipr.get_links()
    for link in links:
        name = link.IFLA_IFNAME.value
        if '-ns3-' in name:
            print(f'remove interface {name}')
            if not dry_run:
                ipr.link('delete', ifname=name)

    client = docker.from_env()
    containers = client.containers.list(all=True, filters={'label': 'created-by=ns-3'})
    for container in containers:
        print(f'remove container {container.name}')
        if not dry_run:
            container.remove(force=True)

    if images or all_images:
        for image in client.images.list():
            remove = False
            for tag in image.tags:
                if tag.startswith('ns3-'):
                    remove = True
                elif not all_images:
                    remove = False
                    break

            if remove:
                tags = ', '.join(image.tags)
                print(f'remove image {tags}')
                if not dry_run:
                    client.images.remove(image=image.id)

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()

    PARSER.add_argument('-d', '--dry-run', action='store_true', help="Do not execute any commands")
    PARSER.add_argument('-i', '--images', action='store_true', help="Remove all images build by ns3d")
    PARSER.add_argument('-a', '--all-images', action='store_true', help="Remove all images used by ns3d")

    main(**vars(PARSER.parse_args()))
