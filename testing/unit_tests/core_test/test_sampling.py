import os
import numpy as np
import unittest


from input.coil_sampler import BatchSequenceSampler, SubsetSampler, RandomSampler
from input.coil_dataset import CoILDataset
from input import Augmenter
import input.splitter as splitter
from PIL import Image
# from utils.general import plot_test_image

from configs import set_type_of_process, merge_with_yaml

from torchvision import transforms
from utils.checkpoint_schedule import get_latest_evaluated_checkpoint, is_next_checkpoint_ready,\
    maximun_checkpoint_reach, get_next_checkpoint

from  coil_core.train import select_balancing_strategy
from configs import g_conf

def create_log_folder(exp_batch_name):
    """
        Only the train creates the path. The validation should wait for the training anyway,
        so there is no need to create any path for the logs. That avoids race conditions.
    Returns:

    """
    # This is hardcoded the logs always stay on the _logs folder
    root_path = '_logs'

    if not os.path.exists(root_path):
        os.mkdir(root_path)

    if not os.path.exists(os.path.join(root_path, exp_batch_name)):
        os.mkdir(os.path.join(root_path, exp_batch_name))


def create_exp_path(exp_batch_name, experiment_name):
    # This is hardcoded the logs always stay on the _logs folder
    root_path = '_logs'

    if not os.path.exists(os.path.join(root_path, exp_batch_name, experiment_name)):
        os.mkdir(os.path.join(root_path, exp_batch_name, experiment_name))


class testValidation(unittest.TestCase):
    # def __init__(self, *args, **kwargs):
    #    super(testSampler, self).__init__(*args, **kwargs)
    # self.root_test_dir = '/home/felipe/Datasets/CVPR02Noise/SeqTrain'

    # self.test_images_write_path = 'testing/unit_tests/_test_images_'


    def test_core_validation(self):

        dataset_name = 'CARLAValidationL1'

        exp_batch  = 'eccv_debug'
        exp_alias = 'experiment_1'
        full_dataset = os.path.join('/media/eder/Seagate Expansion Drive/', dataset_name)

        os.environ["CUDA_VISIBLE_DEVICES"] = "0"

        create_log_folder('eccv_debug')
        create_exp_path(exp_batch, exp_alias)


        # At this point the log file with the correct naming is created.
        merge_with_yaml(os.path.join('configs', exp_batch, exp_alias+'.yaml'))
        set_type_of_process('drive', dataset_name)

        augmenter = Augmenter(None)

        dataset = CoILDataset(full_dataset, transform=augmenter)

        # Creates the sampler, this part is responsible for managing the keys. It divides
        # all keys depending on the measurements and produces a set of keys for each bach.

        # The data loader is the multi threaded module from pytorch that release a number of
        # workers to get all the data.
        # TODO: batch size an number of workers go to some configuration file

        g_conf.SPLIT = [['lateral_noise', []], ['longitudinal_noise', []], ['weights', [0.0, 0.0, 1.0]]]
        data_loader = select_balancing_strategy(dataset, 0)

        for data in data_loader:
            for i in range(120):
                print (data[i]['steer'], data[i]['steer_noise'])
                self.assertEqual(data[i]['steer'], data[i]['steer_noise'])
                self.assertEqual(data[i]['throttle'], data[i]['throttle_noise'])
                self.assertEqual(data[i]['brake'], data[i]['brake_noise'])




