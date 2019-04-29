import unittest
from typing import List

from janis.types import CpuSelector, MemorySelector

from janis import ToolOutput, ToolInput, String, CommandTool, Stdout, InputSelector, Array, File, Filename, \
    WildcardSelector
import janis.translations.cwl as cwl


class TestTool(CommandTool):

    @staticmethod
    def tool(): return "TestTranslation-tool"

    @staticmethod
    def base_command(): return "echo"

    def inputs(self) -> List[ToolInput]: return [ToolInput("testtool", String())]

    def outputs(self) -> List[ToolOutput]: return [ToolOutput("std", Stdout())]

    def friendly_name(self) -> str: return "Tool for testing translation"

    @staticmethod
    def docker(): return "ubuntu:latest"


class TestCwl(unittest.TestCase):

    def test_str_tool(self):
        t = TestTool()
        self.assertEqual(t.translate("cwl"), cwl_testtool)

    def test_input_selector_base(self):
        input_sel = InputSelector("random")
        self.assertEqual("$(inputs.random)", cwl.translate_input_selector(input_sel))

    def test_input_selector_prefix(self):
        input_sel = InputSelector("random", prefix="&& ")
        self.assertEqual("&& $(inputs.random)", cwl.translate_input_selector(input_sel))

    def test_base_input_selector(self):
        input_sel = InputSelector("random", suffix=".cwl")
        self.assertEqual("$(inputs.random).cwl", cwl.translate_input_selector(input_sel))

    def test_input_value_none_stringenv(self):
        self.assertEqual(None, cwl.get_input_value_from_potential_selector_or_generator(None, "tool_id", string_environment=True))

    def test_input_value_none_nostringenv(self):
        self.assertEqual(None, cwl.get_input_value_from_potential_selector_or_generator(None, "tool_id", string_environment=False))

    def test_input_value_string_stringenv(self):
        self.assertEqual(
            "TestString",
            cwl.get_input_value_from_potential_selector_or_generator("TestString", "tool_id", string_environment=True)
        )

    def test_input_value_string_nostringenv(self):
        self.assertEqual(
            '"TestString"',
            cwl.get_input_value_from_potential_selector_or_generator("TestString", "tool_id", string_environment=False)
        )

    def test_input_value_filename_stringenv(self):
        import uuid
        fn = Filename(guid=str(uuid.uuid4()))
        self.assertEqual(
            fn.generated_filename(),
            cwl.get_input_value_from_potential_selector_or_generator(fn, "tool_id", string_environment=True)
        )

    def test_input_value_filename_nostringenv(self):
        import uuid
        fn = Filename(guid=str(uuid.uuid4()))
        self.assertEqual(
            '"%s"' % fn.generated_filename(),
            cwl.get_input_value_from_potential_selector_or_generator(fn, "tool_id", string_environment=False)
        )

    def test_input_value_inpselect_stringenv(self):
        inp = InputSelector("threads")
        self.assertEqual(
            "$(inputs.threads)",
            cwl.get_input_value_from_potential_selector_or_generator(inp, "tool_id", string_environment=True)
        )

    def test_input_value_inpselect_nostringenv(self):
        inp = InputSelector("threads")
        self.assertEqual(
            "$(inputs.threads)",
            cwl.get_input_value_from_potential_selector_or_generator(inp, "tool_id", string_environment=False)
        )

    def test_input_value_wildcard(self):
        self.assertRaises(
            Exception,
            cwl.get_input_value_from_potential_selector_or_generator,
            value=WildcardSelector("*"),
            tool_id=None
        )

    def test_input_value_cpuselect_stringenv(self):
        inp = CpuSelector()
        self.assertEqual(
            "$(inputs.runtime_cpu)",
            cwl.get_input_value_from_potential_selector_or_generator(inp, "tool_id", string_environment=True)
        )

    def test_input_value_cpuselect_nostringenv(self):
        inp = CpuSelector()
        self.assertEqual(
            "$(inputs.runtime_cpu)",
            cwl.get_input_value_from_potential_selector_or_generator(inp, "tool_id", string_environment=False)
        )

    def test_input_value_memselect_stringenv(self):
        inp = MemorySelector()
        self.assertEqual(
            "$(Math.floor(inputs.runtime_memory))",
            cwl.get_input_value_from_potential_selector_or_generator(inp, "tool_id", string_environment=True)
        )

    def test_input_value_memselect_nostringenv(self):
        inp = MemorySelector()
        self.assertEqual(
            "$(Math.floor(inputs.runtime_memory))",
            cwl.get_input_value_from_potential_selector_or_generator(inp, "tool_id", string_environment=False)
        )

    def test_input_value_cwl_callable(self):
        class NonCallableCwl:
            def cwl(self):
                return "unbelievable"

        self.assertEqual(
            "unbelievable",
            cwl.get_input_value_from_potential_selector_or_generator(NonCallableCwl(), "tool_id")
        )

    def test_input_value_cwl_noncallable(self):

        class NonCallableCwl:
            def __init__(self):
                self.cwl = None

        self.assertRaises(
            Exception,
            cwl.get_input_value_from_potential_selector_or_generator,
            value=NonCallableCwl(),
            tool_id=None
        )


class TestCwlInputSelector(unittest.TestCase):

    def test_input_selector_1(self):
        self.assertTrue(True)






cwl_testtool = """\
baseCommand: echo
class: CommandLineTool
cwlVersion: v1.0
id: testtranslation-tool
inputs:
- id: testtool
  label: testtool
  type: string
label: testtranslation-tool
outputs:
- id: std
  label: std
  type: stdout
requirements:
  DockerRequirement:
    dockerPull: ubuntu:latest
  InlineJavascriptRequirement: {}
"""
