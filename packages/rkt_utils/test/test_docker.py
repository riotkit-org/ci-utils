
from rkt_utils.docker import TagImageTask
from rkd.api.testing import FunctionalTestingCase


class DockerTestCase(FunctionalTestingCase):
    def test_tag_calculation_for_release_candidate(self):
        images = TagImageTask().calculate_images(
            image='quay.io/riotkit/infracheck:v2.0.0-rc1',
            latest_per_version=False,
            global_latest=False,
            allowed_meta_list='rc,alpha,stable,dev,prod,test,beta,build,b',
            keep_prefix=True
        )

        self.assertEqual(['quay.io/riotkit/infracheck:v2.0.0-rc1',
                          'quay.io/riotkit/infracheck:v2.0.0-latest-rc'], images)

    def test_tag_calculation_for_release(self):
        # CASE 1
        with self.subTest('With prefix - "v" at the beginning'):
            images = TagImageTask().calculate_images(
                image='quay.io/riotkit/infracheck:v2.3.4',
                latest_per_version=False,
                global_latest=False,
                allowed_meta_list='rc,alpha,stable,dev,prod,test,beta,build,b',
                keep_prefix=True
            )

            self.assertEqual(
                ['quay.io/riotkit/infracheck:v2.3.4',
                 'quay.io/riotkit/infracheck:v2',
                 'quay.io/riotkit/infracheck:v2.3'],
                images
            )

        # CASE 2
        with self.subTest('Without prefix - "v" is removed from beginning'):
            images = TagImageTask().calculate_images(
                image='quay.io/riotkit/infracheck:v2.3.4',
                latest_per_version=False,
                global_latest=False,
                allowed_meta_list='rc,alpha,stable,dev,prod,test,beta,build,b',
                keep_prefix=False
            )

            self.assertEqual(
                ['quay.io/riotkit/infracheck:2.3.4',
                 'quay.io/riotkit/infracheck:2',
                 'quay.io/riotkit/infracheck:2.3'],
                images
            )

    def test_gradle_style_prefix_is_cut_off(self):
        """
        Gradle and Axion plugin requires to tag in GIT in a specific convention with is "release-x.y.z"
        this test checks that "release-" can be cut off, so we will have only the version number + version meta
        """

        images = TagImageTask().calculate_images(
            image='quay.io/riotkit/backuprepository:release-4.0.5',
            latest_per_version=False,
            global_latest=False,
            allowed_meta_list='rc,alpha,stable,dev,prod,test,beta,build,b',
            keep_prefix=False
        )

        self.assertEqual(
            ['quay.io/riotkit/backuprepository:4.0.5',
             'quay.io/riotkit/backuprepository:4',
             'quay.io/riotkit/backuprepository:4.0'],
            images
        )

    def test_latest_tags(self):
        with self.subTest('global_latest'):
            images = TagImageTask().calculate_images(
                image='quay.io/riotkit/backuprepository:release-4.0.5',
                latest_per_version=False,
                global_latest=True,
                allowed_meta_list='rc,alpha,stable,dev,prod,test,beta,build,b',
                keep_prefix=False
            )

            self.assertIn('quay.io/riotkit/backuprepository:latest', images)

        with self.subTest('latest_per_version=True'):
            images = TagImageTask().calculate_images(
                image='quay.io/riotkit/backuprepository:release-4.0.5-dev1',
                latest_per_version=True,
                global_latest=False,
                allowed_meta_list='rc,alpha,stable,dev,prod,test,beta,build,b',
                keep_prefix=False
            )

            self.assertEqual(
                ['quay.io/riotkit/backuprepository:4.0.5-dev1',
                 'quay.io/riotkit/backuprepository:4.0.5-latest-dev',
                 'quay.io/riotkit/backuprepository:4-latest-dev',
                 'quay.io/riotkit/backuprepository:4.0-latest-dev'],
                images
            )

    def test_strip_out_each_tag(self):
        """
        Assert that "release-" will be stripped out
        """

        out = TagImageTask.strip_out_each_tag(
            [
                'quay.io/riotkit/taiga:release-4.0.4',
                'quay.io/riotkit/taiga:release-4.0',
                'quay.io/riotkit/taiga:release-4'
            ],
            to_strip_at_beginning='release-',
            originally_tagged_image='quay.io/riotkit/taiga:release-4.0.4',
        )

        self.assertEqual(
            ['quay.io/riotkit/taiga:4.0.4', 'quay.io/riotkit/taiga:4.0', 'quay.io/riotkit/taiga:4'],
            out
        )
