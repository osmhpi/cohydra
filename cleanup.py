#!/usr/bin/env python3

from hostcomponents import argparse
from pyroute2 import IPRoute
import docker

def main(logger, dry_run, images, all_images):
    ipr = IPRoute()
    links = ipr.get_links()
    for link in links:
        name = link.IFLA_IFNAME.value
        if '-ns3-' in name or 'br-net' in name or 'br-veth-' in name or 'tun-net' in name:
            logger.info('remove interface %s', name)
            if not dry_run:
                ipr.link('delete', ifname=name)

    client = docker.from_env()
    containers = client.containers.list(all=True, filters={'label': 'created-by=ns-3'})
    for container in containers:
        logger.info('remove container %s', container.name)
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
                logger.info('remove image %s', ', '.join(image.tags))
                if not dry_run:
                    client.images.remove(image=image.id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(logger=True)

    parser.add_argument('-d', '--dry-run', action='store_true', help='do not execute any commands (but show information)')
    parser.add_argument('-i', '--images', action='store_true', help='remove all docker images build by dasylab-testbed')
    parser.add_argument('-a', '--all-images', action='store_true', help='remove all docker images used by dasylab-testbed')

    parser.run(main)
