""" Unit tests for SceneRecognizer """

import nose.tools
import sys
sys.path.append('..')
import json
import os
import numpy
from dcase_framework.features import FeatureContainer, FeatureExtractor
from dcase_framework.metadata import MetaDataItem
from dcase_framework.learners import SceneClassifierGMM
from dcase_framework.recognizers import SceneRecognizer
import tempfile

def test_wrong_parameters():
    FeatureExtractor(store=True, overwrite=True).extract(
        audio_file=os.path.join('material', 'test.wav'),
        extractor_name='mfcc',
        extractor_params={
            'mfcc': {
                'n_mfcc': 10
            }
        },
        storage_paths={
            'mfcc': os.path.join('material', 'test.mfcc.cpickle')
        }
    )

    feature_container = FeatureContainer(filename=os.path.join('material', 'test.mfcc.cpickle'))

    data = {
        'file1.wav': feature_container,
        'file2.wav': feature_container,
    }

    annotations = {
        'file1.wav': MetaDataItem(
            {
                'file': 'file1.wav',
                'scene_label': 'scene1',
            }
        ),
        'file2.wav': MetaDataItem(
            {
                'file': 'file2.wav',
                'scene_label': 'scene2',
            }
        ),
    }

    sc = SceneClassifierGMM(
        method='gmm',
        class_labels=['scene1', 'scene2'],
        params={
            'n_components': 6,
            'covariance_type': 'diag',
            'tol': 0.001,
            'reg_covar': 0,
            'max_iter': 40,
            'n_init': 1,
            'init_params': 'kmeans',
            'random_state': 0,
        },
        filename=os.path.join('material', 'test.model.cpickle'),
        disable_progress_bar=True,
    )

    sc.learn(data=data, annotations=annotations)
    recognizer_params = {
        'frame_accumulation': {
            'enable': True,
            'type': 'sum',
        },
        'frame_binarization': {
            'enable': False,
        },
        'decision_making': {
            'enable': True,
            'type': 'maximum',
        }
    }
    # Frame probabilities
    frame_probabilities = sc.predict(feature_data=feature_container)

    recognizer_params = {
        'frame_accumulation': {
            'enable': True,
            'type': 'sum',
        },
        'frame_binarization': {
            'enable': False,
        },
        'decision_making': {
            'enable': True,
            'type': 'maximum',
        }
    }
    recognizer_params['frame_accumulation']['type'] = 'test'
    sr = SceneRecognizer(
        params=recognizer_params,
        class_labels=['scene1', 'scene2'],
    )

    # Test errors
    nose.tools.assert_raises(AssertionError, sr.process, frame_probabilities)

    recognizer_params['frame_accumulation']['type'] = 'sum'
    recognizer_params['decision_making']['type'] = 'test'
    sr = SceneRecognizer(
        params=recognizer_params,
        class_labels=['scene1', 'scene2'],
    )
    nose.tools.assert_raises(AssertionError, sr.process, frame_probabilities)
