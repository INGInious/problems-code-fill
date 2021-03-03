# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os
import re
import itertools

from flask import send_from_directory
from inginious.common.tasks_problems import CodeProblem
from inginious.frontend.pages.utils import INGIniousPage
from inginious.frontend.task_problems import DisplayableCodeProblem
from inginious.frontend.parsable_text import ParsableText


__version__ = "0.2"

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")


class StaticMockPage(INGIniousPage):
    def GET(self, path):
        return send_from_directory(os.path.join(PATH_TO_PLUGIN, "static"), path)

    def POST(self, path):
        return self.GET(path)

def normalize(s):
    return s.replace('\r\n', '\n').replace('\r', '\n')

class CodeFillProblem(CodeProblem):
    """
    Fill-in-the-blanks code problem
    """
    def __init__(self, problemid, content, translations, taskfs):
        CodeProblem.__init__(self, problemid, content, translations, taskfs)
        self._default = normalize(self._default)

    @classmethod
    def get_type(cls):
        return "code_fill"

    @classmethod
    def parse_problem(cls, problem_content):
        return problem_content

    @classmethod
    def problem_type(self):
        return dict

    def getFillRegex(self):
        regex = r'({})'.format(re.sub(r'\\{\\?%.+?\\?%\\}', r')\{%(.*?)%\}(', re.escape(self._default), flags=re.DOTALL))
        #print("default", self._default)
        #print("escaped default", re.escape(self._default))
        #print("regex", regex)
        return re.compile(regex, flags=re.DOTALL)

    def input_is_consistent(self, task_input, default_allowed_extension, default_max_size):
        if not str(self.get_id()) in task_input:
            return False
        return task_input[self.get_id()]["matches"]


class DisplayableCodeFillProblem(CodeFillProblem, DisplayableCodeProblem):

    """ A displayable fill-in-the-blanks code problem """
    def __init__(self, problemid, content, translations, taskfs):
        CodeFillProblem.__init__(self, problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(self, gettext):
        return "code-fill"

    def show_input(self, template_helper, language, seed):
        """ Show CodeFillProblem """
        header = ParsableText(self.gettext(language, self._header), "rst",
                              translation=self.get_translation_obj(language))
        return template_helper.render("tasks/code_fill.html",
                template_folder=PATH_TO_TEMPLATES, inputId=self.get_id(),
                header=header, lines=8, maxChars=0, language=self._language,
                optional=self._optional, template=self._default)

    def adapt_input_for_backend(self, input_data):
        """ Adapt the web input for the backend """
        if not str(self.get_id()) in input_data:
            return input_data

        text = normalize(input_data[self.get_id()])
        match = self.getFillRegex().fullmatch(text)
        #print("text", text)
        #print("match", match, match.groups())
        if not match:
            input_data[self.get_id()] = { "input": text,
                                          "template": self._default,
                                          "matches": False,
                                        }
        else:
            input_data[self.get_id()] = { "input": text,
                                          "template": self._default,
                                          "code": ''.join(match.groups()),
                                          "regions": match.groups()[1::2],
                                          "matches": True,
                                        }
        return input_data


def init(plugin_manager, course_factory, client, plugin_config):
    # TODO: Replace by shared static middleware and let webserver serve the files
    plugin_manager.add_page('/plugins/code-fill/static/<path:path>', StaticMockPage.as_view('codefillstaticpage'))
    plugin_manager.add_hook("css", lambda: "/plugins/code-fill/static/css/code-fill.css")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/code-fill/static/js/code-fill.js")
    course_factory.get_task_factory().add_problem_type(DisplayableCodeFillProblem)
