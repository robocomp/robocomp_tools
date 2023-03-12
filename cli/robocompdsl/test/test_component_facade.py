import json
import os
import unittest
from pathlib import Path
from pprint import pprint

from config_tests import CURRENT_DIR

from robocompdsl.dsl_parsers.specific_parsers.cdsl.componentfacade import ComponentFacade

RESOURCES_DIR = Path(CURRENT_DIR) / "resources"

class ComponentFacadeTestCase(unittest.TestCase):

    def test_init(self):
        component = ComponentFacade()
        component = ComponentFacade({"name": "the_name", "options": ["agmagent"], "statemachine_path": RESOURCES_DIR /'gamestatemachine.smdsl'})
        self.assertEqual(component.name, "the_name")
        self.assertEqual(component.statemachine['machine']['name'], 'application_machine')
        self.assertEqual(component.statemachine['machine']['contents']['finalstate'], 'app_end')
        self.assertDictEqual(component.statemachine['substates'][0], {'parallel': False, 'parent': 'game_machine', 'contents': dict(
            states=['session_init', 'game_start_wait', 'game_init', 'game_loop', 'game_pause', 'game_resume', 'game_reset', 'game_end', 'game_won', 'game_lost', 'session_end'], finalstate=None, initialstate='session_start_wait',
            transitions=[{'src': 'session_start_wait', 'dests': ['session_init']}, {'src': 'session_init', 'dests': ['game_start_wait']}, {'src': 'game_start_wait', 'dests': ['game_start_wait']}, {'src': 'game_start_wait', 'dests': ['game_init']},
                         {'src': 'game_start_wait', 'dests': ['session_end']}, {'src': 'session_end', 'dests': ['session_start_wait']}, {'src': 'game_init', 'dests': ['game_loop']}, {'src': 'game_loop', 'dests': ['game_loop', 'game_pause', 'game_won', 'game_lost', 'game_end']},
                         {'src': 'game_pause', 'dests': ['game_loop']}, {'src': 'game_pause', 'dests': ['game_reset']}, {'src': 'game_pause', 'dests': ['game_resume']}, {'src': 'game_pause', 'dests': ['game_end']}, {'src': 'game_resume', 'dests': ['game_loop']},
                         {'src': 'game_end', 'dests': ['game_lost']}, {'src': 'game_end', 'dests': ['game_won']}, {'src': 'game_lost', 'dests': ['game_start_wait']}, {'src': 'game_won', 'dests': ['game_start_wait']}, {'src': 'game_reset', 'dests': ['game_start_wait']}])})
        self.assertTrue(component.is_agm_agent())

if __name__ == '__main__':
    unittest.main()


# {
#   "machine": {
#     "name": "",
#     "default": false,
#     "contents": {
#       "states": null,
#       "finalstate": "app_end",
#       "initialstate": "game_machine",
#       "transitions": [
#         {
#           "src": "game_machine",
#           "dests": [
#             "app_end"
#           ]
#         }
#       ]
#     }
#   },
#   "substates": [
#     {
#       "parallel": false,
#       "parent": "game_machine",
#       "contents": {
#         "states": [
#           "session_init",
#           "game_start_wait",
#           "game_init",
#           "game_loop",
#           "game_pause",
#           "game_resume",
#           "game_reset",
#           "game_end",
#           "game_won",
#           "game_lost",
#           "session_end"
#         ],
#         "finalstate": null,
#         "initialstate": "session_start_wait",
#         "transitions": [
#           {
#             "src": "session_start_wait",
#             "dests": [
#               "session_init"
#             ]
#           },
#           {
#             "src": "session_init",
#             "dests": [
#               "game_start_wait"
#             ]
#           },
#           {
#             "src": "game_start_wait",
#             "dests": [
#               "game_start_wait"
#             ]
#           },
#           {
#             "src": "game_start_wait",
#             "dests": [
#               "game_init"
#             ]
#           },
#           {
#             "src": "game_start_wait",
#             "dests": [
#               "session_end"
#             ]
#           },
#           {
#             "src": "session_end",
#             "dests": [
#               "session_start_wait"
#             ]
#           },
#           {
#             "src": "game_init",
#             "dests": [
#               "game_loop"
#             ]
#           },
#           {
#             "src": "game_loop",
#             "dests": [
#               "game_loop",
#               "game_pause",
#               "game_won",
#               "game_lost",
#               "game_end"
#             ]
#           },
#           {
#             "src": "game_pause",
#             "dests": [
#               "game_loop"
#             ]
#           },
#           {
#             "src": "game_pause",
#             "dests": [
#               "game_reset"
#             ]
#           },
#           {
#             "src": "game_pause",
#             "dests": [
#               "game_resume"
#             ]
#           },
#           {
#             "src": "game_pause",
#             "dests": [
#               "game_end"
#             ]
#           },
#           {
#             "src": "game_resume",
#             "dests": [
#               "game_loop"
#             ]
#           },
#           {
#             "src": "game_end",
#             "dests": [
#               "game_lost"
#             ]
#           },
#           {
#             "src": "game_end",
#             "dests": [
#               "game_won"
#             ]
#           },
#           {
#             "src": "game_lost",
#             "dests": [
#               "game_start_wait"
#             ]
#           },
#           {
#             "src": "game_won",
#             "dests": [
#               "game_start_wait"
#             ]
#           },
#           {
#             "src": "game_reset",
#             "dests": [
#               "game_start_wait"
#             ]
#           }
#         ]
#       }
#     },
#     {
#       "parallel": false,
#       "parent": "session_init",
#       "contents": {
#         "states": [
#           "player_acquisition_loop"
#         ],
#         "finalstate": "player_acquisition_ended",
#         "initialstate": "player_acquisition_init",
#         "transitions": [
#           {
#             "src": "player_acquisition_init",
#             "dests": [
#               "player_acquisition_loop"
#             ]
#           },
#           {
#             "src": "player_acquisition_loop",
#             "dests": [
#               "player_acquisition_loop"
#             ]
#           },
#           {
#             "src": "player_acquisition_loop",
#             "dests": [
#               "player_acquisition_ended"
#             ]
#           }
#         ]
#       }
#     }
#   ],
#   "filename": "/home/robolab/robocomp/tools/cli/robocompdsl/test/resources/gamestatemachine.smdsl"
# }