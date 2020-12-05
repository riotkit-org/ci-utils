
import re
from argparse import ArgumentParser
from abc import ABC
from typing import Callable
from subprocess import CalledProcessError
from rkd.api.contract import TaskInterface, ExecutionContext
from rkd.api.syntax import TaskDeclaration


class DockerBaseTask(TaskInterface, ABC):
    def calculate_images(self, image: str, latest_per_version: bool, global_latest: bool, allowed_meta_list: str,
                         keep_prefix: bool):
        """ Calculate tags propagation """

        allowed_meta = allowed_meta_list.replace(' ', '').split(',')
        tag = image.split(':')[-1]

        # output
        output_tags = [image]

        pattern = re.compile('(?P<version>[0-9.]+)(-(?P<meta>[A-Za-z]+))?(?P<metanum>[0-9]+)?', re.IGNORECASE)
        matches = [m.groupdict() for m in pattern.finditer(tag)]

        if not matches:
            self._io.warn('No release version found')
            return output_tags

        meta_type = matches[0]['meta']
        meta_number = matches[0]['metanum']

        if meta_type and meta_type not in allowed_meta:
            self.io().warn('Version meta part is not allowed, not calculating propagation')
            return output_tags

        original_tag = tag
        base_version = matches[0]['version']
        optional_prefix = tag[0:tag.find(matches[0]['version'])]
        base_version_with_optional_prefix = optional_prefix + base_version
        meta = '-' + meta_type if meta_type else None
        to_strip_at_beginning = optional_prefix if not keep_prefix else ''

        # :latest
        if global_latest:
            output_tags.append(image.replace(original_tag, 'latest'))

        # case 1: 1.0.0-RC1 -> 1.0.0-latest-RC
        if meta and meta_number:
            output_tags = self.generate_tags_for_numbered_pre_release(
                output_tags=output_tags,
                base_version_with_optional_prefix=base_version_with_optional_prefix,
                original_tag=original_tag,
                image=image,
                latest_per_version=latest_per_version,
                meta=meta,
                meta_number=meta_number
            )

        # case 2: 1.0.0-RC (without meta number)
        elif meta and not meta_number:
            output_tags = self.generate_tags_for_pre_release_without_number(
                output_tags=output_tags,
                base_version_with_optional_prefix=base_version_with_optional_prefix,
                original_tag=original_tag,
                image=image,
                latest_per_version=latest_per_version,
                meta=meta
            )

        # release
        elif not meta:
            output_tags = self.generate_tags_for_release(
                output_tags=output_tags,
                base_version_with_optional_prefix=base_version_with_optional_prefix,
                original_tag=original_tag,
                image=image
            )

        return self.strip_out_each_tag(output_tags, to_strip_at_beginning, image)

    @staticmethod
    def strip_out_each_tag(input_tagged_images: list, to_strip_at_beginning: str, originally_tagged_image: str):
        """
        Removes a prefix like a "release-", "v" from beginning of each tagged image

        :param input_tagged_images:
        :param to_strip_at_beginning:
        :param originally_tagged_image:
        :return:
        """

        if not to_strip_at_beginning:
            return input_tagged_images

        output_tagged_images = []
        image = originally_tagged_image[0:originally_tagged_image.find(':')]  # separate image from tag

        for tagged_image in input_tagged_images:
            tag = tagged_image[len(image) + 1:]

            # strip out the prefix eg. "release-", "v" or other
            if tag.startswith(to_strip_at_beginning):
                tag = tag[len(to_strip_at_beginning):]

            output_tagged_images.append(image + ':' + tag)

        return output_tagged_images

    @staticmethod
    def generate_originally_tagged_image(original_tag: str, to_strip_at_beginning: str, image: str):
        if to_strip_at_beginning:
            return image.replace(original_tag, original_tag[len(to_strip_at_beginning):], 1)

        return image

    def generate_tags_for_numbered_pre_release(self, output_tags: list, base_version_with_optional_prefix: str,
                                               original_tag: str, image: str, meta: str,
                                               latest_per_version: bool, meta_number: str):
        """
        EXAMPLE CASES:
            - v2.0.0-BETA1
            - 2.0.0-BETA1
            - release-2.0.0-BETA1
        """

        output_tags.append(image.replace(original_tag, base_version_with_optional_prefix + '-latest%s' % meta, 1))

        if latest_per_version:
            output_tags = self._generate_for_each_version(
                image, original_tag, output_tags,
                lambda version: original_tag.replace(base_version_with_optional_prefix + meta + meta_number,
                                                     version + '-latest%s' % meta, 1)
            )

        return output_tags

    def generate_tags_for_pre_release_without_number(self, output_tags: list, base_version_with_optional_prefix: str,
                                                     original_tag: str, image: str, meta: str,
                                                     latest_per_version: bool):
        """
        EXAMPLE CASES:
            - v2.0.0-PRE
            - 2.0.0-PRE
            - release-2.0.0-PRE
        """

        output_tags.append(image.replace(original_tag, base_version_with_optional_prefix + '-latest%s' % meta, 1))

        if latest_per_version:
            output_tags = self._generate_for_each_version(
                image, original_tag, output_tags,
                lambda version: original_tag.replace(base_version_with_optional_prefix + meta,
                                                     version + '-latest%s' % meta, 1)
            )

        return output_tags

    def generate_tags_for_release(self, output_tags: list, base_version_with_optional_prefix: str,
                                  original_tag: str, image: str):
        """
        EXAMPLE CASES:
            - v2.0.0
            - 2.0.0
            - release-1.2.3
        """

        output_tags = self._generate_for_each_version(
            image, original_tag, output_tags,
            lambda version: original_tag.replace(base_version_with_optional_prefix, version, 1)
        )

        return output_tags

    @staticmethod
    def _generate_for_each_version(image: str, original_tag: str, output_tags: list, callback: Callable) -> list:
        """
        Generate a list of tags for each sub-version eg. 2.1.3 -> 2.1 -> 2

        :param image: Original image eg. quay.io/riotkit/infracheck
        :param original_tag: Original image tag eg. v2.0.0
        :param output_tags: List of existing output tags to append generated tags to
        :param callback: A callback that replaces version in original_tag part
        :param to_strip_at_beginning: Strip a string at the beginning eg. "release-" or "v" or "v."
        :return:
        """

        parts = original_tag.split('.')

        for part_num in range(0, len(parts)):
            version = ".".join(parts[0:part_num])

            if not version:
                continue

            output_tags.append(
                image.replace(
                    original_tag,
                    callback(version)
                )
            )

        return output_tags

    def _print_images(self, images: list, action: str):
        for image in images:
            self._io.info(' -> Going to %s image "%s"' % (action, image))

    def get_group_name(self) -> str:
        return ':docker'

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('--image', '-i', help='Image name', required=True)
        parser.add_argument('--without-latest', '-wl', help='Do not tag latest per version', action='store_true')
        parser.add_argument('--without-global-latest', '-wgl', help='Do not tag :latest', action='store_true')
        parser.add_argument('--propagate', '-p', help='Propagate tags? eg. 1.0.0 -> 1.0 -> 1 -> latest',
                            action='store_true')
        parser.add_argument('--allowed-meta', '-m', help='Allowed meta part eg. rc, alpha, beta',
                            default='rc,alpha,stable,dev,prod,test,beta,build,b,pre,a,preprod,prerelease,early,ea,stage')
        parser.add_argument('--keep-prefix', '-k', help='Keep prefix eg. "release-", "v" or "v." if present in tag')


class TagImageTask(DockerBaseTask):
    """Re-tag images to propagate version tags in docker-like format eg. 1.0.1 -> 1.0 -> 1 -> latest

    Examples:
        1.0.0 -> 1.0 -> 1 -> latest
        1.0.0-RC1 -> 1.0.0-latest-rc
    """

    def get_name(self) -> str:
        return ':tag'

    def execute(self, context: ExecutionContext) -> bool:
        original_image = context.args['image']

        if context.args['propagate']:
            images = self.calculate_images(
                image=original_image,
                latest_per_version=not context.args['without_latest'],
                global_latest=not context.args['without_global_latest'],
                allowed_meta_list=context.args['allowed_meta'],
                keep_prefix=bool(context.args['keep_prefix'])
            )
        else:
            images = [original_image]

        self._print_images(images, 'tag')

        for image in images:
            try:
                self.exec('docker tag %s %s' % (original_image, image))
            except CalledProcessError as e:
                print(e)
                return False

        return True


class PushTask(DockerBaseTask):
    """Pushes all re-tagged images
    """

    def get_name(self) -> str:
        return ':push'

    def execute(self, context: ExecutionContext) -> bool:
        original_image = context.args['image']
        images = []

        if context.args['propagate']:
            images += self.calculate_images(
                image=original_image,
                latest_per_version=not context.args['without_latest'],
                global_latest=not context.args['without_global_latest'],
                allowed_meta_list=context.args['allowed_meta'],
                keep_prefix=bool(context.args['keep_prefix'])
            )
        else:
            images = [original_image]

        self._print_images(images, 'push')

        for image in images:
            try:
                self.exec('docker push %s' % image)
            except CalledProcessError as e:
                print(e)
                return False

        return True


def imports():
    return [
        TaskDeclaration(TagImageTask()),
        TaskDeclaration(PushTask())
    ]
