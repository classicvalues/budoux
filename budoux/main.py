#!/usr/bin/env python
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""BudouX Script to provide CLI for user."""
import argparse
import json
import os
import shutil
import sys
import textwrap
import typing

import pkg_resources

import budoux

ArgList = typing.Optional[typing.List[str]]


class BudouxHelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawDescriptionHelpFormatter):
  pass


def check_file(path: str) -> str:
  """Check if filepath is exist or not.

  Args:
      path (str): Model path

  Raises:
      FileNotFoundError: Raise if given path is not exist.

  Returns:
      str: Model path confirmed its existance.
  """
  if os.path.isfile(path):
    return path
  else:
    raise FileNotFoundError("'{}' is not found.".format(path))


def parse_args(test: ArgList = None) -> argparse.Namespace:
  """Parse commandline arguments.

  Args:
      test (typing.Optional[typing.List[str]], optional): Commandline args for testing. Defaults to None.

  Returns:
      argparse.Namespace: Parsed data of args.
  """
  parser = argparse.ArgumentParser(
      prog="budoux",
      formatter_class=(lambda prog: BudouxHelpFormatter(
          prog,
          **{
              "width": shutil.get_terminal_size(fallback=(120, 50)).columns,
              "max_help_position": 30,
          },
      )),
      description=textwrap.dedent("""\
        BudouX is the successor to Budou,
        the machine learning powered line break organizer tool."""),
  )

  parser.add_argument("text", metavar="TXT", nargs="?", type=str, help="text")
  parser.add_argument(
      "-H",
      "--html",
      action="store_true",
      help="HTML mode",
  )
  parser.add_argument(
      "-m",
      "--model",
      metavar="JSON",
      type=check_file,
      default=pkg_resources.resource_filename(__name__, "models/ja-knbc.json"),
      help="custom model file path",
  )
  parser.add_argument(
      "-d",
      "--delim",
      metavar="STR",
      type=str,
      default="---",
      help="output delimiter in TEXT mode",
  )
  parser.add_argument(
      "-t",
      "--thres",
      type=int,
      default=budoux.DEFAULT_THRES,
      help="threshold value to separate chunks",
  )
  parser.add_argument(
      "-V",
      "--version",
      action="version",
      version="%(prog)s {}".format(budoux.__version__),
  )
  if test is not None:
    return parser.parse_args(test)
  else:
    return parser.parse_args()


def _main(test: ArgList = None) -> str:
  args = parse_args(test=test)
  with open(args.model, "r") as f:
    model = json.load(f)

  parser = budoux.Parser(model)
  if args.html:
    if args.text is None:
      inputs_html = sys.stdin.read()
    else:
      inputs_html = args.text
    res = parser.translate_html_string(inputs_html, thres=args.thres)
  else:
    if args.text is None:
      inputs = [v.rstrip() for v in sys.stdin.readlines()]
    else:
      inputs = [v.rstrip() for v in args.text.splitlines()]
    outputs = [parser.parse(sentence, thres=args.thres) for sentence in inputs]
    conbined_output = ["\n".join(output) for output in outputs]
    ors = "\n" + args.delim + "\n"
    res = ors.join(conbined_output)

  return res


def main(test: ArgList = None) -> None:
  try:
    print(_main(test))
  except KeyboardInterrupt:
    exit(0)


if __name__ == "__main__":
  main()
